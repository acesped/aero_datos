#!/usr/bin/env python3
"""Convierte el script AERO_DATOS proporcionado a aerofactum.py.

Uso: python migrar_aerofactum.py aero_datos.py
No altera el original. Mantiene los IDs AD-001..AD-500 para preservar historial.
"""
from __future__ import annotations
import ast
import re
import sys
from pathlib import Path


def replace_once(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count != 1:
        raise ValueError(f"{label}: se esperaba 1 coincidencia, encontradas {count}. Verifica que el archivo sea el código original.")
    return src.replace(old, new, 1)


def migrate(original: Path, target: Path) -> None:
    src = original.read_text(encoding="utf-8")
    # Cambios de identidad; el catálogo y los ID se conservan deliberadamente.
    edits = [
        ("AERO_DATOS: 500 propuestas", "AEROFACTUM: 500 propuestas", "docstring"),
        ("BRAND = 'AERO_DATOS'", "BRAND = 'AEROFACTUM'", "marca"),
        ("'X-Title':'AERO_DATOS'", "'X-Title':'AEROFACTUM'", "título OpenRouter"),
        ("'aero datos - conocimiento en 20 segundos'", "'AEROFACTUM · CONOCIMIENTO AERONÁUTICO'", "pie de video"),
        ("#AeroDatos #Aviacion #ConocimientoAeronautico", "#Aerofactum #Aviacion #ConocimientoAeronautico", "hashtags"),
        ("AeroDatos: {path}", "Aerofactum: {path}", "mensajes GitHub"),
        ("'aerodatos_assets/media','aerodatos_video_assets/media','aerodatos_public_videos/media'", "'aerofactum_assets/media','aerofactum_video_assets/media','aerofactum_public_videos/media'", "carpetas multimedia"),
        ("'AeroDatosEducationalBot/1.3 (https://github.com/acesped/aero_datos; contact via GitHub issues)'", "'AerofactumEducationalBot/1.4 (https://github.com; contact via repository issues)'", "user agent"),
        ("description='AERO_DATOS: 500 ideas, video e Instagram con foto única por publicación'", "description='AEROFACTUM: 500 ideas, video e Instagram con foto única por publicación'", "ayuda CLI"),
        ("ap.add_argument('--out',default='output')", "ap.add_argument('--out',default='aerofactum_output')", "carpeta de salida"),
        ("'creative_variant':'aero_hook_technical_clean_zoom_unique_photo_v2'", "'creative_variant':'aerofactum_hook_technical_clean_zoom_unique_photo_v2'", "experimento"),
    ]
    for old, new, label in edits:
        src = replace_once(src, old, new, label)

    # La verificación siempre apunta a @aerofactum, incluso si queda una
    # variable IG_EXPECTED_USERNAME antigua en el workflow.
    src = replace_once(
        src,
        "expected=(expected if expected is not None else os.getenv('IG_EXPECTED_USERNAME','')).strip().lstrip('@').lower()\n    if not expected:raise RuntimeError('Falta IG_EXPECTED_USERNAME')",
        "expected=(expected if expected is not None else os.getenv('IG_EXPECTED_USERNAME','aerofactum')).strip().lstrip('@').lower()\n"
        "    if expected!='aerofactum':raise RuntimeError('IG_EXPECTED_USERNAME debe ser aerofactum; evita publicar en la cuenta anterior')",
        "identidad de Instagram",
    )

    # Se migra el historial remoto sin borrar el anterior. Los identificadores
    # AD- siguen idénticos, por lo que las publicaciones previas siguen bloqueadas.
    src = replace_once(
        src,
        "STATE_PATH='aerodatos/state.json'\ndef load_state(gh):\n"
        "    raw,sha=gh.read(STATE_PATH)\n"
        "    state=json.loads(raw) if raw is not None else {'schema':1,'episodes':{}}\n"
        "    if not isinstance(state,dict) or not isinstance(state.get('episodes'),dict):\n"
        "        raise RuntimeError('Estado remoto inválido: revisión manual necesaria')\n"
        "    return state,sha",
        "STATE_PATH='aerofactum/state.json'\n"
        "LEGACY_STATE_PATH='aerodatos/state.json'\n"
        "def load_state(gh):\n"
        "    raw,sha=gh.read(STATE_PATH)\n"
        "    if raw is None:\n"
        "        legacy,_=gh.read(LEGACY_STATE_PATH)\n"
        "        if legacy is not None:\n"
        "            print('Migrando historial aerodatos -> aerofactum; conservar IDs AD-',flush=True)\n"
        "            raw=legacy\n"
        "    state=json.loads(raw) if raw is not None else {'schema':1,'episodes':{}}\n"
        "    if not isinstance(state,dict) or not isinstance(state.get('episodes'),dict):\n"
        "        raise RuntimeError('Estado remoto inválido: revisión manual necesaria')\n"
        "    return state,sha",
        "migración del estado",
    )

    # Comprobaciones de que el rebranding no deje textos visibles anteriores.
    forbidden = ["BRAND = 'AERO_DATOS'", "#AeroDatos", "AeroDatos:",
                 "'X-Title':'AERO_DATOS'", "'aero datos - conocimiento"]
    leftovers = [s for s in forbidden if s in src]
    if leftovers:
        raise ValueError(f"Quedan cadenas antiguas sin transformar: {leftovers}")
    ast.parse(src, filename=str(target))
    target.write_text(src, encoding='utf-8')
    print(f"Creado: {target} ({len(src.splitlines())} líneas)")
    print('Catálogo AD-001..AD-500 conservado; historial antiguo migrado bajo demanda.')
    print('Actualiza IG_EXPECTED_USERNAME=aerofactum y credenciales de la cuenta Aerofactum.')


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit('Uso: python migrar_aerofactum.py aero_datos.py [aerofactum.py]')
    original=Path(sys.argv[1])
    target=Path(sys.argv[2]) if len(sys.argv)==3 else original.with_name('aerofactum.py')
    if original.resolve()==target.resolve():
        raise SystemExit('El archivo de salida debe ser diferente del original')
    migrate(original,target)

if __name__=='__main__':
    main()
