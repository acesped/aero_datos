#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AERO DATOS: valida y renueva el token de Instagram Login.

La cuenta se configura con IG_EXPECTED_USERNAME (p. ej. aerofactum).
La renovación solo modifica INSTAGRAM_TOKEN si se valida la identidad
antes y después de renovar. No recupera tokens revocados o expirados.

Dependencias: requests, PyNaCl.

Uso:
  python scripts/refresh_instagram_token.py
  python scripts/refresh_instagram_token.py --refresh

Variables:
  INSTAGRAM_TOKEN, INSTAGRAM_USER_ID, IG_EXPECTED_USERNAME
  Para --refresh: IG_SECRET_MANAGER_TOKEN, GITHUB_REPOSITORY
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import os
import re
import sys
import time
from urllib.parse import quote

import requests
from nacl import encoding, public

IG_ROOT = "https://graph.instagram.com"
GH_ROOT = "https://api.github.com"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AeroDatos-InstagramTokenWatch/2.1"})
TIMEOUT = 25
SECRET_NAME = "INSTAGRAM_TOKEN"
ALLOWED_REPO = "acesped/aero_datos"
TRANSIENT_HTTP = (429, 500, 502, 503, 504)


def log(message):
    print(message, flush=True)


def require(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta variable o secreto {name}")
    return value


def normalized_username(value):
    name = str(value or "").strip().lstrip("@").lower()
    if not re.fullmatch(r"[a-z0-9._]{1,30}", name):
        raise RuntimeError("IG_EXPECTED_USERNAME tiene un formato inválido")
    return name


def safe_get(url, *, params=None, headers=None, service="API", attempts=5):
    """Reintenta solo GET y evita imprimir URL/params (pueden llevar tokens)."""
    for attempt in range(attempts):
        try:
            response = SESSION.get(url, params=params, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f"{service}: error de red persistente ({type(exc).__name__})") from None
            time.sleep(min(2 ** (attempt + 1), 20))
            continue
        if response.status_code in TRANSIENT_HTTP and attempt < attempts - 1:
            log(f"{service}: HTTP {response.status_code}; reintento {attempt + 2}/{attempts}")
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = min(max(float(retry_after), 1), 30)
            except ValueError:
                delay = min(2 ** (attempt + 1), 20)
            time.sleep(delay)
            continue
        return response
    raise RuntimeError(f"{service}: no se pudo completar la lectura")


def ig_call(endpoint, token, **params):
    if endpoint not in ("me", "refresh_access_token"):
        raise RuntimeError("Endpoint de Instagram no permitido")
    resp = safe_get(
        f"{IG_ROOT}/{endpoint}",
        params={"access_token": token, **params},
        service="Instagram",
        attempts=1 if endpoint == "refresh_access_token" else 5,
    )
    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError(f"Instagram HTTP {resp.status_code}: respuesta no JSON") from None
    if not isinstance(data, dict):
        raise RuntimeError("Instagram: respuesta JSON inesperada")
    if not resp.ok or data.get("error"):
        err = data.get("error") if isinstance(data.get("error"), dict) else {}
        code = err.get("code", "?")
        subcode = err.get("error_subcode", "?")
        if resp.status_code in (400, 401, 403):
            raise RuntimeError(
                f"Instagram rechazó token o permisos (HTTP {resp.status_code}, "
                f"code={code}, subcode={subcode}). Si está revocado/caducado, "
                "requiere reconexión manual"
            )
        raise RuntimeError(f"Instagram no disponible (HTTP {resp.status_code}, code={code})")
    return data


def verify_identity(token, expected_username, expected_id):
    """Exige username y coincidencia con id o user_id devuelto por Instagram."""
    me = ig_call("me", token, fields="id,user_id,username")
    username = str(me.get("username") or "").strip().lstrip("@").lower()
    app_id = str(me.get("id") or "").strip()
    professional_id = str(me.get("user_id") or "").strip()
    expected_id = str(expected_id).strip()
    if username != expected_username:
        raise RuntimeError(
            "Instagram: nombre de usuario no coincide "
            f"(esperado=@{expected_username}; recibido=@{username or 'no disponible'}). "
            "No se modificó ningún secreto."
        )
    if expected_id not in (app_id, professional_id):
        raise RuntimeError(
            f"Instagram: @{expected_username} validado, pero INSTAGRAM_USER_ID "
            "no coincide con los identificadores devueltos por Meta "
            f"(id={'disponible' if app_id else 'ausente'}, "
            f"user_id={'disponible' if professional_id else 'ausente'}). "
            "No se modificó ningún secreto."
        )
    matched = "user_id" if expected_id == professional_id else "id"
    log("Instagram: identidad validada; INSTAGRAM_USER_ID coincide con " + matched)
    return username


def github_request(method, path, token, *, payload=None):
    method = method.upper()
    if method not in ("GET", "PUT"):
        raise RuntimeError("Método de GitHub no permitido")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = GH_ROOT + path
    if method == "GET":
        resp = safe_get(url, headers=headers, service="GitHub")
    else:
        # No repetir PUT automáticamente: un timeout podría ocurrir después
        # de haber almacenado el secreto. Requiere comprobación manual.
        try:
            resp = SESSION.put(url, headers=headers, json=payload, timeout=TIMEOUT)
        except requests.RequestException as exc:
            raise RuntimeError(
                "GitHub: resultado de escritura incierto "
                f"({type(exc).__name__}); revisar secreto antes de reintentar"
            ) from None
    if resp.status_code >= 400:
        raise RuntimeError(
            f"GitHub HTTP {resp.status_code} en {method} de Actions Secrets; "
            "comprobar permisos Secrets: read/write y estado de GitHub"
        )
    if not resp.content:
        return {}
    try:
        result = resp.json()
    except ValueError:
        raise RuntimeError("GitHub: respuesta JSON inválida") from None
    if not isinstance(result, dict):
        raise RuntimeError("GitHub: respuesta inesperada")
    return result


def secret_metadata(repo, admin_token):
    return github_request("GET", f"/repos/{repo}/actions/secrets/{SECRET_NAME}", admin_token)


def token_fingerprint(token):
    """Huella binaria local, nunca enviada a los registros."""
    return hashlib.sha256(token.encode("utf-8")).digest()


def assert_secret_not_changed(repo, admin_token, initial_updated_at):
    current = secret_metadata(repo, admin_token).get("updated_at")
    if not current or current != initial_updated_at:
        raise RuntimeError(
            "INSTAGRAM_TOKEN cambió o no pudo verificarse durante la ejecución; "
            "no se sobrescribirá."
        )


def save_secret(repo, admin_token, secret_name, value):
    repo_path = f"/repos/{repo}/actions/secrets"
    pubkey = github_request("GET", repo_path + "/public-key", admin_token)
    if not pubkey.get("key") or not pubkey.get("key_id"):
        raise RuntimeError("GitHub no proporcionó clave pública válida")
    sealed = public.SealedBox(public.PublicKey(pubkey["key"], encoding.Base64Encoder))
    encrypted = base64.b64encode(sealed.encrypt(value.encode("utf-8"))).decode("ascii")
    github_request(
        "PUT", f"{repo_path}/{quote(secret_name, safe='')}", admin_token,
        payload={"encrypted_value": encrypted, "key_id": pubkey["key_id"]},
    )


def summary(message):
    target = os.getenv("GITHUB_STEP_SUMMARY", "")
    if target:
        try:
            with open(target, "a", encoding="utf-8") as fh:
                fh.write(message + "\n")
        except OSError:
            log("Aviso: no se pudo escribir GITHUB_STEP_SUMMARY")


def main():
    parser = argparse.ArgumentParser(description="Validar y renovar token Instagram de AERO DATOS")
    parser.add_argument("--refresh", action="store_true", help="Renovar token válido de larga duración")
    args = parser.parse_args()

    expected_username = normalized_username(require("IG_EXPECTED_USERNAME"))
    expected_id = require("INSTAGRAM_USER_ID")
    token = require("INSTAGRAM_TOKEN")
    log("Instagram: comprobando credencial e identidad de @" + expected_username)
    try:
        verify_identity(token, expected_username, expected_id)
    except RuntimeError:
        summary("❌ Instagram: token o identidad inválidos; ningún secreto fue modificado.")
        raise
    log("Instagram: token vigente y cuenta correcta")

    if not args.refresh:
        summary(f"✅ Instagram: token vigente e identidad correcta de @{expected_username}.")
        return 0

    # Comprobar repositorio y acceso de escritura antes de renovar.
    repo = require("GITHUB_REPOSITORY")
    if repo.lower() != ALLOWED_REPO:
        raise RuntimeError(f"Repositorio inesperado ({repo}); no se actualizará ningún secreto")
    admin = require("IG_SECRET_MANAGER_TOKEN")
    initial_updated = secret_metadata(repo, admin).get("updated_at")
    if not initial_updated:
        raise RuntimeError("No se pudo comprobar la versión inicial de INSTAGRAM_TOKEN")
    key_check = github_request("GET", f"/repos/{repo}/actions/secrets/public-key", admin)
    if not key_check.get("key_id") or not key_check.get("key"):
        raise RuntimeError("No se puede obtener clave pública de GitHub Secrets")

    log("Instagram: intentando renovación preventiva del token vigente")
    try:
        obj = ig_call("refresh_access_token", token, grant_type="ig_refresh_token")
    except RuntimeError as exc:
        summary("⚠️ Token validado, pero Meta rechazó la renovación; secreto sin cambios.")
        raise RuntimeError(
            "Meta no permitió renovar el token vigente. "
            "Se conserva el secreto; revisar antigüedad, tipo de token y cuotas. " + str(exc)
        ) from exc

    updated = str(obj.get("access_token") or "").strip()
    if not updated:
        raise RuntimeError("Meta respondió sin access_token; ningún secreto fue modificado")
    expires_in = obj.get("expires_in")
    if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)) or expires_in <= 0:
        raise RuntimeError("Meta respondió sin expires_in válido; ningún secreto fue modificado")

    verify_identity(updated, expected_username, expected_id)
    assert_secret_not_changed(repo, admin, initial_updated)

    if hmac.compare_digest(token_fingerprint(updated), token_fingerprint(token)):
        log("Instagram: Meta devolvió el mismo valor de token; sigue vigente")

    save_secret(repo, admin, SECRET_NAME, updated)
    # Solo se puede verificar la fecha, no el valor del secreto.
    after = secret_metadata(repo, admin).get("updated_at")
    if not after or after == initial_updated:
        raise RuntimeError(
            "GitHub no confirmó una nueva fecha de actualización del secreto. "
            "Revisar manualmente antes de volver a ejecutar."
        )
    log("Instagram: renovación y actualización de GitHub Secrets confirmadas")
    summary(
        f"✅ @{expected_username}: token validado, renovado y secreto actualizado. "
        f"Vigencia informada por Meta: {int(expires_in // 86400)} días."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, requests.RequestException, KeyError, ValueError) as exc:
        # Nunca registrar URLs, headers ni respuestas completas que incluyan tokens.
        safe_message = type(exc).__name__ if isinstance(exc, requests.RequestException) else str(exc)
        log("ERROR: " + safe_message)
        summary("❌ AERO DATOS: monitor/renovación falló; revisar configuración y autorización.")
        sys.exit(1)
