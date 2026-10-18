#!/usr/bin/env python3
"""AeroDatos: catálogo integrado (500 propuestas), previews y publicación de VIDEO en Reels, feed y Stories de IG.

Las referencias son opcionales; la ausencia de fuentes no impide publicar.
Los datos generados por IA no están verificados independientemente.
Para contenido sensible, mantener revisión humana antes de publicar.
Python 3.11+. Dependencias en requirements.txt; ffmpeg instalado por workflow.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import wave
import zlib
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

AERO_CATALOG = [{'id': 'AD-001', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona Rolls-Royce Trent 1000?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Rolls-Royce Trent 1000; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Rolls-Royce Trent 1000'}, {'id': 'AD-002', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de Rolls-Royce Trent 1000?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Rolls-Royce Trent 1000; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Rolls-Royce Trent 1000'}, {'id': 'AD-003', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene Rolls-Royce Trent 1000?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Rolls-Royce Trent 1000; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Rolls-Royce Trent 1000'}, {'id': 'AD-004', 'category': 'Motores y propulsión', 'title': '¿Por qué importa Rolls-Royce Trent 1000 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Rolls-Royce Trent 1000; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Rolls-Royce Trent 1000'}, {'id': 'AD-005', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre Rolls-Royce Trent 1000?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Rolls-Royce Trent 1000; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Rolls-Royce Trent 1000'}, {'id': 'AD-006', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona General Electric GEnx?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre General Electric GEnx; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'General Electric GEnx'}, {'id': 'AD-007', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de General Electric GEnx?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre General Electric GEnx; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'General Electric GEnx'}, {'id': 'AD-008', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene General Electric GEnx?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre General Electric GEnx; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'General Electric GEnx'}, {'id': 'AD-009', 'category': 'Motores y propulsión', 'title': '¿Por qué importa General Electric GEnx en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre General Electric GEnx; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'General Electric GEnx'}, {'id': 'AD-010', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre General Electric GEnx?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre General Electric GEnx; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'General Electric GEnx'}, {'id': 'AD-011', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona CFM56-5B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CFM56-5B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CFM56-5B'}, {'id': 'AD-012', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de CFM56-5B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CFM56-5B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CFM56-5B'}, {'id': 'AD-013', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene CFM56-5B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CFM56-5B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CFM56-5B'}, {'id': 'AD-014', 'category': 'Motores y propulsión', 'title': '¿Por qué importa CFM56-5B en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CFM56-5B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CFM56-5B'}, {'id': 'AD-015', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre CFM56-5B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CFM56-5B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CFM56-5B'}, {'id': 'AD-016', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona LEAP-1A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre LEAP-1A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'LEAP-1A'}, {'id': 'AD-017', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de LEAP-1A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre LEAP-1A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'LEAP-1A'}, {'id': 'AD-018', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene LEAP-1A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre LEAP-1A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'LEAP-1A'}, {'id': 'AD-019', 'category': 'Motores y propulsión', 'title': '¿Por qué importa LEAP-1A en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre LEAP-1A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'LEAP-1A'}, {'id': 'AD-020', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre LEAP-1A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre LEAP-1A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'LEAP-1A'}, {'id': 'AD-021', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona Pratt & Whitney PW1100G?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Pratt & Whitney PW1100G; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Pratt & Whitney PW1100G'}, {'id': 'AD-022', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de Pratt & Whitney PW1100G?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Pratt & Whitney PW1100G; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Pratt & Whitney PW1100G'}, {'id': 'AD-023', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene Pratt & Whitney PW1100G?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Pratt & Whitney PW1100G; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Pratt & Whitney PW1100G'}, {'id': 'AD-024', 'category': 'Motores y propulsión', 'title': '¿Por qué importa Pratt & Whitney PW1100G en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Pratt & Whitney PW1100G; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Pratt & Whitney PW1100G'}, {'id': 'AD-025', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre Pratt & Whitney PW1100G?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Pratt & Whitney PW1100G; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Pratt & Whitney PW1100G'}, {'id': 'AD-026', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona GE90?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GE90; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GE90'}, {'id': 'AD-027', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de GE90?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GE90; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GE90'}, {'id': 'AD-028', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene GE90?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GE90; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GE90'}, {'id': 'AD-029', 'category': 'Motores y propulsión', 'title': '¿Por qué importa GE90 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GE90; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GE90'}, {'id': 'AD-030', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre GE90?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GE90; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GE90'}, {'id': 'AD-031', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona Trent XWB?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Trent XWB; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Trent XWB'}, {'id': 'AD-032', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de Trent XWB?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Trent XWB; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Trent XWB'}, {'id': 'AD-033', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene Trent XWB?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Trent XWB; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Trent XWB'}, {'id': 'AD-034', 'category': 'Motores y propulsión', 'title': '¿Por qué importa Trent XWB en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Trent XWB; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Trent XWB'}, {'id': 'AD-035', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre Trent XWB?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Trent XWB; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Trent XWB'}, {'id': 'AD-036', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona CF34?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CF34; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CF34'}, {'id': 'AD-037', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de CF34?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CF34; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CF34'}, {'id': 'AD-038', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene CF34?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CF34; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CF34'}, {'id': 'AD-039', 'category': 'Motores y propulsión', 'title': '¿Por qué importa CF34 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CF34; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CF34'}, {'id': 'AD-040', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre CF34?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CF34; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CF34'}, {'id': 'AD-041', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona PT6A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre PT6A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'PT6A'}, {'id': 'AD-042', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de PT6A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre PT6A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'PT6A'}, {'id': 'AD-043', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene PT6A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre PT6A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'PT6A'}, {'id': 'AD-044', 'category': 'Motores y propulsión', 'title': '¿Por qué importa PT6A en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre PT6A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'PT6A'}, {'id': 'AD-045', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre PT6A?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre PT6A; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'PT6A'}, {'id': 'AD-046', 'category': 'Motores y propulsión', 'title': '¿Cómo funciona APU de un avión comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre APU de un avión comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'APU de un avión comercial'}, {'id': 'AD-047', 'category': 'Motores y propulsión', 'title': '¿Qué determina el rendimiento de APU de un avión comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre APU de un avión comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'APU de un avión comercial'}, {'id': 'AD-048', 'category': 'Motores y propulsión', 'title': '¿Qué limitaciones tiene APU de un avión comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre APU de un avión comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'APU de un avión comercial'}, {'id': 'AD-049', 'category': 'Motores y propulsión', 'title': '¿Por qué importa APU de un avión comercial en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre APU de un avión comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'APU de un avión comercial'}, {'id': 'AD-050', 'category': 'Motores y propulsión', 'title': '¿Qué errores comunes existen sobre APU de un avión comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre APU de un avión comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'APU de un avión comercial'}, {'id': 'AD-051', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona sustentación de un ala?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sustentación de un ala; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sustentación de un ala'}, {'id': 'AD-052', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de sustentación de un ala?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sustentación de un ala; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sustentación de un ala'}, {'id': 'AD-053', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene sustentación de un ala?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sustentación de un ala; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sustentación de un ala'}, {'id': 'AD-054', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa sustentación de un ala en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sustentación de un ala; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sustentación de un ala'}, {'id': 'AD-055', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre sustentación de un ala?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sustentación de un ala; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sustentación de un ala'}, {'id': 'AD-056', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona resistencia inducida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre resistencia inducida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'resistencia inducida'}, {'id': 'AD-057', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de resistencia inducida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre resistencia inducida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'resistencia inducida'}, {'id': 'AD-058', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene resistencia inducida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre resistencia inducida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'resistencia inducida'}, {'id': 'AD-059', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa resistencia inducida en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre resistencia inducida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'resistencia inducida'}, {'id': 'AD-060', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre resistencia inducida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre resistencia inducida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'resistencia inducida'}, {'id': 'AD-061', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona winglets?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre winglets; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'winglets'}, {'id': 'AD-062', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de winglets?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre winglets; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'winglets'}, {'id': 'AD-063', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene winglets?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre winglets; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'winglets'}, {'id': 'AD-064', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa winglets en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre winglets; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'winglets'}, {'id': 'AD-065', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre winglets?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre winglets; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'winglets'}, {'id': 'AD-066', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona flaps y slats?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre flaps y slats; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'flaps y slats'}, {'id': 'AD-067', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de flaps y slats?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre flaps y slats; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'flaps y slats'}, {'id': 'AD-068', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene flaps y slats?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre flaps y slats; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'flaps y slats'}, {'id': 'AD-069', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa flaps y slats en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre flaps y slats; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'flaps y slats'}, {'id': 'AD-070', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre flaps y slats?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre flaps y slats; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'flaps y slats'}, {'id': 'AD-071', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona velocidad de pérdida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre velocidad de pérdida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'velocidad de pérdida'}, {'id': 'AD-072', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de velocidad de pérdida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre velocidad de pérdida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'velocidad de pérdida'}, {'id': 'AD-073', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene velocidad de pérdida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre velocidad de pérdida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'velocidad de pérdida'}, {'id': 'AD-074', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa velocidad de pérdida en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre velocidad de pérdida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'velocidad de pérdida'}, {'id': 'AD-075', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre velocidad de pérdida?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre velocidad de pérdida; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'velocidad de pérdida'}, {'id': 'AD-076', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona onda de choque transónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de choque transónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de choque transónica'}, {'id': 'AD-077', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de onda de choque transónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de choque transónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de choque transónica'}, {'id': 'AD-078', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene onda de choque transónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de choque transónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de choque transónica'}, {'id': 'AD-079', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa onda de choque transónica en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de choque transónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de choque transónica'}, {'id': 'AD-080', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre onda de choque transónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de choque transónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de choque transónica'}, {'id': 'AD-081', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona efecto suelo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre efecto suelo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'efecto suelo'}, {'id': 'AD-082', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de efecto suelo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre efecto suelo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'efecto suelo'}, {'id': 'AD-083', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene efecto suelo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre efecto suelo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'efecto suelo'}, {'id': 'AD-084', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa efecto suelo en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre efecto suelo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'efecto suelo'}, {'id': 'AD-085', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre efecto suelo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre efecto suelo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'efecto suelo'}, {'id': 'AD-086', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona centro de gravedad?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre centro de gravedad; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'centro de gravedad'}, {'id': 'AD-087', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de centro de gravedad?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre centro de gravedad; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'centro de gravedad'}, {'id': 'AD-088', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene centro de gravedad?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre centro de gravedad; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'centro de gravedad'}, {'id': 'AD-089', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa centro de gravedad en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre centro de gravedad; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'centro de gravedad'}, {'id': 'AD-090', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre centro de gravedad?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre centro de gravedad; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'centro de gravedad'}, {'id': 'AD-091', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona ángulo de ataque?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ángulo de ataque; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ángulo de ataque'}, {'id': 'AD-092', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de ángulo de ataque?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ángulo de ataque; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ángulo de ataque'}, {'id': 'AD-093', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene ángulo de ataque?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ángulo de ataque; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ángulo de ataque'}, {'id': 'AD-094', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa ángulo de ataque en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ángulo de ataque; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ángulo de ataque'}, {'id': 'AD-095', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre ángulo de ataque?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ángulo de ataque; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ángulo de ataque'}, {'id': 'AD-096', 'category': 'Aerodinámica y vuelo', 'title': '¿Cómo funciona formación de estelas turbulentas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre formación de estelas turbulentas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'formación de estelas turbulentas'}, {'id': 'AD-097', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué determina el rendimiento de formación de estelas turbulentas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre formación de estelas turbulentas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'formación de estelas turbulentas'}, {'id': 'AD-098', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué limitaciones tiene formación de estelas turbulentas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre formación de estelas turbulentas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'formación de estelas turbulentas'}, {'id': 'AD-099', 'category': 'Aerodinámica y vuelo', 'title': '¿Por qué importa formación de estelas turbulentas en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre formación de estelas turbulentas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'formación de estelas turbulentas'}, {'id': 'AD-100', 'category': 'Aerodinámica y vuelo', 'title': '¿Qué errores comunes existen sobre formación de estelas turbulentas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre formación de estelas turbulentas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'formación de estelas turbulentas'}, {'id': 'AD-101', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona sistema hidráulico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema hidráulico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema hidráulico'}, {'id': 'AD-102', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de sistema hidráulico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema hidráulico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema hidráulico'}, {'id': 'AD-103', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene sistema hidráulico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema hidráulico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema hidráulico'}, {'id': 'AD-104', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa sistema hidráulico en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema hidráulico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema hidráulico'}, {'id': 'AD-105', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre sistema hidráulico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema hidráulico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema hidráulico'}, {'id': 'AD-106', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona sistema fly-by-wire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema fly-by-wire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema fly-by-wire'}, {'id': 'AD-107', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de sistema fly-by-wire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema fly-by-wire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema fly-by-wire'}, {'id': 'AD-108', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene sistema fly-by-wire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema fly-by-wire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema fly-by-wire'}, {'id': 'AD-109', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa sistema fly-by-wire en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema fly-by-wire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema fly-by-wire'}, {'id': 'AD-110', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre sistema fly-by-wire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema fly-by-wire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema fly-by-wire'}, {'id': 'AD-111', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona tren de aterrizaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tren de aterrizaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tren de aterrizaje'}, {'id': 'AD-112', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de tren de aterrizaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tren de aterrizaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tren de aterrizaje'}, {'id': 'AD-113', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene tren de aterrizaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tren de aterrizaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tren de aterrizaje'}, {'id': 'AD-114', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa tren de aterrizaje en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tren de aterrizaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tren de aterrizaje'}, {'id': 'AD-115', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre tren de aterrizaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tren de aterrizaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tren de aterrizaje'}, {'id': 'AD-116', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona frenos de carbono?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre frenos de carbono; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'frenos de carbono'}, {'id': 'AD-117', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de frenos de carbono?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre frenos de carbono; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'frenos de carbono'}, {'id': 'AD-118', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene frenos de carbono?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre frenos de carbono; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'frenos de carbono'}, {'id': 'AD-119', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa frenos de carbono en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre frenos de carbono; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'frenos de carbono'}, {'id': 'AD-120', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre frenos de carbono?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre frenos de carbono; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'frenos de carbono'}, {'id': 'AD-121', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona protección contra hielo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre protección contra hielo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'protección contra hielo'}, {'id': 'AD-122', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de protección contra hielo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre protección contra hielo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'protección contra hielo'}, {'id': 'AD-123', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene protección contra hielo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre protección contra hielo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'protección contra hielo'}, {'id': 'AD-124', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa protección contra hielo en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre protección contra hielo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'protección contra hielo'}, {'id': 'AD-125', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre protección contra hielo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre protección contra hielo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'protección contra hielo'}, {'id': 'AD-126', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona sistema neumático?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema neumático; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema neumático'}, {'id': 'AD-127', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de sistema neumático?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema neumático; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema neumático'}, {'id': 'AD-128', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene sistema neumático?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema neumático; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema neumático'}, {'id': 'AD-129', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa sistema neumático en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema neumático; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema neumático'}, {'id': 'AD-130', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre sistema neumático?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre sistema neumático; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'sistema neumático'}, {'id': 'AD-131', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona presurización de cabina?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre presurización de cabina; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'presurización de cabina'}, {'id': 'AD-132', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de presurización de cabina?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre presurización de cabina; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'presurización de cabina'}, {'id': 'AD-133', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene presurización de cabina?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre presurización de cabina; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'presurización de cabina'}, {'id': 'AD-134', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa presurización de cabina en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre presurización de cabina; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'presurización de cabina'}, {'id': 'AD-135', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre presurización de cabina?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre presurización de cabina; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'presurización de cabina'}, {'id': 'AD-136', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona generadores eléctricos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre generadores eléctricos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'generadores eléctricos'}, {'id': 'AD-137', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de generadores eléctricos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre generadores eléctricos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'generadores eléctricos'}, {'id': 'AD-138', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene generadores eléctricos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre generadores eléctricos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'generadores eléctricos'}, {'id': 'AD-139', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa generadores eléctricos en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre generadores eléctricos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'generadores eléctricos'}, {'id': 'AD-140', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre generadores eléctricos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre generadores eléctricos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'generadores eléctricos'}, {'id': 'AD-141', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona inspección de álabes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre inspección de álabes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'inspección de álabes'}, {'id': 'AD-142', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de inspección de álabes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre inspección de álabes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'inspección de álabes'}, {'id': 'AD-143', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene inspección de álabes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre inspección de álabes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'inspección de álabes'}, {'id': 'AD-144', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa inspección de álabes en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre inspección de álabes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'inspección de álabes'}, {'id': 'AD-145', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre inspección de álabes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre inspección de álabes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'inspección de álabes'}, {'id': 'AD-146', 'category': 'Mantenimiento y sistemas', 'title': '¿Cómo funciona fatiga estructural?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre fatiga estructural; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'fatiga estructural'}, {'id': 'AD-147', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué determina el rendimiento de fatiga estructural?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre fatiga estructural; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'fatiga estructural'}, {'id': 'AD-148', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué limitaciones tiene fatiga estructural?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre fatiga estructural; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'fatiga estructural'}, {'id': 'AD-149', 'category': 'Mantenimiento y sistemas', 'title': '¿Por qué importa fatiga estructural en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre fatiga estructural; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'fatiga estructural'}, {'id': 'AD-150', 'category': 'Mantenimiento y sistemas', 'title': '¿Qué errores comunes existen sobre fatiga estructural?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre fatiga estructural; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'fatiga estructural'}, {'id': 'AD-151', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona despegue con viento cruzado?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre despegue con viento cruzado; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'despegue con viento cruzado'}, {'id': 'AD-152', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de despegue con viento cruzado?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre despegue con viento cruzado; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'despegue con viento cruzado'}, {'id': 'AD-153', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene despegue con viento cruzado?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre despegue con viento cruzado; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'despegue con viento cruzado'}, {'id': 'AD-154', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa despegue con viento cruzado en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre despegue con viento cruzado; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'despegue con viento cruzado'}, {'id': 'AD-155', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre despegue con viento cruzado?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre despegue con viento cruzado; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'despegue con viento cruzado'}, {'id': 'AD-156', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona cálculo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cálculo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cálculo de combustible'}, {'id': 'AD-157', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de cálculo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cálculo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cálculo de combustible'}, {'id': 'AD-158', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene cálculo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cálculo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cálculo de combustible'}, {'id': 'AD-159', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa cálculo de combustible en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cálculo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cálculo de combustible'}, {'id': 'AD-160', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre cálculo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cálculo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cálculo de combustible'}, {'id': 'AD-161', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona aproximación estabilizada?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación estabilizada; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación estabilizada'}, {'id': 'AD-162', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de aproximación estabilizada?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación estabilizada; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación estabilizada'}, {'id': 'AD-163', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene aproximación estabilizada?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación estabilizada; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación estabilizada'}, {'id': 'AD-164', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa aproximación estabilizada en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación estabilizada; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación estabilizada'}, {'id': 'AD-165', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre aproximación estabilizada?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación estabilizada; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación estabilizada'}, {'id': 'AD-166', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona desvío al alternativo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre desvío al alternativo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'desvío al alternativo'}, {'id': 'AD-167', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de desvío al alternativo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre desvío al alternativo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'desvío al alternativo'}, {'id': 'AD-168', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene desvío al alternativo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre desvío al alternativo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'desvío al alternativo'}, {'id': 'AD-169', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa desvío al alternativo en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre desvío al alternativo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'desvío al alternativo'}, {'id': 'AD-170', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre desvío al alternativo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre desvío al alternativo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'desvío al alternativo'}, {'id': 'AD-171', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona separación en pista?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación en pista; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación en pista'}, {'id': 'AD-172', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de separación en pista?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación en pista; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación en pista'}, {'id': 'AD-173', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene separación en pista?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación en pista; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación en pista'}, {'id': 'AD-174', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa separación en pista en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación en pista; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación en pista'}, {'id': 'AD-175', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre separación en pista?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación en pista; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación en pista'}, {'id': 'AD-176', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona CRM de tripulación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CRM de tripulación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CRM de tripulación'}, {'id': 'AD-177', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de CRM de tripulación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CRM de tripulación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CRM de tripulación'}, {'id': 'AD-178', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene CRM de tripulación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CRM de tripulación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CRM de tripulación'}, {'id': 'AD-179', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa CRM de tripulación en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CRM de tripulación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CRM de tripulación'}, {'id': 'AD-180', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre CRM de tripulación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre CRM de tripulación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'CRM de tripulación'}, {'id': 'AD-181', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona peso y balance?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre peso y balance; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'peso y balance'}, {'id': 'AD-182', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de peso y balance?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre peso y balance; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'peso y balance'}, {'id': 'AD-183', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene peso y balance?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre peso y balance; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'peso y balance'}, {'id': 'AD-184', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa peso y balance en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre peso y balance; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'peso y balance'}, {'id': 'AD-185', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre peso y balance?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre peso y balance; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'peso y balance'}, {'id': 'AD-186', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona operación ETOPS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre operación ETOPS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'operación ETOPS'}, {'id': 'AD-187', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de operación ETOPS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre operación ETOPS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'operación ETOPS'}, {'id': 'AD-188', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene operación ETOPS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre operación ETOPS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'operación ETOPS'}, {'id': 'AD-189', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa operación ETOPS en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre operación ETOPS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'operación ETOPS'}, {'id': 'AD-190', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre operación ETOPS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre operación ETOPS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'operación ETOPS'}, {'id': 'AD-191', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona reporte de incidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reporte de incidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reporte de incidentes'}, {'id': 'AD-192', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de reporte de incidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reporte de incidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reporte de incidentes'}, {'id': 'AD-193', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene reporte de incidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reporte de incidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reporte de incidentes'}, {'id': 'AD-194', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa reporte de incidentes en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reporte de incidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reporte de incidentes'}, {'id': 'AD-195', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre reporte de incidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reporte de incidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reporte de incidentes'}, {'id': 'AD-196', 'category': 'Operaciones y seguridad', 'title': '¿Cómo funciona gestión de amenazas y errores?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de amenazas y errores; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de amenazas y errores'}, {'id': 'AD-197', 'category': 'Operaciones y seguridad', 'title': '¿Qué determina el rendimiento de gestión de amenazas y errores?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de amenazas y errores; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de amenazas y errores'}, {'id': 'AD-198', 'category': 'Operaciones y seguridad', 'title': '¿Qué limitaciones tiene gestión de amenazas y errores?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de amenazas y errores; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de amenazas y errores'}, {'id': 'AD-199', 'category': 'Operaciones y seguridad', 'title': '¿Por qué importa gestión de amenazas y errores en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de amenazas y errores; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de amenazas y errores'}, {'id': 'AD-200', 'category': 'Operaciones y seguridad', 'title': '¿Qué errores comunes existen sobre gestión de amenazas y errores?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de amenazas y errores; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de amenazas y errores'}, {'id': 'AD-201', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona cizalladura del viento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cizalladura del viento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cizalladura del viento'}, {'id': 'AD-202', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de cizalladura del viento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cizalladura del viento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cizalladura del viento'}, {'id': 'AD-203', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene cizalladura del viento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cizalladura del viento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cizalladura del viento'}, {'id': 'AD-204', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa cizalladura del viento en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cizalladura del viento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cizalladura del viento'}, {'id': 'AD-205', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre cizalladura del viento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre cizalladura del viento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'cizalladura del viento'}, {'id': 'AD-206', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona microburst?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre microburst; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'microburst'}, {'id': 'AD-207', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de microburst?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre microburst; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'microburst'}, {'id': 'AD-208', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene microburst?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre microburst; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'microburst'}, {'id': 'AD-209', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa microburst en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre microburst; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'microburst'}, {'id': 'AD-210', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre microburst?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre microburst; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'microburst'}, {'id': 'AD-211', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona engelamiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre engelamiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'engelamiento'}, {'id': 'AD-212', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de engelamiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre engelamiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'engelamiento'}, {'id': 'AD-213', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene engelamiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre engelamiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'engelamiento'}, {'id': 'AD-214', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa engelamiento en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre engelamiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'engelamiento'}, {'id': 'AD-215', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre engelamiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre engelamiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'engelamiento'}, {'id': 'AD-216', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona turbulencia en aire claro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre turbulencia en aire claro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'turbulencia en aire claro'}, {'id': 'AD-217', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de turbulencia en aire claro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre turbulencia en aire claro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'turbulencia en aire claro'}, {'id': 'AD-218', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene turbulencia en aire claro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre turbulencia en aire claro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'turbulencia en aire claro'}, {'id': 'AD-219', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa turbulencia en aire claro en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre turbulencia en aire claro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'turbulencia en aire claro'}, {'id': 'AD-220', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre turbulencia en aire claro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre turbulencia en aire claro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'turbulencia en aire claro'}, {'id': 'AD-221', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona tormentas convectivas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tormentas convectivas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tormentas convectivas'}, {'id': 'AD-222', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de tormentas convectivas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tormentas convectivas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tormentas convectivas'}, {'id': 'AD-223', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene tormentas convectivas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tormentas convectivas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tormentas convectivas'}, {'id': 'AD-224', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa tormentas convectivas en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tormentas convectivas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tormentas convectivas'}, {'id': 'AD-225', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre tormentas convectivas?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre tormentas convectivas; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'tormentas convectivas'}, {'id': 'AD-226', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona corrientes en chorro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre corrientes en chorro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'corrientes en chorro'}, {'id': 'AD-227', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de corrientes en chorro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre corrientes en chorro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'corrientes en chorro'}, {'id': 'AD-228', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene corrientes en chorro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre corrientes en chorro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'corrientes en chorro'}, {'id': 'AD-229', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa corrientes en chorro en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre corrientes en chorro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'corrientes en chorro'}, {'id': 'AD-230', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre corrientes en chorro?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre corrientes en chorro; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'corrientes en chorro'}, {'id': 'AD-231', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona visibilidad RVR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre visibilidad RVR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'visibilidad RVR'}, {'id': 'AD-232', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de visibilidad RVR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre visibilidad RVR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'visibilidad RVR'}, {'id': 'AD-233', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene visibilidad RVR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre visibilidad RVR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'visibilidad RVR'}, {'id': 'AD-234', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa visibilidad RVR en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre visibilidad RVR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'visibilidad RVR'}, {'id': 'AD-235', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre visibilidad RVR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre visibilidad RVR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'visibilidad RVR'}, {'id': 'AD-236', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona niebla de radiación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre niebla de radiación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'niebla de radiación'}, {'id': 'AD-237', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de niebla de radiación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre niebla de radiación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'niebla de radiación'}, {'id': 'AD-238', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene niebla de radiación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre niebla de radiación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'niebla de radiación'}, {'id': 'AD-239', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa niebla de radiación en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre niebla de radiación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'niebla de radiación'}, {'id': 'AD-240', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre niebla de radiación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre niebla de radiación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'niebla de radiación'}, {'id': 'AD-241', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona ceniza volcánica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ceniza volcánica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ceniza volcánica'}, {'id': 'AD-242', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de ceniza volcánica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ceniza volcánica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ceniza volcánica'}, {'id': 'AD-243', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene ceniza volcánica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ceniza volcánica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ceniza volcánica'}, {'id': 'AD-244', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa ceniza volcánica en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ceniza volcánica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ceniza volcánica'}, {'id': 'AD-245', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre ceniza volcánica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ceniza volcánica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ceniza volcánica'}, {'id': 'AD-246', 'category': 'Meteorología aeronáutica', 'title': '¿Cómo funciona onda de montaña?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de montaña; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de montaña'}, {'id': 'AD-247', 'category': 'Meteorología aeronáutica', 'title': '¿Qué determina el rendimiento de onda de montaña?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de montaña; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de montaña'}, {'id': 'AD-248', 'category': 'Meteorología aeronáutica', 'title': '¿Qué limitaciones tiene onda de montaña?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de montaña; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de montaña'}, {'id': 'AD-249', 'category': 'Meteorología aeronáutica', 'title': '¿Por qué importa onda de montaña en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de montaña; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de montaña'}, {'id': 'AD-250', 'category': 'Meteorología aeronáutica', 'title': '¿Qué errores comunes existen sobre onda de montaña?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre onda de montaña; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'onda de montaña'}, {'id': 'AD-251', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona ADS-B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ADS-B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ADS-B'}, {'id': 'AD-252', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de ADS-B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ADS-B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ADS-B'}, {'id': 'AD-253', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene ADS-B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ADS-B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ADS-B'}, {'id': 'AD-254', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa ADS-B en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ADS-B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ADS-B'}, {'id': 'AD-255', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre ADS-B?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ADS-B; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ADS-B'}, {'id': 'AD-256', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona transpondedor modo S?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre transpondedor modo S; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'transpondedor modo S'}, {'id': 'AD-257', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de transpondedor modo S?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre transpondedor modo S; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'transpondedor modo S'}, {'id': 'AD-258', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene transpondedor modo S?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre transpondedor modo S; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'transpondedor modo S'}, {'id': 'AD-259', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa transpondedor modo S en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre transpondedor modo S; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'transpondedor modo S'}, {'id': 'AD-260', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre transpondedor modo S?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre transpondedor modo S; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'transpondedor modo S'}, {'id': 'AD-261', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona ILS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ILS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ILS'}, {'id': 'AD-262', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de ILS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ILS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ILS'}, {'id': 'AD-263', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene ILS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ILS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ILS'}, {'id': 'AD-264', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa ILS en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ILS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ILS'}, {'id': 'AD-265', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre ILS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ILS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ILS'}, {'id': 'AD-266', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona aproximación RNP?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación RNP; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación RNP'}, {'id': 'AD-267', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de aproximación RNP?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación RNP; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación RNP'}, {'id': 'AD-268', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene aproximación RNP?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación RNP; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación RNP'}, {'id': 'AD-269', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa aproximación RNP en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación RNP; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación RNP'}, {'id': 'AD-270', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre aproximación RNP?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aproximación RNP; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aproximación RNP'}, {'id': 'AD-271', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona GNSS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GNSS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GNSS'}, {'id': 'AD-272', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de GNSS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GNSS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GNSS'}, {'id': 'AD-273', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene GNSS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GNSS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GNSS'}, {'id': 'AD-274', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa GNSS en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GNSS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GNSS'}, {'id': 'AD-275', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre GNSS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre GNSS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'GNSS'}, {'id': 'AD-276', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona VOR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre VOR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'VOR'}, {'id': 'AD-277', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de VOR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre VOR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'VOR'}, {'id': 'AD-278', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene VOR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre VOR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'VOR'}, {'id': 'AD-279', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa VOR en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre VOR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'VOR'}, {'id': 'AD-280', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre VOR?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre VOR; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'VOR'}, {'id': 'AD-281', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona TCAS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre TCAS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'TCAS'}, {'id': 'AD-282', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de TCAS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre TCAS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'TCAS'}, {'id': 'AD-283', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene TCAS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre TCAS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'TCAS'}, {'id': 'AD-284', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa TCAS en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre TCAS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'TCAS'}, {'id': 'AD-285', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre TCAS?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre TCAS; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'TCAS'}, {'id': 'AD-286', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona separación radar?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación radar; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación radar'}, {'id': 'AD-287', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de separación radar?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación radar; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación radar'}, {'id': 'AD-288', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene separación radar?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación radar; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación radar'}, {'id': 'AD-289', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa separación radar en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación radar; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación radar'}, {'id': 'AD-290', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre separación radar?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre separación radar; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'separación radar'}, {'id': 'AD-291', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona NOTAM?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre NOTAM; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'NOTAM'}, {'id': 'AD-292', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de NOTAM?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre NOTAM; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'NOTAM'}, {'id': 'AD-293', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene NOTAM?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre NOTAM; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'NOTAM'}, {'id': 'AD-294', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa NOTAM en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre NOTAM; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'NOTAM'}, {'id': 'AD-295', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre NOTAM?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre NOTAM; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'NOTAM'}, {'id': 'AD-296', 'category': 'Navegación y control aéreo', 'title': '¿Cómo funciona altitud de transición?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre altitud de transición; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'altitud de transición'}, {'id': 'AD-297', 'category': 'Navegación y control aéreo', 'title': '¿Qué determina el rendimiento de altitud de transición?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre altitud de transición; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'altitud de transición'}, {'id': 'AD-298', 'category': 'Navegación y control aéreo', 'title': '¿Qué limitaciones tiene altitud de transición?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre altitud de transición; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'altitud de transición'}, {'id': 'AD-299', 'category': 'Navegación y control aéreo', 'title': '¿Por qué importa altitud de transición en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre altitud de transición; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'altitud de transición'}, {'id': 'AD-300', 'category': 'Navegación y control aéreo', 'title': '¿Qué errores comunes existen sobre altitud de transición?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre altitud de transición; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'altitud de transición'}, {'id': 'AD-301', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona factor de ocupación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre factor de ocupación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'factor de ocupación'}, {'id': 'AD-302', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de factor de ocupación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre factor de ocupación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'factor de ocupación'}, {'id': 'AD-303', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene factor de ocupación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre factor de ocupación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'factor de ocupación'}, {'id': 'AD-304', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa factor de ocupación en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre factor de ocupación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'factor de ocupación'}, {'id': 'AD-305', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre factor de ocupación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre factor de ocupación; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'factor de ocupación'}, {'id': 'AD-306', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona costo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costo de combustible'}, {'id': 'AD-307', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de costo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costo de combustible'}, {'id': 'AD-308', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene costo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costo de combustible'}, {'id': 'AD-309', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa costo de combustible en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costo de combustible'}, {'id': 'AD-310', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre costo de combustible?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costo de combustible; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costo de combustible'}, {'id': 'AD-311', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona leasing aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre leasing aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'leasing aeronáutico'}, {'id': 'AD-312', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de leasing aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre leasing aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'leasing aeronáutico'}, {'id': 'AD-313', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene leasing aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre leasing aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'leasing aeronáutico'}, {'id': 'AD-314', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa leasing aeronáutico en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre leasing aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'leasing aeronáutico'}, {'id': 'AD-315', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre leasing aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre leasing aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'leasing aeronáutico'}, {'id': 'AD-316', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona rentabilidad de una ruta?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre rentabilidad de una ruta; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'rentabilidad de una ruta'}, {'id': 'AD-317', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de rentabilidad de una ruta?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre rentabilidad de una ruta; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'rentabilidad de una ruta'}, {'id': 'AD-318', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene rentabilidad de una ruta?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre rentabilidad de una ruta; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'rentabilidad de una ruta'}, {'id': 'AD-319', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa rentabilidad de una ruta en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre rentabilidad de una ruta; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'rentabilidad de una ruta'}, {'id': 'AD-320', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre rentabilidad de una ruta?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre rentabilidad de una ruta; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'rentabilidad de una ruta'}, {'id': 'AD-321', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona carga aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre carga aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'carga aérea'}, {'id': 'AD-322', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de carga aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre carga aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'carga aérea'}, {'id': 'AD-323', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene carga aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre carga aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'carga aérea'}, {'id': 'AD-324', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa carga aérea en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre carga aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'carga aérea'}, {'id': 'AD-325', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre carga aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre carga aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'carga aérea'}, {'id': 'AD-326', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona ingresos auxiliares?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ingresos auxiliares; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ingresos auxiliares'}, {'id': 'AD-327', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de ingresos auxiliares?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ingresos auxiliares; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ingresos auxiliares'}, {'id': 'AD-328', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene ingresos auxiliares?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ingresos auxiliares; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ingresos auxiliares'}, {'id': 'AD-329', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa ingresos auxiliares en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ingresos auxiliares; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ingresos auxiliares'}, {'id': 'AD-330', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre ingresos auxiliares?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre ingresos auxiliares; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'ingresos auxiliares'}, {'id': 'AD-331', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona utilización diaria de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre utilización diaria de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'utilización diaria de aeronaves'}, {'id': 'AD-332', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de utilización diaria de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre utilización diaria de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'utilización diaria de aeronaves'}, {'id': 'AD-333', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene utilización diaria de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre utilización diaria de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'utilización diaria de aeronaves'}, {'id': 'AD-334', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa utilización diaria de aeronaves en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre utilización diaria de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'utilización diaria de aeronaves'}, {'id': 'AD-335', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre utilización diaria de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre utilización diaria de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'utilización diaria de aeronaves'}, {'id': 'AD-336', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona costos de mantenimiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costos de mantenimiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costos de mantenimiento'}, {'id': 'AD-337', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de costos de mantenimiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costos de mantenimiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costos de mantenimiento'}, {'id': 'AD-338', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene costos de mantenimiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costos de mantenimiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costos de mantenimiento'}, {'id': 'AD-339', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa costos de mantenimiento en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costos de mantenimiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costos de mantenimiento'}, {'id': 'AD-340', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre costos de mantenimiento?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre costos de mantenimiento; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'costos de mantenimiento'}, {'id': 'AD-341', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona planificación de flota?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre planificación de flota; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'planificación de flota'}, {'id': 'AD-342', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de planificación de flota?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre planificación de flota; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'planificación de flota'}, {'id': 'AD-343', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene planificación de flota?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre planificación de flota; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'planificación de flota'}, {'id': 'AD-344', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa planificación de flota en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre planificación de flota; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'planificación de flota'}, {'id': 'AD-345', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre planificación de flota?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre planificación de flota; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'planificación de flota'}, {'id': 'AD-346', 'category': 'Economía y aerolíneas', 'title': '¿Cómo funciona precio del queroseno?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre precio del queroseno; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'precio del queroseno'}, {'id': 'AD-347', 'category': 'Economía y aerolíneas', 'title': '¿Qué determina el rendimiento de precio del queroseno?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre precio del queroseno; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'precio del queroseno'}, {'id': 'AD-348', 'category': 'Economía y aerolíneas', 'title': '¿Qué limitaciones tiene precio del queroseno?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre precio del queroseno; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'precio del queroseno'}, {'id': 'AD-349', 'category': 'Economía y aerolíneas', 'title': '¿Por qué importa precio del queroseno en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre precio del queroseno; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'precio del queroseno'}, {'id': 'AD-350', 'category': 'Economía y aerolíneas', 'title': '¿Qué errores comunes existen sobre precio del queroseno?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre precio del queroseno; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'precio del queroseno'}, {'id': 'AD-351', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona certificación de tipo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre certificación de tipo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'certificación de tipo'}, {'id': 'AD-352', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de certificación de tipo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre certificación de tipo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'certificación de tipo'}, {'id': 'AD-353', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene certificación de tipo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre certificación de tipo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'certificación de tipo'}, {'id': 'AD-354', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa certificación de tipo en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre certificación de tipo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'certificación de tipo'}, {'id': 'AD-355', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre certificación de tipo?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre certificación de tipo; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'certificación de tipo'}, {'id': 'AD-356', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona libertades del aire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre libertades del aire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'libertades del aire'}, {'id': 'AD-357', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de libertades del aire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre libertades del aire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'libertades del aire'}, {'id': 'AD-358', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene libertades del aire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre libertades del aire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'libertades del aire'}, {'id': 'AD-359', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa libertades del aire en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre libertades del aire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'libertades del aire'}, {'id': 'AD-360', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre libertades del aire?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre libertades del aire; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'libertades del aire'}, {'id': 'AD-361', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona derechos de tráfico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre derechos de tráfico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'derechos de tráfico'}, {'id': 'AD-362', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de derechos de tráfico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre derechos de tráfico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'derechos de tráfico'}, {'id': 'AD-363', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene derechos de tráfico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre derechos de tráfico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'derechos de tráfico'}, {'id': 'AD-364', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa derechos de tráfico en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre derechos de tráfico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'derechos de tráfico'}, {'id': 'AD-365', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre derechos de tráfico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre derechos de tráfico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'derechos de tráfico'}, {'id': 'AD-366', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona normativa de emisiones CORSIA?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre normativa de emisiones CORSIA; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'normativa de emisiones CORSIA'}, {'id': 'AD-367', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de normativa de emisiones CORSIA?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre normativa de emisiones CORSIA; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'normativa de emisiones CORSIA'}, {'id': 'AD-368', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene normativa de emisiones CORSIA?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre normativa de emisiones CORSIA; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'normativa de emisiones CORSIA'}, {'id': 'AD-369', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa normativa de emisiones CORSIA en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre normativa de emisiones CORSIA; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'normativa de emisiones CORSIA'}, {'id': 'AD-370', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre normativa de emisiones CORSIA?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre normativa de emisiones CORSIA; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'normativa de emisiones CORSIA'}, {'id': 'AD-371', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona reglas de cabotaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de cabotaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de cabotaje'}, {'id': 'AD-372', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de reglas de cabotaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de cabotaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de cabotaje'}, {'id': 'AD-373', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene reglas de cabotaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de cabotaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de cabotaje'}, {'id': 'AD-374', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa reglas de cabotaje en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de cabotaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de cabotaje'}, {'id': 'AD-375', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre reglas de cabotaje?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de cabotaje; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de cabotaje'}, {'id': 'AD-376', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona autoridad aeronáutica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre autoridad aeronáutica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'autoridad aeronáutica'}, {'id': 'AD-377', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de autoridad aeronáutica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre autoridad aeronáutica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'autoridad aeronáutica'}, {'id': 'AD-378', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene autoridad aeronáutica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre autoridad aeronáutica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'autoridad aeronáutica'}, {'id': 'AD-379', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa autoridad aeronáutica en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre autoridad aeronáutica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'autoridad aeronáutica'}, {'id': 'AD-380', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre autoridad aeronáutica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre autoridad aeronáutica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'autoridad aeronáutica'}, {'id': 'AD-381', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona investigación de accidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre investigación de accidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'investigación de accidentes'}, {'id': 'AD-382', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de investigación de accidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre investigación de accidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'investigación de accidentes'}, {'id': 'AD-383', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene investigación de accidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre investigación de accidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'investigación de accidentes'}, {'id': 'AD-384', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa investigación de accidentes en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre investigación de accidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'investigación de accidentes'}, {'id': 'AD-385', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre investigación de accidentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre investigación de accidentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'investigación de accidentes'}, {'id': 'AD-386', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona acuerdos bilaterales?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre acuerdos bilaterales; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'acuerdos bilaterales'}, {'id': 'AD-387', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de acuerdos bilaterales?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre acuerdos bilaterales; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'acuerdos bilaterales'}, {'id': 'AD-388', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene acuerdos bilaterales?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre acuerdos bilaterales; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'acuerdos bilaterales'}, {'id': 'AD-389', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa acuerdos bilaterales en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre acuerdos bilaterales; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'acuerdos bilaterales'}, {'id': 'AD-390', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre acuerdos bilaterales?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre acuerdos bilaterales; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'acuerdos bilaterales'}, {'id': 'AD-391', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona gestión de slots?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de slots; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de slots'}, {'id': 'AD-392', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de gestión de slots?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de slots; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de slots'}, {'id': 'AD-393', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene gestión de slots?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de slots; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de slots'}, {'id': 'AD-394', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa gestión de slots en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de slots; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de slots'}, {'id': 'AD-395', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre gestión de slots?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre gestión de slots; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'gestión de slots'}, {'id': 'AD-396', 'category': 'Regulación y política aeronáutica', 'title': '¿Cómo funciona reglas de descanso de tripulaciones?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de descanso de tripulaciones; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de descanso de tripulaciones'}, {'id': 'AD-397', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué determina el rendimiento de reglas de descanso de tripulaciones?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de descanso de tripulaciones; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de descanso de tripulaciones'}, {'id': 'AD-398', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué limitaciones tiene reglas de descanso de tripulaciones?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de descanso de tripulaciones; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de descanso de tripulaciones'}, {'id': 'AD-399', 'category': 'Regulación y política aeronáutica', 'title': '¿Por qué importa reglas de descanso de tripulaciones en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de descanso de tripulaciones; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de descanso de tripulaciones'}, {'id': 'AD-400', 'category': 'Regulación y política aeronáutica', 'title': '¿Qué errores comunes existen sobre reglas de descanso de tripulaciones?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre reglas de descanso de tripulaciones; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'reglas de descanso de tripulaciones'}, {'id': 'AD-401', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona combustible SAF?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre combustible SAF; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'combustible SAF'}, {'id': 'AD-402', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de combustible SAF?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre combustible SAF; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'combustible SAF'}, {'id': 'AD-403', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene combustible SAF?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre combustible SAF; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'combustible SAF'}, {'id': 'AD-404', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa combustible SAF en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre combustible SAF; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'combustible SAF'}, {'id': 'AD-405', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre combustible SAF?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre combustible SAF; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'combustible SAF'}, {'id': 'AD-406', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona hidrógeno aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hidrógeno aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hidrógeno aeronáutico'}, {'id': 'AD-407', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de hidrógeno aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hidrógeno aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hidrógeno aeronáutico'}, {'id': 'AD-408', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene hidrógeno aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hidrógeno aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hidrógeno aeronáutico'}, {'id': 'AD-409', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa hidrógeno aeronáutico en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hidrógeno aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hidrógeno aeronáutico'}, {'id': 'AD-410', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre hidrógeno aeronáutico?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hidrógeno aeronáutico; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hidrógeno aeronáutico'}, {'id': 'AD-411', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona propulsión eléctrica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre propulsión eléctrica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'propulsión eléctrica'}, {'id': 'AD-412', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de propulsión eléctrica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre propulsión eléctrica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'propulsión eléctrica'}, {'id': 'AD-413', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene propulsión eléctrica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre propulsión eléctrica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'propulsión eléctrica'}, {'id': 'AD-414', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa propulsión eléctrica en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre propulsión eléctrica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'propulsión eléctrica'}, {'id': 'AD-415', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre propulsión eléctrica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre propulsión eléctrica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'propulsión eléctrica'}, {'id': 'AD-416', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona motores de ciclo abierto?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre motores de ciclo abierto; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'motores de ciclo abierto'}, {'id': 'AD-417', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de motores de ciclo abierto?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre motores de ciclo abierto; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'motores de ciclo abierto'}, {'id': 'AD-418', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene motores de ciclo abierto?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre motores de ciclo abierto; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'motores de ciclo abierto'}, {'id': 'AD-419', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa motores de ciclo abierto en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre motores de ciclo abierto; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'motores de ciclo abierto'}, {'id': 'AD-420', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre motores de ciclo abierto?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre motores de ciclo abierto; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'motores de ciclo abierto'}, {'id': 'AD-421', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona materiales compuestos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre materiales compuestos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'materiales compuestos'}, {'id': 'AD-422', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de materiales compuestos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre materiales compuestos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'materiales compuestos'}, {'id': 'AD-423', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene materiales compuestos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre materiales compuestos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'materiales compuestos'}, {'id': 'AD-424', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa materiales compuestos en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre materiales compuestos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'materiales compuestos'}, {'id': 'AD-425', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre materiales compuestos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre materiales compuestos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'materiales compuestos'}, {'id': 'AD-426', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona impresión 3D de componentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre impresión 3D de componentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'impresión 3D de componentes'}, {'id': 'AD-427', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de impresión 3D de componentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre impresión 3D de componentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'impresión 3D de componentes'}, {'id': 'AD-428', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene impresión 3D de componentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre impresión 3D de componentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'impresión 3D de componentes'}, {'id': 'AD-429', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa impresión 3D de componentes en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre impresión 3D de componentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'impresión 3D de componentes'}, {'id': 'AD-430', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre impresión 3D de componentes?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre impresión 3D de componentes; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'impresión 3D de componentes'}, {'id': 'AD-431', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona baterías de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre baterías de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'baterías de aeronaves'}, {'id': 'AD-432', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de baterías de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre baterías de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'baterías de aeronaves'}, {'id': 'AD-433', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene baterías de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre baterías de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'baterías de aeronaves'}, {'id': 'AD-434', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa baterías de aeronaves en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre baterías de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'baterías de aeronaves'}, {'id': 'AD-435', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre baterías de aeronaves?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre baterías de aeronaves; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'baterías de aeronaves'}, {'id': 'AD-436', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona optimización de trayectorias?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre optimización de trayectorias; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'optimización de trayectorias'}, {'id': 'AD-437', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de optimización de trayectorias?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre optimización de trayectorias; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'optimización de trayectorias'}, {'id': 'AD-438', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene optimización de trayectorias?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre optimización de trayectorias; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'optimización de trayectorias'}, {'id': 'AD-439', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa optimización de trayectorias en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre optimización de trayectorias; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'optimización de trayectorias'}, {'id': 'AD-440', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre optimización de trayectorias?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre optimización de trayectorias; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'optimización de trayectorias'}, {'id': 'AD-441', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona contrails y clima?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre contrails y clima; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'contrails y clima'}, {'id': 'AD-442', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de contrails y clima?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre contrails y clima; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'contrails y clima'}, {'id': 'AD-443', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene contrails y clima?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre contrails y clima; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'contrails y clima'}, {'id': 'AD-444', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa contrails y clima en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre contrails y clima; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'contrails y clima'}, {'id': 'AD-445', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre contrails y clima?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre contrails y clima; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'contrails y clima'}, {'id': 'AD-446', 'category': 'Ciencia e innovación', 'title': '¿Cómo funciona aviación supersónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aviación supersónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aviación supersónica'}, {'id': 'AD-447', 'category': 'Ciencia e innovación', 'title': '¿Qué determina el rendimiento de aviación supersónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aviación supersónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aviación supersónica'}, {'id': 'AD-448', 'category': 'Ciencia e innovación', 'title': '¿Qué limitaciones tiene aviación supersónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aviación supersónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aviación supersónica'}, {'id': 'AD-449', 'category': 'Ciencia e innovación', 'title': '¿Por qué importa aviación supersónica en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aviación supersónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aviación supersónica'}, {'id': 'AD-450', 'category': 'Ciencia e innovación', 'title': '¿Qué errores comunes existen sobre aviación supersónica?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre aviación supersónica; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'aviación supersónica'}, {'id': 'AD-451', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona hermanos Wright?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hermanos Wright; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hermanos Wright'}, {'id': 'AD-452', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de hermanos Wright?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hermanos Wright; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hermanos Wright'}, {'id': 'AD-453', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene hermanos Wright?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hermanos Wright; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hermanos Wright'}, {'id': 'AD-454', 'category': 'Historia de la aviación', 'title': '¿Por qué importa hermanos Wright en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hermanos Wright; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hermanos Wright'}, {'id': 'AD-455', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre hermanos Wright?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre hermanos Wright; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'hermanos Wright'}, {'id': 'AD-456', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona Boeing 747?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Boeing 747; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Boeing 747'}, {'id': 'AD-457', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de Boeing 747?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Boeing 747; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Boeing 747'}, {'id': 'AD-458', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene Boeing 747?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Boeing 747; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Boeing 747'}, {'id': 'AD-459', 'category': 'Historia de la aviación', 'title': '¿Por qué importa Boeing 747 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Boeing 747; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Boeing 747'}, {'id': 'AD-460', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre Boeing 747?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Boeing 747; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Boeing 747'}, {'id': 'AD-461', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona Concorde?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Concorde; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Concorde'}, {'id': 'AD-462', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de Concorde?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Concorde; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Concorde'}, {'id': 'AD-463', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene Concorde?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Concorde; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Concorde'}, {'id': 'AD-464', 'category': 'Historia de la aviación', 'title': '¿Por qué importa Concorde en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Concorde; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Concorde'}, {'id': 'AD-465', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre Concorde?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Concorde; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Concorde'}, {'id': 'AD-466', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona DC-3?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre DC-3; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'DC-3'}, {'id': 'AD-467', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de DC-3?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre DC-3; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'DC-3'}, {'id': 'AD-468', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene DC-3?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre DC-3; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'DC-3'}, {'id': 'AD-469', 'category': 'Historia de la aviación', 'title': '¿Por qué importa DC-3 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre DC-3; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'DC-3'}, {'id': 'AD-470', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre DC-3?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre DC-3; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'DC-3'}, {'id': 'AD-471', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona Airbus A320?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Airbus A320; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Airbus A320'}, {'id': 'AD-472', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de Airbus A320?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Airbus A320; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Airbus A320'}, {'id': 'AD-473', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene Airbus A320?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Airbus A320; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Airbus A320'}, {'id': 'AD-474', 'category': 'Historia de la aviación', 'title': '¿Por qué importa Airbus A320 en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Airbus A320; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Airbus A320'}, {'id': 'AD-475', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre Airbus A320?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre Airbus A320; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'Airbus A320'}, {'id': 'AD-476', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona primer vuelo comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer vuelo comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer vuelo comercial'}, {'id': 'AD-477', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de primer vuelo comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer vuelo comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer vuelo comercial'}, {'id': 'AD-478', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene primer vuelo comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer vuelo comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer vuelo comercial'}, {'id': 'AD-479', 'category': 'Historia de la aviación', 'title': '¿Por qué importa primer vuelo comercial en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer vuelo comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer vuelo comercial'}, {'id': 'AD-480', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre primer vuelo comercial?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer vuelo comercial; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer vuelo comercial'}, {'id': 'AD-481', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona primer avión a reacción?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer avión a reacción; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer avión a reacción'}, {'id': 'AD-482', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de primer avión a reacción?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer avión a reacción; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer avión a reacción'}, {'id': 'AD-483', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene primer avión a reacción?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer avión a reacción; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer avión a reacción'}, {'id': 'AD-484', 'category': 'Historia de la aviación', 'title': '¿Por qué importa primer avión a reacción en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer avión a reacción; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer avión a reacción'}, {'id': 'AD-485', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre primer avión a reacción?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primer avión a reacción; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primer avión a reacción'}, {'id': 'AD-486', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona evolución de navegación aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de navegación aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de navegación aérea'}, {'id': 'AD-487', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de evolución de navegación aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de navegación aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de navegación aérea'}, {'id': 'AD-488', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene evolución de navegación aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de navegación aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de navegación aérea'}, {'id': 'AD-489', 'category': 'Historia de la aviación', 'title': '¿Por qué importa evolución de navegación aérea en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de navegación aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de navegación aérea'}, {'id': 'AD-490', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre evolución de navegación aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de navegación aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de navegación aérea'}, {'id': 'AD-491', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona primeros vuelos transatlánticos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primeros vuelos transatlánticos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primeros vuelos transatlánticos'}, {'id': 'AD-492', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de primeros vuelos transatlánticos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primeros vuelos transatlánticos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primeros vuelos transatlánticos'}, {'id': 'AD-493', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene primeros vuelos transatlánticos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primeros vuelos transatlánticos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primeros vuelos transatlánticos'}, {'id': 'AD-494', 'category': 'Historia de la aviación', 'title': '¿Por qué importa primeros vuelos transatlánticos en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primeros vuelos transatlánticos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primeros vuelos transatlánticos'}, {'id': 'AD-495', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre primeros vuelos transatlánticos?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre primeros vuelos transatlánticos; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'primeros vuelos transatlánticos'}, {'id': 'AD-496', 'category': 'Historia de la aviación', 'title': '¿Cómo funciona evolución de seguridad aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de seguridad aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de seguridad aérea'}, {'id': 'AD-497', 'category': 'Historia de la aviación', 'title': '¿Qué determina el rendimiento de evolución de seguridad aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de seguridad aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de seguridad aérea'}, {'id': 'AD-498', 'category': 'Historia de la aviación', 'title': '¿Qué limitaciones tiene evolución de seguridad aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de seguridad aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de seguridad aérea'}, {'id': 'AD-499', 'category': 'Historia de la aviación', 'title': '¿Por qué importa evolución de seguridad aérea en aviación?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de seguridad aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de seguridad aérea'}, {'id': 'AD-500', 'category': 'Historia de la aviación', 'title': '¿Qué errores comunes existen sobre evolución de seguridad aérea?', 'script': '', 'source': '', 'lesson': 'Explica un dato técnico comprobable sobre evolución de seguridad aérea; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.', 'image_query': 'evolución de seguridad aérea'}]
# VALORES HARDCODE PARA PRUEBAS LOCALES (ficticios, nunca credenciales reales).
# Los secretos de GitHub prevalecen sobre estos valores.
# Para pruebas locales se puede sustituir el valor de demostración.
# No introduzcas credenciales reales en un repositorio público.
TEST_OPENROUTER_API_KEY = "PON_AQUI_TU_CLAVE_DE_PRUEBA"
TEST_INSTAGRAM_TOKEN = "PON_AQUI_TU_TOKEN_DE_PRUEBA"
TEST_INSTAGRAM_USER_ID = "00000000000000000"

# Únicamente se acepta el router gratuito o un modelo con sufijo :free.
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openrouter/free').strip() or 'openrouter/free'
if OPENROUTER_MODEL != 'openrouter/free' and not OPENROUTER_MODEL.endswith(':free'):
    raise RuntimeError('Modelo no gratuito rechazado: configura openrouter/free o un modelo :free')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

GRAPH_VERSION = os.getenv('IG_GRAPH_VERSION', 'v25.0')

def credential(name, demo):
    value = os.getenv(name, '').strip() or demo
    if not value or value.startswith('PON_AQUI_') or value == '00000000000000000':
        raise RuntimeError(f'Configura {name} como secreto de GitHub o valor de prueba local')
    return value

BRAND = 'AERO_DATOS'


def catalog():
    return AERO_CATALOG


def _parse_ai_json(text):
    """Parsea un objeto JSON completo; admite fences y texto envolvente.

    No intenta cerrar comillas ni fabricar campos de un JSON truncado.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Respuesta sin texto JSON')
    cleaned = text.strip()
    fenced = re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, flags=re.I)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find('{')
        if start < 0:
            raise
        value, end = json.JSONDecoder().raw_decode(cleaned[start:])
        rest = cleaned[start + end:].strip()
        if rest and not rest.startswith('```'):
            raise ValueError('Texto inesperado después del JSON')
    if not isinstance(value, dict):
        raise ValueError('OpenRouter debe devolver un objeto JSON')
    return value


def _validate_ai_data(data):
    for field in ('title', 'script', 'lesson', 'fact'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f'Guion de IA sin campo requerido: {field}')
    words = len(data['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'Duración incompatible: {words} palabras (30-60 aceptadas)')
    return data


def ajustar_texto_visual(texto, max_caracteres=40, max_palabras=6):
    """Obtiene una microfrase SIN cortar letras ni añadir puntos suspensivos.

    Si la entrada excede seis palabras, se utiliza una frase breve completa
    cuando sea posible. En caso contrario, se elige un grupo de palabras
    recortado en frontera léxica y se quita un conector final colgante.
    """
    texto = re.sub(r'\s+', ' ', str(texto or '')).strip(' \t\n.,;:')
    texto = re.sub(r'https?://\S+', '', texto).strip()
    # Si una pregunta original queda demasiado larga, presentar la afirmación central.
    if len(texto.split()) > max_palabras:
        texto = re.sub(r'^[¿¡]?\s*(?:sab[ií]as que|sab[ií]as|te imaginas que)\s+', '', texto, flags=re.I)
    texto = texto.lstrip('¿¡')
    if not texto:
        return 'DESCUBRE ALGO NUEVO'
    candidatos = re.split(r'(?<=[.!?;:])\s+|\s+[—–]\s+|,\s+', texto)
    candidatos = [x.strip(' .,:;!?') for x in candidatos if x.strip(' .,:;!?')]
    candidato = next((x for x in candidatos if len(x.split()) <= max_palabras
                      and len(x) <= max_caracteres), candidatos[0] if candidatos else texto)
    palabras = candidato.split()
    elegidas = []
    for palabra in palabras:
        if len(elegidas) >= max_palabras or len(' '.join(elegidas + [palabra])) > max_caracteres:
            break
        elegidas.append(palabra)
    conectores = {'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'y', 'o', 'que',
                  'para', 'por', 'con', 'sin', 'en', 'a', 'al', 'su', 'sus', 'es'}
    while len(elegidas) > 2 and elegidas[-1].lower().strip('.,:;') in conectores:
        elegidas.pop()
    return ' '.join(elegidas).strip(' .,:;!?¿¡') or 'DATO SORPRENDENTE'


# Los textos son ideas completas, nunca fragmentos cortados.
VISUAL_MIN_WORDS = 3
VISUAL_MAX_WORDS = 12
VISUAL_MAX_CHARS = 72
GENERIC_VISUALS = (
    'sabias esto', 'ahora ya lo sabes', 'dato sorprendente',
    'descubre algo nuevo', 'una idea util', 'increible pero cierto',
    'no te lo pierdas', 'esto te sorprendera', 'sigue aprendiendo',
    'te imaginas', 'mira esto', 'un dato real',
)
VISUAL_STOP_WORDS = {
    'a', 'al', 'ante', 'como', 'con', 'de', 'del', 'desde', 'donde',
    'el', 'ella', 'en', 'entre', 'es', 'esa', 'ese', 'esta', 'este',
    'hay', 'la', 'las', 'le', 'lo', 'los', 'más', 'menos', 'mi',
    'no', 'nos', 'o', 'para', 'pero', 'por', 'porque', 'que',
    'se', 'sin', 'su', 'sus', 'te', 'tu', 'tus', 'un', 'una', 'uno',
    'y', 'ya', 'si', 'son', 'puede', 'pueden', 'ser', 'tiene',
}


def _visual_normalizado(value):
    import unicodedata
    text = unicodedata.normalize('NFKD', str(value).lower())
    return ''.join(c for c in text if not unicodedata.combining(c))


def _palabras_relevantes(value):
    return {w for w in re.findall(r'[a-z0-9]+', _visual_normalizado(value))
            if len(w) >= 4 and w not in VISUAL_STOP_WORDS}


def validar_microfrases(visuals, script, title='', fact='', lesson=''):
    """Valida significado básico y legibilidad; nunca recorta una idea.

    Verifica relación léxica con el relato; no pretende garantizar exactitud
    factual ni reemplazar una revisión editorial humana.
    """
    if not isinstance(visuals, list) or len(visuals) != 5:
        raise ValueError('Se requieren cinco micromensajes relacionados con el guion')
    universo = _palabras_relevantes(' '.join([script, title, fact, lesson]))
    seen = set()
    result = []
    for index, item in enumerate(visuals, 1):
        if not isinstance(item, str):
            raise ValueError(f'Escena {index}: el texto no es una cadena')
        clean = re.sub(r'\s+', ' ', item).strip().strip('"“”')
        words = clean.split()
        if not (VISUAL_MIN_WORDS <= len(words) <= VISUAL_MAX_WORDS):
            raise ValueError(f'Escena {index}: requiere entre 3 y 9 palabras, tiene {len(words)}')
        if len(clean) > VISUAL_MAX_CHARS:
            raise ValueError(f'Escena {index}: supera 72 caracteres; reformular, no truncar')
        if clean.endswith(('...', '…', ':', ',', ';')):
            raise ValueError(f'Escena {index}: mensaje incompleto')
        norm = _visual_normalizado(clean).strip(' .!?¿¡')
        if any(generic in norm for generic in GENERIC_VISUALS):
            raise ValueError(f'Escena {index}: frase generica sin aprendizaje')
        if norm in seen:
            raise ValueError(f'Escena {index}: texto repetido')
        seen.add(norm)
        if not (_palabras_relevantes(clean) & universo):
            raise ValueError(f'Escena {index}: no se identifica relación con el contenido narrado')
        result.append(clean)
    return result


def microfrases(ep):
    """Cinco mensajes completos que expresan conocimiento, no títulos vacíos."""
    return validar_microfrases(
        ep.get('visuals'), ep.get('script', ''), ep.get('title', ''),
        ep.get('fact', ''), ep.get('lesson', ''),
    )


def texto_centrado_seguro(draw, texto, *, centro_y, ancho=560, max_lineas=3):
    """Adapta fuente y saltos sin acortar el mensaje ni cortarlo en pantalla."""
    for tam in range(66, 27, -2):
        fuente = font(tam, True)
        lineas = wrap_text(draw, texto.upper(), fuente, ancho)
        if not lineas or len(lineas) > max_lineas:
            continue
        cajas = [draw.textbbox((0, 0), lin, font=fuente, stroke_width=1) for lin in lineas]
        if any((b[2] - b[0]) > ancho for b in cajas):
            continue
        salto = tam + 17
        alto = len(lineas) * salto
        if alto > 320:
            continue
        y = centro_y - alto // 2
        for linea in lineas:
            caja = draw.textbbox((0, 0), linea, font=fuente, stroke_width=1)
            x = (720 - (caja[2] - caja[0])) / 2
            draw.text((x, y), linea, font=fuente, fill=(255,255,255),
                      stroke_width=1, stroke_fill=(4,7,22))
            y += salto
        return
    raise ValueError('El micromensaje no cabe en la zona segura sin recortes')


OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'


def _free_price(value):
    try:
        return float(value) == 0.0
    except (TypeError, ValueError, OverflowError):
        return False


def select_free_json_models(key, count=5):
    """Selecciona modelos de texto gratuitos; response_format es OPCIONAL.

    El listado de parámetros es informativo: el proveedor concreto puede no
    aceptar json_schema, por lo que se utiliza un segundo modo sin restricciones.
    """
    response = requests.get(OPENROUTER_MODELS_URL,
                            headers={'Authorization': f'Bearer {key}'}, timeout=30)
    response.raise_for_status()
    items = response.json().get('data', [])
    candidates = []
    forbidden = ('safety', 'moderation', 'guard', 'omni', 'embedding',
                 'audio', 'speech', 'image', 'reasoning', 'vision-only')
    for item in items:
        mid = item.get('id', '')
        if not isinstance(mid, str) or not mid.endswith(':free'):
            continue
        price = item.get('pricing') or {}
        if not (_free_price(price.get('prompt')) and _free_price(price.get('completion'))):
            continue
        description = (mid + ' ' + str(item.get('name', ''))).lower()
        if any(term in description for term in forbidden):
            continue
        context = item.get('context_length') or 0
        if not isinstance(context, int) or context < 4000:
            continue
        params = item.get('supported_parameters') or []
        can_format = 'response_format' in params
        # Preferir modelos de instrucciones conocidos, no modelos de razonamiento.
        familiar = any(term in description for term in ('instruct', 'chat', 'qwen', 'llama', 'mistral', 'gemma'))
        candidates.append((0 if familiar else 1, 0 if can_format else 1, mid, can_format))
    candidates.sort()
    # La clave de usuario nunca debe habilitar automáticamente un modelo pagado.
    if OPENROUTER_MODEL != 'openrouter/free':
        selected = [x for x in candidates if x[2] == OPENROUTER_MODEL]
        if not selected:
            raise RuntimeError('Modelo configurado sin cuota gratuita de texto: ' + OPENROUTER_MODEL)
        candidates = selected + [x for x in candidates if x[2] != OPENROUTER_MODEL]
    if not candidates:
        raise RuntimeError('No hay modelos gratuitos de texto en el catálogo de OpenRouter.')
    return [(item[2], item[3]) for item in candidates[:count]]


def _normalize_ai_fields(data):
    """Valida contenido, sin inventar ni reconstruir un JSON truncado."""
    if not isinstance(data, dict):
        raise ValueError('La IA no devolvió un objeto JSON')
    # No exigir metadatos que no afectan al relato; reducir tokens de salida.
    if not data.get('fact') and data.get('lesson'):
        data['fact'] = data['lesson']
    if not data.get('lesson') and data.get('fact'):
        data['lesson'] = data['fact']
    for field in ('title', 'script', 'lesson', 'fact'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError('Falta ' + field)
    words = len(data['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'Guion de {words} palabras; requiere entre 30 y 60')
    visuals = data.get('visuals')
    if not isinstance(visuals, list) or len(visuals) != 5 or not all(isinstance(v, str) and v.strip() for v in visuals):
        raise ValueError('Deben existir cinco frases visuales')
    # Rechazar frases genéricas o incompletas; no truncar conceptos.
    data['visuals'] = validar_microfrases(visuals, data['script'], data['title'],
                                          data['fact'], data['lesson'])
    if not isinstance(data.get('sources'), list):
        data['sources'] = []
    return data


def classify_openrouter_429(response):
    """Distingue saturación del proveedor y cuota global sin asumir que todo 429 es global.

    Devuelve 'provider', 'account' o 'unknown'. Nunca imprime credenciales.
    """
    try:
        body = response.json()
    except (ValueError, TypeError):
        body = {}
    error = body.get('error') if isinstance(body, dict) else None
    if not isinstance(error, dict):
        error = {}
    meta = error.get('metadata')
    if not isinstance(meta, dict):
        meta = {}
    details = ' '.join(str(x) for x in (
        error.get('message', ''), meta.get('raw', ''),
        meta.get('provider_name', ''), meta.get('reason', ''),
    )).lower()
    provider_clues = (
        'temporarily rate-limited upstream', 'rate-limited upstream',
        'upstream', 'provider returned error', 'provider rate limit',
        'provider rate-limit', 'provider is rate limited',
    )
    if any(phrase in details for phrase in provider_clues):
        return 'provider'
    account_clues = (
        'free-models-per-day', 'free model requests per day',
        'daily free requests', 'daily limit', 'daily quota',
        'insufficient credits', 'not enough credits',
        'account rate limit', 'your account', 'your quota',
    )
    if any(phrase in details for phrase in account_clues):
        return 'account'
    return 'unknown'


def _parse_compact_response(text):
    """Acepta JSON compacto o seis líneas delimitadas, sin inventar campos."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Respuesta vacía')
    try:
        return _parse_ai_json(text)
    except (ValueError, json.JSONDecodeError):
        pass
    # Formato alternativo; el guion y cada escena ocupan exactamente una línea.
    cleaned = re.sub(r'^```[^\n]*\n|\n```\s*$', '', text.strip())
    fields = {}
    scenes = {}
    for line in cleaned.splitlines():
        hit = re.match(r'^\s*(TITLE|TITULO|SCRIPT|GUION|LESSON|LECCION|FACT|DATO|MENSAJE_[1-5])\s*:\s*(.*?)\s*$', line, re.I)
        if not hit:
            if line.strip():
                raise ValueError('Línea no reconocida fuera del formato delimitado')
            continue
        key, value = hit.group(1).upper(), hit.group(2).strip()
        if not value:
            raise ValueError('Campo sin contenido: ' + key)
        if key.startswith('MENSAJE_'):
            scenes[int(key[-1])] = value
        elif key in ('TITLE', 'TITULO'):
            fields['title'] = value
        elif key in ('SCRIPT', 'GUION'):
            fields['script'] = value
        elif key in ('LESSON', 'LECCION'):
            fields['lesson'] = value
        elif key in ('FACT', 'DATO'):
            fields['fact'] = value
    if len(scenes) != 5:
        raise ValueError('Formato delimitado: faltan micromensajes')
    fields['visuals'] = [scenes[n] for n in range(1, 6)]
    fields['sources'] = []
    return fields


def _free_prompt(ep, mode):
    content = (
        'Tema: ' + str(ep.get('title', ''))[:180] + '. '
        'Categoría: ' + str(ep.get('category', ''))[:90] + '. '
        'Aprendizaje: ' + str(ep.get('lesson', ''))[:210] + '. '
    )
    instruction = (
        'Eres divulgador aeronáutico riguroso en español. Público: pilotos, mecánicos, despachadores, ATC y personal aeroportuario. No inventes especificaciones, magnitudes, procedimientos ni normas. Si faltan datos exactos, explica el principio verificable. Las recomendaciones de seguridad no reemplazan manuales aprobados.  Crea UN guion de 42 a 50 palabras '
        'que explique un hecho concreto sin inventar cifras. Escribe cinco '
        'microfrases de 3 a 9 palabras y máximo 52 caracteres cada una, '
        'específicas y relacionadas con las afirmaciones del guion, no títulos '
        'vacíos. Una idea completa por frase; nada de cortes o puntos suspensivos. '
        'Las cinco frases siguen el relato. Evita consejos médicos o de emergencia '
        'sin corroborar. Salida breve, sin explicaciones ni Markdown. '
    )
    if mode == 'lines':
        instruction += (
            'Emite exactamente estas nueve líneas con estas etiquetas: '
            'TITULO: ...\nGUION: ...\nDATO: ...\nLECCION: ...\n'
            'MENSAJE_1: ...\nMENSAJE_2: ...\nMENSAJE_3: ...\n'
            'MENSAJE_4: ...\nMENSAJE_5: ... . '
            'No agregues otras líneas.'
        )
    else:
        instruction += (
            'Devuelve SOLO JSON compacto con claves title, script, fact, lesson, '
            'visuals (array de cinco cadenas). Sin sources ni campos extra.'
        )
    return instruction + ' ' + content


def _openrouter_text(key, model, prompt, *, max_tokens=2600):
    """Obtiene texto visible sin perder una respuesta útil por finish_reason=length.

    Desactiva el razonamiento cuando lo admite el proveedor: algunos modelos
    gratuitos consumen su presupuesto en tokens internos. Ante 400 por un
    parámetro no soportado, reintenta la MISMA solicitud sin él.
    """
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'Dato Wow - AeroDatos',
    }
    base = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'Español. Entrega únicamente las líneas solicitadas. No expliques ni razones.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
        'max_tokens': max_tokens,
        'stream': False,
    }
    payload = dict(base)
    payload['reasoning'] = {'effort': 'none', 'exclude': True}
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=130)
    # Los modelos gratuitos no comparten todos los parámetros de razonamiento.
    if response.status_code in (400, 422) and any(
        word in response.text.lower() for word in ('reasoning', 'effort', 'unsupported parameter', 'unrecognized')
    ):
        response = requests.post(OPENROUTER_URL, headers=headers, json=base, timeout=130)
    if response.status_code == 429:
        kind = classify_openrouter_429(response)
        if kind == 'account':
            raise RuntimeError('Cuota gratuita de la cuenta OpenRouter agotada')
        raise ValueError(f'HTTP 429 ({kind}): modelo temporalmente saturado')
    if response.status_code in (401, 403):
        raise RuntimeError('OpenRouter rechazó la credencial o el acceso a la API')
    if not response.ok:
        raise ValueError(f'HTTP {response.status_code}: {response.text[:170]}')
    body = response.json()
    choice = (body.get('choices') or [{}])[0]
    finish = choice.get('finish_reason')
    message = choice.get('message') or {}
    content = message.get('content') or ''
    if isinstance(content, list):
        content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))
    if not isinstance(content, str) or not content.strip():
        reason = 'respuesta truncada: el modelo consumió todos los tokens sin texto visible' if finish == 'length' else 'modelo sin texto visible'
        raise ValueError(reason)
    # finish_reason=length no implica automáticamente que el contenido esté
    # incompleto. El analizador de cada etapa es quien valida su integridad.
    return content.strip()


def _parse_narration(raw):
    """Acepta un objeto JSON corto o líneas TITLE/SCRIPT/FACT/LESSON."""
    try:
        obj = _parse_ai_json(raw)
    except (ValueError, json.JSONDecodeError):
        obj = {}
        for line in raw.strip().strip('`').splitlines():
            hit = re.match(r'^\s*(TITULO|TITLE|GUION|SCRIPT|DATO|FACT|LECCION|LESSON)\s*:\s*(.+?)\s*$', line, re.I)
            if hit:
                key = {'TITULO':'title','TITLE':'title','GUION':'script','SCRIPT':'script',
                       'DATO':'fact','FACT':'fact','LECCION':'lesson','LESSON':'lesson'}[hit.group(1).upper()]
                obj[key] = hit.group(2).strip()
    if not isinstance(obj, dict):
        raise ValueError('narración no estructurada')
    for field in ('title','script'):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError(f'falta {field}')
    obj['fact'] = str(obj.get('fact') or obj.get('lesson') or obj['title']).strip()
    obj['lesson'] = str(obj.get('lesson') or obj.get('fact') or obj['title']).strip()
    words = len(obj['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'guion de {words} palabras, se requieren 30-60')
    return obj


def _parse_five_visuals(raw):
    """Extrae cinco mensajes de un array JSON o cinco líneas numeradas."""
    try:
        obj = json.loads(raw.strip())
        if isinstance(obj, list):
            visuals = obj
        elif isinstance(obj, dict):
            visuals = obj.get('visuals') or obj.get('mensajes')
        else:
            visuals = None
        if isinstance(visuals, list):
            return visuals
    except json.JSONDecodeError:
        pass
    found = {}
    for line in raw.splitlines():
        hit = re.match(r'^\s*(?:MENSAJE[_ ]?|ESCENA[_ ]?|[\-]?)\s*([1-5])\s*[.):\-]\s*(.+?)\s*$', line, re.I)
        if hit:
            found[int(hit.group(1))] = hit.group(2).strip().strip('"')
    if len(found) != 5:
        raise ValueError('faltan cinco mensajes visuales')
    return [found[i] for i in range(1,6)]


def _proposiciones_breves(texto):
    """Extrae proposiciones literales completas; jamás trunca por caracteres.

    Se separan oraciones y cláusulas explícitas. Un fragmento solamente sirve
    si satisface todas las reglas del validador final.
    """
    texto = re.sub(r'\s+', ' ', str(texto or '')).strip()
    for frase in re.split(r'(?<=[.!?;])\s+|\s*[;:]\s*', texto):
        for parte in re.split(r',\s+(?=(?:pero|aunque|además|sin embargo|por eso|mientras)\b)', frase, flags=re.I):
            parte = parte.strip(' \t\n.,;:¡!¿?"“”')
            parte = re.sub(r'^(?:pero|aunque|además|sin embargo|por eso),?\s+', '', parte, flags=re.I)
            if parte and VISUAL_MIN_WORDS <= len(parte.split()) <= VISUAL_MAX_WORDS and len(parte) <= VISUAL_MAX_CHARS:
                yield parte


def _mensajes_parciales(raw):
    """Conserva líneas de mensajes aun si faltan campos o JSON se truncó."""
    resultados = []
    try:
        parsed = _parse_five_visuals(raw)
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, str)]
    except (ValueError, TypeError, KeyError):
        pass
    for linea in str(raw or '').splitlines():
        m = re.match(r'^\s*(?:MENSAJE[_ ]?|ESCENA[_ ]?|[-*]\s*)\s*([1-5])\s*[.):-]\s*(.+?)\s*$', linea, re.I)
        if m:
            resultados.append(m.group(2).strip().strip('"“”'))
    return resultados


def _recuperar_mensajes(narracion, respuestas=()):
    """Acumula frases válidas de TODOS los modelos y del propio guion.

    No se descarta una respuesta entera por una sola escena defectuosa.
    Respeta el orden aproximado del guion y conserva diversidad de mensajes.
    """
    vistos = set()
    candidatos = []
    universo = _palabras_relevantes(' '.join(str(narracion[k]) for k in ('script','title','fact','lesson')))

    def agregar(frase):
        if not isinstance(frase, str):
            return
        frase = re.sub(r'\s+', ' ', frase).strip().strip('"“”')
        clave = _visual_normalizado(frase).strip(' .!?¿¡')
        if not clave or clave in vistos:
            return
        if not VISUAL_MIN_WORDS <= len(frase.split()) <= VISUAL_MAX_WORDS:
            return
        if len(frase) > VISUAL_MAX_CHARS or frase.endswith(('...', '…', ':', ',', ';')):
            return
        if any(generic in clave for generic in GENERIC_VISUALS):
            return
        if not (_palabras_relevantes(frase) & universo):
            return
        vistos.add(clave)
        candidatos.append(frase)

    # Primero, material válido propuesto por los modelos aunque otra escena falle.
    for respuesta in respuestas:
        if isinstance(respuesta, list):
            for frase in respuesta:
                agregar(frase)
                if isinstance(frase, str):
                    for breve in _proposiciones_breves(frase):
                        agregar(breve)
    # Después, proposiciones literales del guion y sus afirmaciones asociadas.
    for campo in ('script', 'fact', 'lesson', 'title'):
        for breve in _proposiciones_breves(narracion[campo]):
            agregar(breve)

    if len(candidatos) < 5:
        raise ValueError(f'solo se recuperaron {len(candidatos)} mensajes válidos distintos (se requieren 5)')
    return validar_microfrases(candidatos[:5], narracion['script'],
                               narracion['title'], narracion['fact'], narracion['lesson'])


def _mensajes_locales_desde_guion(narration):
    """Respaldo extractivo, sin introducir afirmaciones que no estén en guion."""
    return _recuperar_mensajes(narration)


# Orden de proveedores configurable, sin nuevas dependencias.
# Las cuentas gratuitas están sujetas a cuotas propias; no se garantiza cuota infinita.
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GEMINI_API_ROOT = 'https://generativelanguage.googleapis.com/v1beta/models/'


def _provider_credentials():
    providers = []
    for name, secret in (('groq', 'GROQ_API_KEY'), ('gemini', 'GEMINI_API_KEY'),
                         ('openrouter', 'OPENROUTER_API_KEY')):
        key = os.getenv(secret, '').strip()
        if key:
            providers.append((name, key))
    if not providers:
        raise RuntimeError('Configura al menos una clave: GROQ_API_KEY, GEMINI_API_KEY u OPENROUTER_API_KEY')
    return providers


def _discover_groq_models(key):
    """Consulta el catálogo accesible para esta API key, sin suponer IDs vigentes."""
    preferred = ('openai/gpt-oss-20b', 'openai/gpt-oss-120b',
                 'llama-3.3-70b-versatile', 'llama-3.1-8b-instant')
    response = requests.get('https://api.groq.com/openai/v1/models',
                            headers={'Authorization': f'Bearer {key}'}, timeout=25)
    response.raise_for_status()
    available = {row.get('id') for row in response.json().get('data', [])
                 if isinstance(row, dict) and isinstance(row.get('id'), str)}
    chosen = os.getenv('GROQ_MODEL', '').strip()
    # Only general text generation models: avoid audio, guard, vision, or tooling.
    allowed = [mid for mid in preferred if mid in available]
    if chosen and chosen in available and chosen not in allowed:
        allowed.insert(0, chosen)
    elif chosen in allowed:
        allowed.remove(chosen)
        allowed.insert(0, chosen)
    return allowed[:3]


def _discover_gemini_models(key):
    """Lista modelos con generateContent y prioriza Flash-Lite (no TTS/imágenes)."""
    preferred = ('gemini-3.1-flash-lite', 'gemini-3.5-flash-lite',
                 'gemini-3.6-flash', 'gemini-3.8-flash')
    found = set()
    page = None
    for _ in range(5):
        params = {'pageSize': 100}
        if page:
            params['pageToken'] = page
        response = requests.get('https://generativelanguage.googleapis.com/v1beta/models',
                                headers={'x-goog-api-key': key}, params=params, timeout=25)
        response.raise_for_status()
        payload = response.json()
        for row in payload.get('models', []):
            if 'generateContent' in row.get('supportedGenerationMethods', []):
                name = str(row.get('name', '')).removeprefix('models/')
                if name:
                    found.add(name)
        page = payload.get('nextPageToken')
        if not page:
            break
    chosen = os.getenv('GEMINI_MODEL', '').strip().removeprefix('models/')
    allowed = [mid for mid in preferred if mid in found]
    if chosen and chosen in found and chosen not in allowed:
        allowed.insert(0, chosen)
    elif chosen in allowed:
        allowed.remove(chosen)
        allowed.insert(0, chosen)
    return allowed[:3]


def _ai_candidates():
    result = []
    for provider, key in _provider_credentials():
        if provider == 'groq':
            try:
                models = _discover_groq_models(key)
                result.extend((provider, model, key) for model in models)
                if not models:
                    print('Groq: sin modelos de texto compatibles accesibles con esta clave', flush=True)
            except (requests.RequestException, ValueError, KeyError) as exc:
                print(f'Groq: no se pudo consultar catálogo: {str(exc)[:160]}', flush=True)
        elif provider == 'gemini':
            try:
                models = _discover_gemini_models(key)
                result.extend((provider, model, key) for model in models)
                if not models:
                    print('Gemini: sin modelos Flash compatibles accesibles con esta clave', flush=True)
            except (requests.RequestException, ValueError, KeyError) as exc:
                print(f'Gemini: no se pudo consultar catálogo: {str(exc)[:160]}', flush=True)
        else:
            try:
                result.extend((provider, model, key) for model, _ in select_free_json_models(key, 5))
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                print(f'OpenRouter: no se pudieron listar modelos gratuitos: {exc}', flush=True)
    if not result:
        raise RuntimeError('Ningún proveedor ofrece modelos compatibles accesibles; revisa las claves y las cuotas.')
    return result


def _response_visible_text(response, provider):
    if response.status_code in (401, 403):
        raise ValueError(f'{provider}: clave o acceso rechazado (HTTP {response.status_code})')
    if response.status_code == 429:
        raise ValueError(f'{provider}: cuota o límite temporal (HTTP 429)')
    if not response.ok:
        raise ValueError(f'{provider}: HTTP {response.status_code}: {response.text[:200]}')
    data = response.json()
    if provider == 'gemini':
        choices = data.get('candidates') or []
        pieces = (choices[0].get('content') or {}).get('parts') or [] if choices else []
        output = ''.join(part.get('text','') for part in pieces if isinstance(part, dict))
    else:
        choices = data.get('choices') or []
        content = (choices[0].get('message') or {}).get('content', '') if choices else ''
        output = (''.join(x.get('text','') for x in content if isinstance(x,dict))
                  if isinstance(content,list) else content)
    if not isinstance(output,str) or not output.strip():
        raise ValueError(f'{provider}: respuesta sin texto visible')
    return output.strip()


def _provider_text(provider, model, key, prompt, *, max_tokens=1500):
    if provider == 'openrouter':
        try:
            return _openrouter_text(key, model, prompt, max_tokens=max_tokens)
        except RuntimeError as exc:
            # Agotamiento de cuota: registrar el fallo, no abortar los otros proveedores.
            if 'cuota gratuita' in str(exc).lower():
                raise ValueError(str(exc)) from exc
            raise
    if provider == 'groq':
        response = requests.post(
            GROQ_URL,
            headers={'Authorization': f'Bearer {key}', 'Content-Type':'application/json'},
            json={'model':model, 'messages':[
                {'role':'system', 'content':'Responde exclusivamente en español y con el formato pedido.'},
                {'role':'user','content':prompt}],
                'temperature':0.2, 'max_tokens':min(max_tokens, 2048)},
            timeout=110)
        return _response_visible_text(response, provider)
    if provider == 'gemini':
        response = requests.post(
            GEMINI_API_ROOT + urllib.parse.quote(model, safe='') + ':generateContent',
            headers={'x-goog-api-key':key,'Content-Type':'application/json'},
            json={'contents':[{'parts':[{'text':prompt}]}],
                  'generationConfig':{'maxOutputTokens':min(max_tokens,2048)}},
            timeout=110)
        return _response_visible_text(response, provider)
    raise ValueError(f'Proveedor desconocido: {provider}')


def create_ai_episode(ep):
    """Dos etapas cortas: narración, después cinco mensajes visuales.

    Evita pedir un gran JSON. Solo usa modelos con prompt/completion gratuitos;
    si alguno falla por saturación o salida truncada prueba el siguiente.
    """
    candidates = _ai_candidates()
    print('Proveedores disponibles: ' + ', '.join(f'{p}:{m}' for p,m,_ in candidates), flush=True)
    intro = (
        f"Tema: {str(ep.get('title', ''))[:140]}. "
        f"Categoría: {str(ep.get('category', ''))[:70]}. "
        f"Enseñanza deseada: {str(ep.get('lesson', ''))[:160]}."
    )
    narration_prompt = (
        'Eres especialista en divulgación aeronáutica para pilotos, mantenimiento, ATC y operaciones. Redacta un guion técnico sorprendente pero preciso, IDEALMENTE 42 A 50 PALABRAS '
        'en español para narrar en 20 segundos. Escribe de cuatro a seis oraciones completas ' 
        'con ideas concretas; deben avanzar de causa a conclusión y ser comprensibles ' 
        'por sí solas. Sin cifras inventadas, sin introducciones vacías, '
        'sin especificaciones inventadas, sin instrucciones operacionales no verificadas, sin afirmar cifras sin condiciones ni fuente. Responde SOLO cuatro líneas, '
        'sin Markdown: TITULO: ...\nGUION: ...\nDATO: ...\nLECCION: ...\n' + intro
    )
    narration = None
    narration_model = None
    last_problem = 'sin respuesta'
    providers_exhausted = set()
    for provider, model, key in candidates:
        if provider in providers_exhausted:
            continue
        try:
            raw = _provider_text(provider, model, key, narration_prompt, max_tokens=1500)
            narration = _parse_narration(raw)
            narration_model = f'{provider}:{model}'
            print(f'Narración validada con {narration_model}', flush=True)
            break
        except RuntimeError:
            raise
        except (ValueError, requests.RequestException, KeyError, TypeError) as exc:
            last_problem = f'{provider}/{model}: {str(exc)[:140]}'
            print(f'IA etapa 1: {last_problem}', flush=True)
            if provider == 'openrouter' and 'cuota gratuita' in str(exc).lower():
                providers_exhausted.add(provider)
    if narration is None:
        raise RuntimeError('Ningún proveedor configurado generó narración válida. '
                           f'Último diagnóstico: {last_problem}. No se publicó nada.')

    # No volver a generar el guion cuando fallan los mensajes visuales.
    visuals_prompt = (
        'Basándote ÚNICAMENTE en el guion siguiente, escribe cinco frases educativas '
        'completas para cinco escenas consecutivas. Idealmente 3 a 9 palabras, '
        'máximo 72 caracteres y nunca más de 12 palabras, sin títulos vacíos, sin puntos suspensivos, sin introducir '
        'hechos ajenos al guion. Deben explicar cinco aspectos o consecuencias distintas. '
        'Responde SOLO estas cinco líneas, sin Markdown ni explicaciones: '
        'MENSAJE_1: ...\nMENSAJE_2: ...\nMENSAJE_3: ...\nMENSAJE_4: ...\nMENSAJE_5: ...\n'
        f"TITULO: {narration['title']}\nGUION: {narration['script']}\n"
        f"DATO: {narration['fact']}\nLECCION: {narration['lesson']}"
    )
    visuals = None
    visual_model = None
    propuestas_parciales = []
    # Antes de otra solicitud, no hay parámetro costoso de razonamiento forzado:
    # muchos proveedores gratuitos no lo admiten; los prompts cortos reducen consumo.
    # El modelo que completó bien la narración recibe la primera oportunidad.
    visual_candidates = sorted(candidates, key=lambda row: f'{row[0]}:{row[1]}' != narration_model)
    for provider, model, key in visual_candidates:
        try:
            raw = _provider_text(provider, model, key, visuals_prompt, max_tokens=1100)
            propuestas_parciales.append(_mensajes_parciales(raw))
            proposed = _parse_five_visuals(raw)
            visuals = validar_microfrases(proposed, narration['script'],
                                           narration['title'], narration['fact'], narration['lesson'])
            visual_model = f'{provider}:{model}'
            print(f'Cinco mensajes validados con {visual_model}', flush=True)
            break
        except RuntimeError:
            raise
        except (ValueError, requests.RequestException, KeyError, TypeError) as exc:
            last_problem = f'{provider}/{model}: {str(exc)[:140]}'
            print(f'IA etapa 2: {last_problem}', flush=True)
    if visuals is None:
        # Evitar fallar por una segunda llamada cuando el propio guion
        # contiene cinco proposiciones breves. Nunca inventar información.
        try:
            visuals = _recuperar_mensajes(narration, propuestas_parciales)
            visual_model = 'recuperacion-local'
            print('Cinco mensajes recuperados de propuestas parciales y del guion', flush=True)
        except ValueError as exc:
            raise RuntimeError(
                'Narración válida, pero no se obtuvieron cinco mensajes seguros. '
                f'IA: {last_problem}. Respaldo local: {exc}. '
                'No se publicó nada.'
            ) from exc

    result = dict(ep)
    result.update(
        title=narration['title'], script=narration['script'],
        fact=narration['fact'], lesson=narration['lesson'],
        visuals=visuals, visual_title=visuals[0], visual_lesson=visuals[-1],
        source='', suggested_sources=[], ai_model=narration_model,
        visual_ai_model=visual_model, generated_at=now(), verified=False,
        verification_note='Contenido generado con IA, no verificado independientemente',
    )
    print(f"Guion IA creado: {ep['id']}; textos cortos: 5; fuentes propuestas: ninguna", flush=True)
    return result

def select_episode(episodes, gh=None, requested=None):
    """Selecciona un episodio pendiente con variedad de categorias y azar real.

    - Un ID explicito respeta la eleccion manual (publish() aplica antidualidad).
    - El historial remoto impide reutilizar publicaciones o envios inciertos.
    - Entre categorias con episodios disponibles, prioriza las menos publicadas;
      entre empates evita la ultima categoria usada, si existe alternativa.
    - Sortea tanto la categoria como el episodio usando SystemRandom.
    No altera el schema ni la ubicacion del estado previo.
    """
    if requested:
        return next((e for e in episodes if e['id'] == requested), None)

    states = {}
    if gh is not None:
        raw, _ = gh.read('aerodatos/state.json')
        if raw is not None:
            document = json.loads(raw)
            if not isinstance(document, dict) or not isinstance(document.get('episodes'), dict):
                raise RuntimeError('Estado remoto de AeroDatos invalido; no se seleccionara episodio')
            states = document['episodes']

    blocked = {'publicado', 'enviando', 'incierto'}
    by_category = {}
    published_counts = {}
    recent = []
    for ep in episodes:
        category = ep['category']
        row = states.get(ep['id'], {})
        if not isinstance(row, dict):
            raise RuntimeError('Registro de estado invalido para ' + ep['id'])
        statuses = [row.get(field) for field in ('reel', 'foto', 'feed_video')]
        if any(status in blocked for status in statuses):
            if 'publicado' in statuses:
                published_counts[category] = published_counts.get(category, 0) + 1
                if row.get('updated_at'):
                    recent.append((str(row['updated_at']), category))
            continue
        by_category.setdefault(category, []).append(ep)
        published_counts.setdefault(category, 0)

    if not by_category:
        raise RuntimeError('Los 500 episodios ya estan publicados o bloqueados por incertidumbre')

    # Equilibrio entre categorias; no completar cien episodios de una sola.
    minimum = min(published_counts[category] for category in by_category)
    eligible_categories = [category for category in by_category
                           if published_counts[category] == minimum]
    if recent and len(eligible_categories) > 1:
        last_category = max(recent, key=lambda pair: pair[0])[1]
        others = [category for category in eligible_categories if category != last_category]
        if others:
            eligible_categories = others

    rng = random.SystemRandom()
    chosen_category = rng.choice(eligible_categories)
    selected = rng.choice(by_category[chosen_category])
    print(f'Episodio aleatorio equilibrado: {selected["id"]} | '
          f'categoria: {chosen_category} | '
          f'publicados de esa categoria: {published_counts[chosen_category]}', flush=True)
    return selected


def now():
    return datetime.now(timezone.utc).isoformat()


def font(size, bold=False):
    filenames = (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                  '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'] if bold else
                 ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                  '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'])
    for filename in filenames:
        if Path(filename).exists():
            return ImageFont.truetype(filename, size)
    return ImageFont.load_default()


def wrap_text(draw, text, text_font, width):
    words = text.split()
    result, current = [], ''
    for word in words:
        trial = f'{current} {word}'.strip()
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= width:
            current = trial
        else:
            if current:
                result.append(current)
            current = word
    if current:
        result.append(current)
    return result


def palette(i):
    return [(12, 12, 32), (9, 23, 38), (27, 15, 28), (14, 26, 25), (20, 17, 45)][i % 5], [
        (186, 93, 253), (39, 217, 241), (255, 193, 92), (69, 231, 169), (252, 105, 174)
    ][i % 5]



# Solo material CC0 o dominio público: no requiere crédito visible.
# No se descargan imágenes CC BY/CC BY-SA si no se va a publicar su atribución.
IMAGE_LICENSES = {'cc0', 'pdm'}

def _safe_photo_download(url, target):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname:
        return False
    try:
        r = requests.get(url, timeout=16, headers={'User-Agent': 'AeroDatosBot/1.0 (educational-content; Wikimedia/Openverse)'}, stream=True)
        r.raise_for_status()
        kind = r.headers.get('Content-Type', '').lower()
        if 'image/' not in kind or any(x in kind for x in ('svg', 'gif')):
            return False
        payload = bytearray()
        for chunk in r.iter_content(65536):
            payload.extend(chunk)
            if len(payload) > 8_000_000:
                return False
        from PIL import ImageOps
        with Image.open(io.BytesIO(payload)) as image:
            image = ImageOps.exif_transpose(image)
            if image.width < 500 or image.height < 350:
                return False
            image.convert('RGB').save(target, 'JPEG', quality=86)
        return True
    except Exception as exc:
        print(f'Imagen descartada: {type(exc).__name__}: {str(exc)[:100]}', flush=True)
        return False


def _strip_html(value):
    return re.sub(r'<[^>]*>', '', str(value or '')).strip()


def _commons_candidates(query):
    params = {'action':'query','format':'json','generator':'search',
              'gsrsearch': 'filetype:bitmap ' + query, 'gsrnamespace':6,'gsrlimit':8,
              'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1100}
    r = requests.get('https://commons.wikimedia.org/w/api.php', params=params, timeout=20,
                     headers={'User-Agent':'AeroDatosBot/1.0 (automatic educational video; contact via repository)'})
    r.raise_for_status()
    for page in r.json().get('query',{}).get('pages',{}).values():
        info = (page.get('imageinfo') or [{}])[0]
        meta = info.get('extmetadata') or {}
        lic = _strip_html((meta.get('LicenseShortName') or {}).get('value','')).lower().replace(' ', '')
        # Wikimedia utiliza variantes para CC0, marca de dominio público y PD.
        # Ante cualquier ambigüedad se descarta la imagen, nunca se presume libre.
        free_of_attribution = (
            'cc0' in lic or 'publicdomain' in lic or
            lic in ('pd', 'pdm', 'dominiopúblico', 'dominiopublico') or
            lic.startswith('pd-')
        )
        if not free_of_attribution or any(x in lic for x in ('cc-by', '-nc', '-nd')):
            continue
        url = info.get('thumburl') or info.get('url')
        if not url:
            continue
        yield {'url':url,'title':page.get('title',''),'author':_strip_html((meta.get('Artist') or {}).get('value','')),
               'license':lic,'source':info.get('descriptionurl','')}


def _openverse_candidates(query):
    r=requests.get('https://api.openverse.org/v1/images/',
                   params={'q':query,'license':'cc0,pdm','page_size':8},
                   timeout=18, headers={'User-Agent':'AeroDatosBot/1.0'})
    r.raise_for_status()
    for item in r.json().get('results',[]):
        lic=str(item.get('license') or '').lower()
        if lic not in IMAGE_LICENSES:
            continue
        url=item.get('thumbnail') or item.get('url')
        if url:
            yield {'url':url,'title':item.get('title',''),'author':item.get('creator',''),
                   'license':lic,'source':item.get('foreign_landing_url','')}


def prepare_photos(ep, folder):
    """Hasta cinco fotografías. Fallo de red/licencia => escenas animadas."""
    query = str(ep.get('image_query') or ep.get('title',''))[:100]
    # Las consultas con designación exacta no deben reemplazarse por otras máquinas.
    photos=[]; credits=[]; used=set()
    for backend in (_commons_candidates, _openverse_candidates):
        if len(photos)>=5:
            break
        try:
            for candidate in backend(query):
                if len(photos)>=5:
                    break
                url=candidate['url']
                if url in used:
                    continue
                used.add(url)
                title=(str(candidate.get('title',''))+' '+str(candidate.get('source',''))).lower()
                # Si el tema menciona una designación concreta, exigir coincidencia de nombre.
                models=re.findall(r'\b(?:CFM56(?:-5B)?|PW1100G|GEnx|GE90|CF34|PT6A|A320|747|787|Trent\s*(?:1000|XWB)|LEAP-1A|Concorde)\b',query,re.I)
                if models and not all(x.lower().replace(' ','') in title.replace(' ','') for x in models):
                    continue
                path=folder/f'foto_{len(photos)}.jpg'
                if _safe_photo_download(url,path):
                    photos.append(path); credits.append(candidate)
        except Exception as exc:
            print(f'Fuente fotográfica no disponible: {type(exc).__name__}: {str(exc)[:120]}', flush=True)
    (folder/'creditos_imagenes.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2),encoding='utf-8')
    return photos,credits


def _photo_background(image_path, w=720, h=1280):
    from PIL import ImageOps, ImageEnhance
    with Image.open(image_path) as raw:
        base=ImageOps.fit(raw.convert('RGB'),(w,h),method=Image.Resampling.LANCZOS)
        base=ImageEnhance.Brightness(base).enhance(0.48)
        return base


def scene(ep, number, dest, photo=None):
    W, H = 720, 1280
    bg, accent = palette(number + int(ep['id'][-3:]))
    img = _photo_background(photo, W, H) if photo else Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img, 'RGBA')
    rng = random.Random(ep['id'] + str(number))
    for _ in range(8 if photo else 22):
        x, y = rng.randrange(-150, 800), rng.randrange(-150, 1400)
        r = rng.randrange(15, 145)
        d.ellipse((x-r, y-r, x+r, y+r), outline=(*accent, rng.randrange(22, 90)), width=rng.randrange(2, 8))
    d.rounded_rectangle((52, 72, 668, 152), 24, fill=(255, 255, 255, 18), outline=(*accent, 200), width=3)
    d.text((77, 91), 'AERO_DATOS', font=font(33, True), fill=(255, 255, 255))
    d.text((55, 187), ep['category'].upper(), font=font(19, True), fill=accent)
    # Zona segura central: sin párrafos de narración ni frases truncadas.
    titulares = microfrases(ep)
    texto_centrado_seguro(d, titulares[number], centro_y=610, ancho=560, max_lineas=3)
    d.line((58, 1128, 662, 1128), fill=accent, width=5)
    d.text((92, 1154), 'aero datos - conocimiento en 20 segundos', font=font(21, True), fill='white')
    img.save(dest, quality=92)


def ambient(path: Path, seconds=20):
    rate = 16000
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        import array
        buff = array.array('h')
        for i in range(rate*seconds):
            t = i/rate
            f = min(1., t/.8, (seconds-t)/1.3)
            v = (math.sin(2*math.pi*110*t)*.17 + math.sin(2*math.pi*164.81*t)*.07 +
                 math.sin(2*math.pi*220*t)*.05)
            buff.append(int(32767*max(0,f)*v))
        w.writeframes(buff.tobytes())


async def narrate(script: str, path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(script, voice=os.getenv('AERO_VOICE', 'es-ES-AlvaroNeural'), rate='+12%')
    await communicate.save(str(path))
    if not path.exists() or path.stat().st_size < 500:
        raise RuntimeError('No se generó una narración válida')


def render(ep, out: Path, require_voice=False):
    out.mkdir(parents=True, exist_ok=True)
    if not ep.get('script'):
        raise ValueError(f"{ep['id']}: propuesta sin guion; no se puede producir")
    # Las fuentes son metadatos opcionales; no bloquean video ni publicacion.
    if not ep.get('source'):
        print(f"AVISO: {ep['id']} sin fuentes propuestas; contenido no verificado independientemente.", flush=True)
    folder = out / ep['id']
    folder.mkdir(parents=True, exist_ok=True)
    photos, image_credits = prepare_photos(ep, folder)
    ep['image_credits'] = image_credits
    frames = []
    for i in range(5):
        path = folder / f'escena_{i}.jpg'
        scene(ep, i, path, photos[i % len(photos)] if photos else None)
        frames.append(path)
    cover = out / f"{ep['id']}.jpg"
    cover.write_bytes(frames[0].read_bytes())
    ambient_path = folder / 'ambient.wav'
    ambient(ambient_path)
    narration = folder / 'voz.mp3'
    try:
        asyncio.run(narrate(ep['script'], narration))
    except Exception as exc:
        if require_voice:
            raise RuntimeError(f'Narración obligatoria falló: {exc}') from exc
        print(f'AVISO: preview sin voz por: {exc}', file=sys.stderr)
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for frame in frames:
        args += ['-loop', '1', '-framerate', '12', '-t', '4', '-i', str(frame)]
    args += ['-i', str(ambient_path)]
    voice_available = narration.exists() and narration.stat().st_size > 500
    if voice_available:
        args += ['-i', str(narration)]
    video_filters = ''.join(f'[{i}:v]fps=12,scale=720:1280,setsar=1[v{i}];' for i in range(5))
    video_filters += ''.join(f'[v{i}]' for i in range(5)) + 'concat=n=5:v=1:a=0[v];'
    if voice_available:
        video_filters += '[5:a]volume=0.28[amb];[6:a]volume=1.4[voice];[amb][voice]amix=inputs=2:duration=first:dropout_transition=0[a]'
    else:
        video_filters += '[5:a]volume=0.5[a]'
    movie = out / f"{ep['id']}.mp4"
    args += ['-filter_complex', video_filters, '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast',
             '-crf', '24', '-r', '30', '-c:a', 'aac', '-b:a', '128k',
             '-t', '20', '-movflags', '+faststart', str(movie)]
    subprocess.run(args, check=True, timeout=240)
    print(f'Video: {movie} ({movie.stat().st_size:,} bytes)')
    print(f'Portada: {cover}')
    return movie, cover


class Github:
    def __init__(self):
        self.repo = os.environ['GITHUB_REPOSITORY']
        self.token = os.environ['GH_TOKEN']
        self.base = f'https://api.github.com/repos/{self.repo}'
        self.branch = os.getenv('GITHUB_REF_NAME', 'main')
        self.s = requests.Session()
        self.s.headers.update({'Authorization': f'Bearer {self.token}',
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2022-11-28'})

    def request(self, method, route, **kwargs):
        r = self.s.request(method, self.base + route, timeout=40, **kwargs)
        if r.status_code >= 400:
            raise RuntimeError(f'GitHub API HTTP {r.status_code}: {r.text[:600]}')
        return r.json()

    def read(self, path):
        route = '/contents/' + urllib.parse.quote(path, safe='/')
        r = self.s.get(self.base + route, params={'ref': self.branch}, timeout=40)
        if r.status_code == 404:
            return None, None
        if r.status_code >= 400:
            raise RuntimeError(f'Lectura GitHub falló HTTP {r.status_code}')
        data = r.json()
        return base64.b64decode(data['content']), data['sha']

    def write(self, path, content: bytes, previous_sha=None):
        payload = {'message': f'AeroDatos: {path}', 'branch': self.branch,
                   'content': base64.b64encode(content).decode()}
        if previous_sha:
            payload['sha'] = previous_sha
        route = '/contents/' + urllib.parse.quote(path, safe='/')
        return self.request('PUT', route, json=payload)

    def assert_public(self):
        if self.request('GET', '').get('private') is not False:
            raise RuntimeError('Para Instagram, el repositorio que aloja el MP4 debe ser público')


def ig_api(method, path, *, token, **kwargs):
    url = f'https://graph.instagram.com/{GRAPH_VERSION}/{path}'
    data = dict(kwargs.pop('data', {}) or {})
    data['access_token'] = token
    if method == 'GET':
        r = requests.get(url, params=data, timeout=50)
    else:
        r = requests.post(url, data=data, timeout=60)
    try:
        obj = r.json()
    except ValueError:
        raise RuntimeError(f'Instagram HTTP {r.status_code} respuesta no JSON')
    if not r.ok or obj.get('error'):
        raise RuntimeError(f'Instagram HTTP {r.status_code}: {obj.get("error", obj)}')
    return obj


def publish_container(user_id, token, video_url, caption):
    """Publica una sola vez el MP4 como Reel visible también en el feed.

    La API expone el mismo video en la pestaña Reels y la cuadrícula/feed,
    sin crear una segunda publicación ni enviar ninguna imagen.
    """
    fields = {'caption': caption, 'media_type': 'REELS',
              'video_url': video_url, 'share_to_feed': 'true'}
    container = ig_api('POST', f'{user_id}/media', token=token, data=fields)['id']
    for _ in range(30):
        time.sleep(10)
        status = ig_api('GET', container, token=token, data={'fields': 'status_code,status'})
        if status.get('status_code') == 'FINISHED':
            break
        if status.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f'Contenedor Instagram {container}: {status}')
    else:
        raise RuntimeError(f'Timeout contenedor IG {container}; NO reintentar sin reconciliar')
    return ig_api('POST', f'{user_id}/media_publish', token=token,
                  data={'creation_id': container})['id']


def publish_story_container(user_id, token, video_url):
    """Crea una Story de video independiente mediante Instagram Login API.

    No incluye caption ni share_to_feed: esos campos son del Reel.
    Un fallo tras media_publish puede ser ambiguo; el estado remoto se deja
    en 'incierto' para impedir una duplicación accidental.
    """
    fields = {'media_type': 'STORIES', 'video_url': video_url}
    container = ig_api('POST', f'{user_id}/media', token=token, data=fields)['id']
    for _ in range(30):
        time.sleep(10)
        status = ig_api('GET', container, token=token,
                        data={'fields': 'status_code,status'})
        if status.get('status_code') == 'FINISHED':
            break
        if status.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f'Contenedor Story Instagram {container}: {status}')
    else:
        raise RuntimeError(f'Timeout contenedor Story IG {container}; reconciliar antes de reintentar')
    return ig_api('POST', f'{user_id}/media_publish', token=token,
                  data={'creation_id': container})['id']



def upload_video_to_public_github(gh, movie: Path, episode_id: str):
    """Sube un MP4 con nombre inmutable, sin modificar el estado histórico.

    Evita el conflicto 409 si un nombre de carpeta ya existe como archivo.
    Solo cambia la carpeta de medios; el estado sigue en aerodatos/state.json.
    """
    movie_bytes = movie.read_bytes()
    digest = hashlib.sha256(movie_bytes).hexdigest()[:16]
    filename = f'{episode_id}-{digest}.mp4'
    # Nombres independientes del antiguo dataviral/media. Si un antecesor
    # de cualquiera es un archivo, probamos el siguiente directorio.
    roots = ('aerodatos_assets/media', 'aerodatos_video_assets/media',
             'aerodatos_public_videos/media')
    for root in roots:
        remote = f'{root}/{filename}'
        try:
            old, _ = gh.read(remote)
        except (KeyError, TypeError) as exc:
            # GitHub Contents responde distinto si la ruta ya es un directorio
            # u otro objeto; no convertir errores ambiguos en sobrescrituras.
            raise RuntimeError(f'No se pudo inspeccionar ruta GitHub {remote}: {exc}') from exc
        if old is not None:
            if old != movie_bytes:
                raise RuntimeError(f'Colisión: existe otro archivo en {remote}')
            commit = gh.request('GET', f'/commits/{gh.branch}')['sha']
            print(f'Video ya almacenado en GitHub: {remote}', flush=True)
            return remote, commit
        try:
            result = gh.write(remote, movie_bytes)
        except RuntimeError as exc:
            message = str(exc)
            if 'HTTP 409' in message and ('subdirectory' in message or 'file exists' in message):
                print(f'Aviso: conflicto de ruta de medios {remote}; probando alternativa.', flush=True)
                continue
            raise
        print(f'Video almacenado en GitHub: {remote}', flush=True)
        return remote, result['commit']['sha']
    raise RuntimeError('GitHub: todos los directorios alternativos de video chocan con archivos. '
                       'Revisar manualmente la estructura del repositorio; no se publicó en Instagram.')


def check_instagram_identity(token=None, user_id=None, expected=None):
    """Verifica en Meta el usuario e ID, sin publicar ni mostrar secretos."""
    token = token if token is not None else credential('INSTAGRAM_TOKEN', TEST_INSTAGRAM_TOKEN)
    user_id = str(user_id if user_id is not None else credential('INSTAGRAM_USER_ID', TEST_INSTAGRAM_USER_ID)).strip()
    expected = (expected if expected is not None else os.environ.get('IG_EXPECTED_USERNAME', '')).strip().lstrip('@').lower()
    if not expected:
        raise RuntimeError('Falta IG_EXPECTED_USERNAME en GitHub Actions')
    if not user_id.isdigit():
        raise RuntimeError('INSTAGRAM_USER_ID debe ser numérico')
    try:
        me = ig_api('GET', 'me', token=token, data={'fields': 'id,user_id,username'})
    except RuntimeError as exc:
        detail = str(exc).lower()
        unsupported = 'user_id' in detail and any(x in detail for x in
            ('nonexisting field', 'non-existing field', 'unknown field', 'field is not supported'))
        if not unsupported:
            raise
        me = ig_api('GET', 'me', token=token, data={'fields': 'id,username'})
    username = str(me.get('username', '')).strip().lstrip('@').lower()
    if username != expected:
        raise RuntimeError('TOKEN DE OTRA CUENTA: se esperaba @' + expected +
                           ' pero Meta autorizó @' + (username or 'desconocido') +
                           '. Reautoriza INSTAGRAM_TOKEN para @' + expected)
    ids = {str(me.get(k, '')).strip() for k in ('id', 'user_id') if str(me.get(k, '')).strip().isdigit()}
    if user_id not in ids:
        # Identificadores no se imprimen completos en logs públicos.
        safe = lambda v: ('…' + v[-4:]) if v else '(ausente)'
        raise RuntimeError('INSTAGRAM_USER_ID INCORRECTO para @' + expected +
            ': secret termina en ' + safe(user_id) +
            '; Meta devuelve id ' + safe(str(me.get('id',''))) +
            ' y user_id ' + safe(str(me.get('user_id',''))) +
            '. Corrige el secret usando el ID del mismo flujo Instagram Login. '
            'El video no se publicará con credenciales inconsistentes.')
    print('Instagram verificado: @' + username +
          '; identificador coincide con ' + ('user_id' if user_id == str(me.get('user_id','')) else 'id'),
          flush=True)
    return me


def publish(ep, movie, cover, approval):
    if approval != ep['id']:
        raise ValueError('Se exige aprobación explícita del mismo ID de episodio')
    if not ep.get('script'):
        raise ValueError('Publicación bloqueada: falta el guion narrado')
    if not ep.get('source'):
        print('AVISO: publicación sin enlaces de referencia; la IA no ha verificado los hechos.', flush=True)
    token = credential('INSTAGRAM_TOKEN', TEST_INSTAGRAM_TOKEN)
    user_id = credential('INSTAGRAM_USER_ID', TEST_INSTAGRAM_USER_ID)
    if not user_id.isdigit():
        raise ValueError('INSTAGRAM_USER_ID debe ser numérico')
    # La cuenta autorizada se define exclusivamente con variables de entorno.
    # Nunca escribir un usuario fijo en este archivo: la configuración vive en
    # GitHub Actions -> Settings -> Secrets and variables -> Actions -> Variables.
    expected = os.environ.get('IG_EXPECTED_USERNAME', '').strip().lstrip('@').lower()
    if not expected:
        raise RuntimeError('Falta IG_EXPECTED_USERNAME: define la variable de GitHub para publicar')
    check_instagram_identity(token, user_id, expected)
    gh = Github()
    gh.assert_public()
    path = 'aerodatos/state.json'
    raw, sha = gh.read(path)
    state = json.loads(raw) if raw is not None else {'schema':1,'episodes':{}}
    row = state['episodes'].get(ep['id'], {})
    if any(row.get(key) in ('enviando','incierto','publicado') for key in ('reel', 'foto', 'feed_video')):
        raise RuntimeError('Hay publicación previa o incierta: bloqueo anti-duplicados')
    def save():
        nonlocal sha
        result = gh.write(path, json.dumps(state,ensure_ascii=False,indent=2).encode(), sha)
        sha = result['content']['sha']
    # Subida de archivos a un repositorio público: URL estable de commit. El tamaño
    # máximo de GitHub Contents API es 100 MB; no es un CDN de producción.
    remote, commit = upload_video_to_public_github(gh, movie, ep['id'])
    video_url = f'https://raw.githubusercontent.com/{gh.repo}/{commit}/{remote}'
    response = requests.get(video_url, timeout=60)
    if not response.ok or len(response.content) != movie.stat().st_size:
        raise RuntimeError(f'MP4 no accesible públicamente: HTTP {response.status_code}')
    # La descripción desarrolla el contenido en lugar de mostrar autores de fotos.
    # Los datos se extraen exclusivamente del guion generado; no se inventan cifras.
    caption = f'{ep["title"]}\n\n{ep["script"].strip()}'
    fact = str(ep.get('fact') or '').strip()
    lesson = str(ep.get('lesson') or '').strip()
    if fact and fact.casefold() not in ep['script'].casefold():
        caption += f'\n\nDato clave: {fact}'
    if lesson and lesson.casefold() not in ep['script'].casefold():
        caption += f'\n\nPara recordar: {lesson}'
    if ep.get('source'):
        caption += f'\n\nReferencias sugeridas (no verificadas): {ep["source"]}'
    caption += '\n\n#AeroDatos #Aviacion #ConocimientoAeronautico'
    state['episodes'][ep['id']] = row
    row['reel'] = 'enviando'
    row['updated_at'] = now()
    save()
    try:
        published = publish_container(user_id, token, video_url, caption)
    except BaseException:
        row['reel'] = 'incierto'
        row['updated_at'] = now()
        try:
            save()
        except Exception as ex:
            print(f'ALERTA: sin persistencia de estado incierto: {ex}', file=sys.stderr)
        raise
    row['reel'] = 'publicado'
    row['share_to_feed'] = True
    row['reel_id'] = published
    row['video_url'] = video_url
    row['updated_at'] = now()
    save()
    print(f'Video publicado como Reel Y visible en el feed: {published}', flush=True)
    # Story independiente: nunca borrar ni degradar 'reel=publicado' si falla.
    # Guardar estado 'enviando' ANTES de llamar a Instagram y 'incierto' si
    # hubo error (incluye fallos cuya publicación pudo haber ocurrido).
    row['story'] = 'enviando'
    row['updated_at'] = now()
    save()
    try:
        story_id = publish_story_container(user_id, token, video_url)
    except BaseException:
        row['story'] = 'incierto'
        row['updated_at'] = now()
        try:
            save()
        except Exception as ex:
            print(f'ALERTA: sin persistencia del estado incierto Story: {ex}', file=sys.stderr)
        print('Reel publicado. Story incierta o fallida; NO se repetirá el Reel.', file=sys.stderr)
        raise
    row['story'] = 'publicado'
    row['story_id'] = story_id
    row['updated_at'] = now()
    save()
    print(f'Story publicada: {story_id}', flush=True)


def main():
    ap = argparse.ArgumentParser(description='AERO_DATOS: 500 ideas, IA OpenRouter Free y video Instagram')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--check-instagram', action='store_true', help='Verifica token, cuenta e ID sin generar video ni publicar')
    ap.add_argument('--episode', default='', help='ID concreto; vacío = siguiente disponible')
    ap.add_argument('--out', default='output')
    ap.add_argument('--publish', action='store_true', help='Publicar Reel en feed y Story independiente')
    ap.add_argument('--approved-id', default='', help='ID revisado manualmente (modo seguro)')
    ap.add_argument('--auto-publish', action='store_true', help='Publicación autónoma (sin revisión humana)')
    args=ap.parse_args()
    if args.check_instagram:
        check_instagram_identity()
        return 0
    if args.publish:
        # Validar ANTES de consumir OpenRouter y renderizar video.
        check_instagram_identity()
    episodes=catalog()
    if len(episodes)!=500 or len({e['id'] for e in episodes})!=500:
        raise RuntimeError('Catálogo de 500 propuestas dañado')
    if args.list:
        for ep in episodes:
            print(f"{ep['id']}: {ep['title']}")
        return 0
    gh=Github() if args.publish and not args.episode else None
    ep=select_episode(episodes,gh,args.episode or None)
    if ep is None:
        ap.error('ID de episodio desconocido')
    if args.publish and not args.auto_publish and args.approved_id!=ep['id']:
        ap.error('Sin --auto-publish, debe confirmar --approved-id con el ID')
    generated=create_ai_episode(ep)
    out=Path(args.out)
    out.mkdir(exist_ok=True,parents=True)
    (out/f"{ep['id']}-guion.json").write_text(
        json.dumps(generated,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Guion IA creado: {ep['id']}; referencias propuestas: {generated['source'] or 'ninguna'}")
    if args.publish and not generated.get('source'):
        print('AVISO: el guion no tiene fuentes; se permite publicar, pero no existe verificación independiente.', flush=True)
    movie,cover=render(generated,out,require_voice=args.publish)
    if args.publish:
        # Los enlaces son opcionales y nunca equivalen a verificación independiente.
        # --auto-publish implica riesgo de errores factuales de la IA.
        publish(generated,movie,cover,generated['id'])
    else:
        print('VISTA PREVIA: no se publicó el video')
    return 0


if __name__=='__main__':
    sys.exit(main())
