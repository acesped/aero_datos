#!/usr/bin/env python3
"""Verifica la cuenta de Instagram y renueva su token cuando corresponda.

Actualiza exclusivamente INSTAGRAM_TOKEN como Repository Secret en GitHub.
No imprime tokens ni respuestas confidenciales de APIs.
No recupera tokens revocados o caducados por Meta.
"""

import base64
import os
import re
import sys
from datetime import datetime, timezone

import requests
from nacl import encoding, public

TIMEOUT = 25
GRAPH = "https://graph.instagram.com"
API_VERSION = "v25.0"
MIN_HOURS = 48
EXPECTED_REPOSITORY = "acesped/aero_datos"


def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta secreto o variable: {name}")
    return value


def call(method, url, **kwargs):
    """Realiza solicitudes sin exponer URLs, cuerpos ni credenciales en errores."""
    try:
        response = requests.request(
            method,
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Error de conexión: {type(exc).__name__}"
        ) from None

    if not 200 <= response.status_code < 300:
        if response.status_code in (400, 401, 403) and url.startswith(GRAPH + "/"):
            try:
                payload = response.json()
                error = payload.get("error", {}) if isinstance(payload, dict) else {}
                if isinstance(error, dict) and str(error.get("code")) == "190":
                    raise RuntimeError(
                        "Meta OAuth 190: token inválido, caducado o revocado; "
                        "puede requerir nueva autorización manual"
                    )
            except ValueError:
                pass
        raise RuntimeError(f"{method} rechazado: HTTP {response.status_code}")

    if response.status_code == 204 or not response.content:
        return {}
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Respuesta no JSON") from None
    if not isinstance(data, dict):
        raise RuntimeError("Respuesta de API inesperada")
    return data


def verify_identity(token, uid, username):
    """Verifica que el token pertenezca a la cuenta de Instagram esperada."""
    data = call(
        "GET",
        f"{GRAPH}/{API_VERSION}/me",
        headers={"Authorization": f"Bearer {token}"},
        params={"fields": "user_id,username"},
    )

    actual_uid = str(data.get("user_id", "")).strip()
    actual_username = str(data.get("username", "")).strip().lstrip("@").lower()
    expected_username = username.strip().lstrip("@").lower()

    if actual_uid != uid:
        raise RuntimeError(
            "INSTAGRAM_USER_ID no coincide con el user_id asociado al token; "
            "verifica el ID de Instagram Login en GitHub Secrets. "
            "No se modifica el secreto"
        )

    if actual_username != expected_username:
        raise RuntimeError(
            "IG_EXPECTED_USERNAME no coincide con la cuenta asociada al token; "
            f"se esperaba @{expected_username}. No se modifica el secreto"
        )


def main():
    if os.getenv("IG_LOGIN_TYPE", "instagram").lower() != "instagram":
        raise RuntimeError("Se requiere IG_LOGIN_TYPE=instagram")

    token = required("INSTAGRAM_TOKEN")
    uid = required("INSTAGRAM_USER_ID")
    username = required("IG_EXPECTED_USERNAME").lstrip("@").lower()
    gh_token = required("GH_SECRETS_TOKEN")
    repo = required("GITHUB_REPOSITORY")

    if not re.fullmatch(r"\d+", uid):
        raise RuntimeError("INSTAGRAM_USER_ID debe ser numérico")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise RuntimeError("Nombre de repositorio inválido")
    if repo.lower() != EXPECTED_REPOSITORY:
        raise RuntimeError("Repositorio inesperado: operación bloqueada")
    if not re.fullmatch(r"[a-z0-9._]+", username):
        raise RuntimeError("Nombre de usuario esperado inválido")

    verify_identity(token, uid, username)
    print(f"Identidad actual confirmada: @{username}")

    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    base = f"https://api.github.com/repos/{repo}/actions/secrets"

    metadata = call("GET", base + "/INSTAGRAM_TOKEN", headers=headers)
    updated_at = metadata.get("updated_at")
    if not isinstance(updated_at, str):
        raise RuntimeError("GitHub no devolvió updated_at para INSTAGRAM_TOKEN")
    try:
        updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if updated.tzinfo is None:
            raise ValueError("Fecha sin zona horaria")
    except ValueError:
        raise RuntimeError("GitHub devolvió una fecha updated_at inválida") from None

    age_hours = (datetime.now(timezone.utc) - updated).total_seconds() / 3600
    if age_hours < 0:
        raise RuntimeError("La fecha del secreto está en el futuro; revisar el reloj")
    if age_hours < MIN_HOURS:
        print(
            f"OMITIDA: secreto actualizado hace {age_hours:.1f} h; "
            f"mínimo {MIN_HOURS} h."
        )
        return

    renewed = call(
        "GET",
        GRAPH + "/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
    )
    new_token = renewed.get("access_token")
    expires = renewed.get("expires_in")

    if not isinstance(new_token, str) or len(new_token) < 30:
        raise RuntimeError("Meta no devolvió un token válido")
    if isinstance(expires, bool) or not isinstance(expires, (int, float)) or not 0 < expires < float("inf"):
        raise RuntimeError("Meta no devolvió una vigencia válida")

    # Enmascarar inmediatamente el token nuevo, incluso si coincide con el anterior.
    print("::add-mask::" + new_token, flush=True)
    verify_identity(new_token, uid, username)

    key_info = call("GET", base + "/public-key", headers=headers)
    key_b64 = key_info.get("key")
    key_id = key_info.get("key_id")
    if not isinstance(key_b64, str) or not isinstance(key_id, str):
        raise RuntimeError("GitHub no devolvió una clave pública válida")
    try:
        public_key = public.PublicKey(
            key_b64.encode("ascii"), encoding.Base64Encoder()
        )
        encrypted_value = base64.b64encode(
            public.SealedBox(public_key).encrypt(new_token.encode("utf-8"))
        ).decode("ascii")
    except (ValueError, TypeError):
        raise RuntimeError("No se pudo preparar el cifrado del secreto") from None

    call(
        "PUT",
        base + "/INSTAGRAM_TOKEN",
        headers=headers,
        json={"encrypted_value": encrypted_value, "key_id": key_id},
    )
    print(
        f"Renovación exitosa para @{username}. "
        "INSTAGRAM_TOKEN actualizado. "
        f"Vigencia reportada: {int(expires // 86400)} días."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Solo nuestras excepciones controladas pueden escribirse en el log.
        if isinstance(exc, RuntimeError):
            print(f"ERROR en renovación Instagram: {exc}", file=sys.stderr)
        else:
            print(
                f"ERROR interno en renovación Instagram: {type(exc).__name__}",
                file=sys.stderr,
            )
        sys.exit(1)
