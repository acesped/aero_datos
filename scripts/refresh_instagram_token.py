#!/usr/bin/env python3
"""AERO DATOS: valida token Instagram y renueva tokens long-lived válidos.

Requiere: requests, PyNaCl. No puede recuperar un token revocado/expirado.
Actualizar INSTAGRAM_TOKEN solo después de comprobar la nueva credencial.
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
from datetime import datetime, timezone

import requests
from nacl import public, encoding

IG_ROOT = "https://graph.instagram.com"
GH_ROOT = "https://api.github.com"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AeroDatos-InstagramTokenWatch/2.0"})
TIMEOUT = 25


def log(message):
    print(message, flush=True)


def require(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta variable o secreto {name}")
    return value


def ig_call(endpoint, token, **params):
    resp = SESSION.get(f"{IG_ROOT}/{endpoint}",
                       params={"access_token": token, **params}, timeout=TIMEOUT)
    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError(f"Instagram HTTP {resp.status_code}: respuesta no JSON")
    if not resp.ok or data.get("error"):
        err = data.get("error") or {}
        code = err.get("code", "?")
        subcode = err.get("error_subcode", "?")
        # No imprimir JSON completo: algunas respuestas pueden incluir datos sensibles.
        if resp.status_code in (400, 401, 403):
            raise RuntimeError(f"Instagram rechazó token o permisos (HTTP {resp.status_code}, code={code}, subcode={subcode}). "
                               "Si está revocado/caducado, requiere reconexión manual")
        raise RuntimeError(f"Instagram no disponible (HTTP {resp.status_code}, code={code})")
    return data


def verify_identity(token, expected_username, expected_id):
    """Verifica nombre Y uno de los IDs de Instagram Login, sin cambiar secretos.

    El campo ``id`` puede ser el identificador con alcance de aplicación,
    mientras ``user_id`` puede ser el ID profesional usado en publicación.
    Nunca basta con que coincida solamente un ID: el username es obligatorio.
    """
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
            "Instagram: @" + expected_username + " validado, pero INSTAGRAM_USER_ID "
            "no coincide con los identificadores devueltos por Meta "
            f"(id={'disponible' if app_id else 'ausente'}, "
            f"user_id={'disponible' if professional_id else 'ausente'}). "
            "Revisar el ID profesional guardado en GitHub. "
            "No se modificó ningún secreto."
        )
    matched = "user_id" if expected_id == professional_id else "id"
    log("Instagram: identidad validada, INSTAGRAM_USER_ID coincide con " + matched)
    return username


def github_request(method, path, token, *, payload=None):
    resp = SESSION.request(method, f"{GH_ROOT}{path}",
                           headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/vnd.github+json",
                                    "X-GitHub-Api-Version": "2022-11-28"},
                           json=payload, timeout=TIMEOUT)
    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub HTTP {resp.status_code} al actualizar secreto; "
                           "comprueba permisos Secrets: read/write del token administrador")
    return resp.json() if resp.content else {}


def save_secret(repo, admin_token, secret_name, value):
    repo_path = f"/repos/{repo}/actions/secrets"
    pubkey = github_request("GET", repo_path + "/public-key", admin_token)
    sealed = public.SealedBox(public.PublicKey(pubkey["key"], encoding.Base64Encoder))
    ciphertext = sealed.encrypt(value.encode("utf-8"))
    encrypted = base64.b64encode(ciphertext).decode("ascii")
    github_request("PUT", f"{repo_path}/{secret_name}", admin_token,
                   payload={"encrypted_value": encrypted, "key_id": pubkey["key_id"]})


def summary(message):
    target = os.getenv("GITHUB_STEP_SUMMARY", "")
    if target:
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(message + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true",
                        help="Intentar renovación preventiva del token vigente")
    args = parser.parse_args()

    token = require("INSTAGRAM_TOKEN")
    expected_username = require("IG_EXPECTED_USERNAME").lstrip("@").lower()
    if expected_username != "aero_datos":
        raise RuntimeError("Este monitor solo puede actualizar el token de @aero_datos")
    expected_id = require("INSTAGRAM_USER_ID")
    log("Instagram: comprobando credencial e identidad de @" + expected_username)
    verify_identity(token, expected_username, expected_id)
    log("Instagram: token vigente, cuenta correcta")
    if not args.refresh:
        summary("✅ Instagram @" + expected_username + ": token vigente e identidad validada.")
        return 0

    log("Instagram: intentando renovar token de larga duración (solo Instagram Login)")
    try:
        obj = ig_call("refresh_access_token", token, grant_type="ig_refresh_token")
    except RuntimeError as exc:
        # El token recién renovado puede no reunir todavía las 24 horas
        # mínimas; no convertir esa condición específica en una alarma falsa.
        detail = str(exc)
        if "code=190" not in detail and "code=?" not in detail and (
            "24 hour" in detail.lower() or "24 horas" in detail.lower()
        ):
            log("Instagram: renovación aún no habilitada (edad mínima de 24 horas).")
            summary("ℹ️ Token válido; renovación aplazada por edad mínima de Meta.")
            return 0
        summary("⚠️ Renovación no completada; el secreto actual no se modificó.")
        raise RuntimeError("No se pudo renovar. Token almacenado sin cambios. "
                           "Si está revocado o caducado, necesita reautorización. " + detail) from exc
    updated = str(obj.get("access_token", "")).strip()
    if not updated:
        raise RuntimeError("Renovación sin access_token; secreto antiguo conservado")
    verify_identity(updated, expected_username, expected_id)
    expires_in = obj.get("expires_in")
    if not isinstance(expires_in, (int, float)) or expires_in <= 0:
        raise RuntimeError("Renovación sin expires_in válido; secreto antiguo conservado")

    admin = require("IG_SECRET_MANAGER_TOKEN")
    repo = require("GITHUB_REPOSITORY")
    save_secret(repo, admin, "INSTAGRAM_TOKEN", updated)
    log("Instagram: token renovado, identidad verificada y secreto INSTAGRAM_TOKEN actualizado")
    summary("✅ Instagram @" + expected_username + ": token renovado y guardado en GitHub Secrets. "
            "Validez informada: " + str(int(expires_in // 86400)) + " días.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, requests.RequestException, KeyError, ValueError) as exc:
        # No registrar una URL completa de requests: podría contener access_token.
        safe_message = type(exc).__name__ if isinstance(exc, requests.RequestException) else str(exc)
        log("ERROR: " + safe_message)
        summary("❌ AERO DATOS: monitor/renovación de token falló. "
                "Revisa la ejecución y, si está revocado, vuelve a autorizar la cuenta manualmente.")
        sys.exit(1)
 
