#!/usr/bin/env python3
"""AERO_DATOS: 500 propuestas, videos de 20 s y publicación en Instagram.

Python 3.11+. Requires: requests, Pillow, edge-tts, ffmpeg (on PATH).
Images: Wikimedia Commons / Openverse, only CC0/public domain; no Pexels.
For production, configure environment secrets; never commit real credentials.
AI output is not independently fact-checked. Review important technical claims.

IMAGES: Every NEW published episode uses a different image. Hashes and source
URLs are tracked in aerodatos/state.json. Within a video, one photo across five
scenes is intentional. Historical posts without photo fingerprints cannot be
checked retroactively; register them first to guarantee legacy uniqueness.
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
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

BRAND = 'AERO_DATOS'
GRAPH_VERSION = os.getenv('IG_GRAPH_VERSION', 'v25.0')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GEMINI_API_ROOT = 'https://generativelanguage.googleapis.com/v1beta/models/'
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openrouter/free').strip() or 'openrouter/free'
if OPENROUTER_MODEL != 'openrouter/free' and not OPENROUTER_MODEL.endswith(':free'):
    raise RuntimeError('Modelo OpenRouter no gratuito rechazado')

# 10 categorías × 10 temas × 5 enfoques = 500 episodios.
SUBJECTS = [
 ('Motores y propulsión', ['Rolls-Royce Trent 1000','General Electric GEnx','CFM56-5B','LEAP-1A','Pratt & Whitney PW1100G','GE90','Trent XWB','CF34','PT6A','APU de un avión comercial']),
 ('Aerodinámica y vuelo', ['sustentación de un ala','resistencia inducida','winglets','flaps y slats','velocidad de pérdida','onda de choque transónica','efecto suelo','centro de gravedad','ángulo de ataque','formación de estelas turbulentas']),
 ('Mantenimiento y sistemas', ['sistema hidráulico','sistema fly-by-wire','tren de aterrizaje','frenos de carbono','protección contra hielo','sistema neumático','presurización de cabina','generadores eléctricos','inspección de álabes','fatiga estructural']),
 ('Operaciones y seguridad', ['despegue con viento cruzado','cálculo de combustible','aproximación estabilizada','desvío al alternativo','separación en pista','CRM de tripulación','peso y balance','operación ETOPS','reporte de incidentes','gestión de amenazas y errores']),
 ('Meteorología aeronáutica', ['cizalladura del viento','microburst','engelamiento','turbulencia en aire claro','tormentas convectivas','corrientes en chorro','visibilidad RVR','niebla de radiación','ceniza volcánica','onda de montaña']),
 ('Navegación y control aéreo', ['ADS-B','transpondedor modo S','ILS','aproximación RNP','GNSS','VOR','TCAS','separación radar','NOTAM','altitud de transición']),
 ('Economía y aerolíneas', ['factor de ocupación','costo de combustible','leasing aeronáutico','rentabilidad de una ruta','carga aérea','ingresos auxiliares','utilización diaria de aeronaves','costos de mantenimiento','planificación de flota','precio del queroseno']),
 ('Regulación y política aeronáutica', ['certificación de tipo','libertades del aire','derechos de tráfico','normativa de emisiones CORSIA','reglas de cabotaje','autoridad aeronáutica','investigación de accidentes','acuerdos bilaterales','gestión de slots','reglas de descanso de tripulaciones']),
 ('Ciencia e innovación', ['combustible SAF','hidrógeno aeronáutico','propulsión eléctrica','motores de ciclo abierto','materiales compuestos','impresión 3D de componentes','baterías de aeronaves','optimización de trayectorias','contrails y clima','aviación supersónica']),
 ('Historia de la aviación', ['hermanos Wright','Boeing 747','Concorde','DC-3','Airbus A320','primer vuelo comercial','primer avión a reacción','evolución de navegación aérea','primeros vuelos transatlánticos','evolución de seguridad aérea']),
]
QUESTION_TEMPLATES = (
 '¿Cómo funciona {x}?', '¿Qué determina el rendimiento de {x}?',
 '¿Qué limitaciones tiene {x}?', '¿Por qué importa {x} en aviación?',
 '¿Qué errores comunes existen sobre {x}?',
)

def catalog():
    rows = []
    for category, topics in SUBJECTS:
        for subject in topics:
            for template in QUESTION_TEMPLATES:
                rows.append({
                    'id': f'AD-{len(rows)+1:03d}', 'category': category,
                    'title': template.format(x=subject), 'script': '', 'source': '',
                    'lesson': f'Explica un dato técnico comprobable sobre {subject}; distingue magnitudes, unidades, condiciones y limitaciones. No inventes cifras.',
                    'image_query': subject,
                })
    return rows

AERO_CATALOG = catalog()

def now():
    return datetime.now(timezone.utc).isoformat()

def credential(name):
    value = os.getenv(name, '').strip()
    if not value or value.startswith('PON_AQUI_') or value == '00000000000000000':
        raise RuntimeError(f'Configura {name} en GitHub Actions Secrets')
    return value

# ---------- AI narration / five-scene validation ----------
VISUAL_MIN_WORDS, VISUAL_MAX_WORDS, VISUAL_MAX_CHARS = 3, 12, 72
GENERIC_VISUALS = ('sabias esto','ahora ya lo sabes','dato sorprendente','descubre algo nuevo',
 'una idea util','increible pero cierto','no te lo pierdas','esto te sorprendera',
 'sigue aprendiendo','te imaginas','mira esto','un dato real')
VISUAL_STOP_WORDS = set('a al ante como con de del desde donde el ella en entre es esa ese esta este hay la las le lo los mas menos mi no nos o para pero por porque que se sin su sus te tu tus un una uno y ya si son puede pueden ser tiene'.split())

def _visual_normalizado(value):
    import unicodedata
    return ''.join(ch for ch in unicodedata.normalize('NFKD', str(value).lower()) if not unicodedata.combining(ch))

def _palabras_relevantes(value):
    return {w for w in re.findall(r'[a-z0-9]+', _visual_normalizado(value)) if len(w)>=4 and w not in VISUAL_STOP_WORDS}

def validar_microfrases(visuals, script, title='', fact='', lesson=''):
    if not isinstance(visuals,list) or len(visuals)!=5:
        raise ValueError('Se requieren cinco mensajes visuales')
    universe = _palabras_relevantes(' '.join(map(str,(script,title,fact,lesson))))
    seen, result = set(), []
    for index, item in enumerate(visuals,1):
        if not isinstance(item,str):
            raise ValueError(f'Mensaje {index} no es texto')
        clean = re.sub(r'\s+',' ',item).strip().strip('"“”')
        words = clean.split()
        if not VISUAL_MIN_WORDS <= len(words) <= VISUAL_MAX_WORDS or len(clean)>VISUAL_MAX_CHARS:
            raise ValueError(f'Mensaje {index} demasiado largo o corto')
        if clean.endswith(('...','…',':',',',';')):
            raise ValueError(f'Mensaje {index} incompleto')
        norm = _visual_normalizado(clean).strip(' .!?¿¡')
        if norm in seen or any(g in norm for g in GENERIC_VISUALS):
            raise ValueError(f'Mensaje {index} genérico o repetido')
        if not (_palabras_relevantes(clean)&universe):
            raise ValueError(f'Mensaje {index} sin relación léxica con el guion')
        seen.add(norm); result.append(clean)
    return result

def microfrases(ep):
    return validar_microfrases(ep.get('visuals'),ep.get('script',''),ep.get('title',''),ep.get('fact',''),ep.get('lesson',''))

def _parse_ai_json(raw):
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw, flags=re.I)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        pos = raw.find('{')
        if pos<0: raise
        result, end = json.JSONDecoder().raw_decode(raw[pos:])
        if raw[pos+end:].strip().strip('`'):
            raise ValueError('Texto inesperado después del JSON')
    if not isinstance(result,dict): raise ValueError('Se esperaba objeto JSON')
    return result

def _parse_narration(raw):
    try:
        obj = _parse_ai_json(raw)
    except (ValueError,json.JSONDecodeError):
        obj={}
        for line in raw.splitlines():
            m=re.match(r'^\s*(TITULO|TITLE|GUION|SCRIPT|DATO|FACT|LECCION|LESSON)\s*:\s*(.+?)\s*$',line,re.I)
            if m:
                key={'TITULO':'title','TITLE':'title','GUION':'script','SCRIPT':'script','DATO':'fact','FACT':'fact','LECCION':'lesson','LESSON':'lesson'}[m.group(1).upper()]
                obj[key]=m.group(2).strip()
    if not isinstance(obj.get('title'),str) or not isinstance(obj.get('script'),str):
        raise ValueError('Faltan título o guion')
    obj['fact']=str(obj.get('fact') or obj.get('lesson') or obj['title']).strip()
    obj['lesson']=str(obj.get('lesson') or obj.get('fact') or obj['title']).strip()
    words=len(obj['script'].split())
    if words<30 or words>60: raise ValueError(f'Guion de {words} palabras, requiere 30–60')
    return obj

def _parse_five_visuals(raw):
    try:
        obj=json.loads(raw.strip().removeprefix('```json').removesuffix('```').strip())
        arr=obj if isinstance(obj,list) else obj.get('visuals',obj.get('mensajes')) if isinstance(obj,dict) else None
        if isinstance(arr,list):return arr
    except (ValueError,AttributeError): pass
    result={}
    for line in raw.splitlines():
        m=re.match(r'^\s*(?:MENSAJE[_ ]?|ESCENA[_ ]?|[-*]?\s*)([1-5])\s*[.):\-]\s*(.+?)\s*$',line,re.I)
        if m:result[int(m.group(1))]=m.group(2).strip().strip('"“”')
    if len(result)!=5:raise ValueError('Faltan cinco mensajes')
    return [result[i] for i in range(1,6)]

def _proposiciones_breves(text):
    for part in re.split(r'(?<=[.!?;])\s+|\s*[;:]\s*',str(text)):
        part=part.strip(' \t\n.,;:¡!¿?"“”')
        if VISUAL_MIN_WORDS<=len(part.split())<=VISUAL_MAX_WORDS and len(part)<=VISUAL_MAX_CHARS:
            yield part

def _recover_visuals(narration, responses):
    universe=_palabras_relevantes(' '.join(map(str,narration.values())))
    items=[]; seen=set()
    for response in responses:
        for s in response:
            if not isinstance(s,str):continue
            s=re.sub(r'\s+',' ',s).strip().strip('"“”')
            norm=_visual_normalizado(s).strip(' .!?¿¡')
            if norm in seen or any(g in norm for g in GENERIC_VISUALS):continue
            if not VISUAL_MIN_WORDS<=len(s.split())<=VISUAL_MAX_WORDS or len(s)>VISUAL_MAX_CHARS:continue
            if s.endswith(('...', '…',':',',',';')) or not (_palabras_relevantes(s)&universe):continue
            seen.add(norm);items.append(s)
    if len(items)<5:raise ValueError(f'Solo {len(items)} microfrases válidas')
    return validar_microfrases(items[:5],narration['script'],narration['title'],narration['fact'],narration['lesson'])

def _free_price(value):
    try:return float(value)==0.0
    except (ValueError,TypeError,OverflowError):return False

def select_free_json_models(key,count=5):
    r=requests.get(OPENROUTER_MODELS_URL,headers={'Authorization':f'Bearer {key}'},timeout=30)
    r.raise_for_status()
    choices=[]
    forbidden=('safety','moderation','guard','omni','embedding','audio','speech','image','reasoning','vision-only')
    for item in r.json().get('data',[]):
        mid=item.get('id',''); price=item.get('pricing') or {}
        if not isinstance(mid,str) or not mid.endswith(':free'):continue
        if not (_free_price(price.get('prompt')) and _free_price(price.get('completion'))):continue
        desc=(mid+' '+str(item.get('name',''))).lower()
        if any(term in desc for term in forbidden):continue
        if (item.get('context_length') or 0)<4000:continue
        familiar=any(term in desc for term in ('instruct','chat','qwen','llama','mistral','gemma'))
        choices.append((not familiar,'response_format' not in (item.get('supported_parameters') or []),mid))
    choices.sort()
    if OPENROUTER_MODEL!='openrouter/free':
        matches=[x for x in choices if x[2]==OPENROUTER_MODEL]
        if not matches:raise RuntimeError('Modelo configurado no gratuito')
        choices=matches+[x for x in choices if x[2]!=OPENROUTER_MODEL]
    if not choices:raise RuntimeError('No hay modelos gratuitos accesibles de OpenRouter')
    return [x[2] for x in choices[:count]]

def _discover_groq_models(key):
    r=requests.get('https://api.groq.com/openai/v1/models',headers={'Authorization':f'Bearer {key}'},timeout=25)
    r.raise_for_status(); available={x.get('id') for x in r.json().get('data',[])}
    pref=('openai/gpt-oss-20b','openai/gpt-oss-120b','llama-3.3-70b-versatile','llama-3.1-8b-instant')
    allowed=[m for m in pref if m in available]
    chosen=os.getenv('GROQ_MODEL','').strip()
    if chosen in available:
        allowed=[chosen]+[x for x in allowed if x!=chosen]
    return allowed[:3]

def _discover_gemini_models(key):
    found=set();page=None
    for _ in range(5):
        params={'pageSize':100}
        if page:params['pageToken']=page
        r=requests.get('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':key},params=params,timeout=25)
        r.raise_for_status();data=r.json()
        for row in data.get('models',[]):
            if 'generateContent' in row.get('supportedGenerationMethods',[]):
                found.add(row.get('name','').removeprefix('models/'))
        page=data.get('nextPageToken')
        if not page:break
    pref=('gemini-3.1-flash-lite','gemini-3.5-flash-lite','gemini-3.6-flash','gemini-3.8-flash',
          'gemini-2.5-flash-lite','gemini-2.5-flash','gemini-2.0-flash')
    models=[m for m in pref if m in found]
    chosen=os.getenv('GEMINI_MODEL','').strip().removeprefix('models/')
    if chosen in found:models=[chosen]+[m for m in models if m!=chosen]
    return models[:3]

def _ai_candidates():
    choices=[]
    for provider,secret,discover in (
       ('groq','GROQ_API_KEY',_discover_groq_models),
       ('gemini','GEMINI_API_KEY',_discover_gemini_models),
       ('openrouter','OPENROUTER_API_KEY',select_free_json_models)):
        key=os.getenv(secret,'').strip()
        if not key:continue
        try:choices.extend((provider,m,key) for m in discover(key))
        except (requests.RequestException,ValueError,RuntimeError) as exc:
            print(f'{provider}: catálogo no disponible: {str(exc)[:130]}',flush=True)
    if not choices:raise RuntimeError('Configura GROQ_API_KEY, GEMINI_API_KEY o OPENROUTER_API_KEY con modelos disponibles')
    return choices

def _response_visible_text(r,provider):
    if r.status_code in (401,403):raise ValueError(f'{provider}: credencial rechazada')
    if r.status_code==429:raise ValueError(f'{provider}: límite de cuota o capacidad (429)')
    if not r.ok:raise ValueError(f'{provider}: HTTP {r.status_code}: {r.text[:170]}')
    obj=r.json()
    if provider=='gemini':
        choices=obj.get('candidates') or []
        content=''.join(p.get('text','') for p in ((choices[0].get('content') or {}).get('parts') or []) if isinstance(p,dict)) if choices else ''
    else:
        choices=obj.get('choices') or []
        content=(choices[0].get('message') or {}).get('content','') if choices else ''
        if isinstance(content,list):content=''.join(p.get('text','') for p in content if isinstance(p,dict))
    if not isinstance(content,str) or not content.strip():raise ValueError(f'{provider}: respuesta vacía')
    return content.strip()

def _provider_text(provider,model,key,prompt,*,max_tokens=1500):
    if provider=='gemini':
        r=requests.post(GEMINI_API_ROOT+urllib.parse.quote(model,safe='')+':generateContent',
            headers={'x-goog-api-key':key,'Content-Type':'application/json'},
            json={'contents':[{'parts':[{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':min(max_tokens,2048)}},timeout=110)
        return _response_visible_text(r,provider)
    url=OPENROUTER_URL if provider=='openrouter' else GROQ_URL
    headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'}
    payload={'model':model,'messages':[{'role':'system','content':'Responde solo en español y con el formato pedido.'},
           {'role':'user','content':prompt}], 'temperature':0.2,'max_tokens':max_tokens if provider=='openrouter' else min(max_tokens,2048)}
    if provider=='openrouter':
        headers.update({'HTTP-Referer':'https://github.com','X-Title':'AERO_DATOS'})
        payload['reasoning']={'effort':'none','exclude':True}
    r=requests.post(url,headers=headers,json=payload,timeout=130)
    if provider=='openrouter' and r.status_code in (400,422) and any(word in r.text.lower() for word in ('reasoning','effort','unsupported parameter','unrecognized')):
        payload.pop('reasoning');r=requests.post(url,headers=headers,json=payload,timeout=130)
    return _response_visible_text(r,provider)

def create_ai_episode(ep):
    candidates=_ai_candidates()
    print('Modelos disponibles: '+', '.join(f'{p}:{m}' for p,m,_ in candidates),flush=True)
    intro=f"Tema: {ep['title'][:140]}. Categoría: {ep['category'][:70]}. Enseñanza: {ep['lesson'][:160]}."
    prompt=('Eres divulgador aeronáutico riguroso para pilotos, mecánicos, ATC y operaciones. '
      'Escribe en español un guion de 42 a 50 palabras idealmente, 30 a 60 obligatoriamente, '
      'para 20 segundos. Empieza con gancho técnico de 5–10 palabras verificable. '
      'Cuatro a seis oraciones completas, causa, mecanismo, conclusión; sin cifras inventadas, '
      'sin procedimientos inseguros ni afirmaciones no verificadas. Devuelve SOLO estas cuatro líneas: '
      'TITULO: ...\nGUION: ...\nDATO: ...\nLECCION: ...\n'+intro)
    narration=None; chosen=None;problem='sin respuesta'
    for provider,model,key in candidates:
        try:
            narration=_parse_narration(_provider_text(provider,model,key,prompt,max_tokens=1500))
            chosen=f'{provider}:{model}';break
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            problem=f'{provider}/{model}: {str(exc)[:150]}';print('IA etapa 1: '+problem,flush=True)
    if narration is None:raise RuntimeError('Ningún proveedor produjo un guion válido. '+problem)
    visual_prompt=('Basándote SOLO en este guion, crea cinco frases educativas diferentes, '
      'completas, de 3 a 9 palabras idealmente y máximo 12, máximo 72 caracteres, '
      'sin agregar hechos nuevos. Sigue el orden causal. Responde únicamente estas líneas: '
      'MENSAJE_1: ...\nMENSAJE_2: ...\nMENSAJE_3: ...\nMENSAJE_4: ...\nMENSAJE_5: ...\n'
      f"TITULO: {narration['title']}\nGUION: {narration['script']}\nDATO: {narration['fact']}\nLECCION: {narration['lesson']}")
    proposals=[];visuals=None;visual_model=None
    for provider,model,key in sorted(candidates,key=lambda row:f'{row[0]}:{row[1]}'!=chosen):
        try:
            raw=_provider_text(provider,model,key,visual_prompt,max_tokens=1100)
            try:proposals.append(_parse_five_visuals(raw))
            except ValueError:
                partial=[]
                for line in raw.splitlines():
                    m=re.match(r'^\s*MENSAJE_[1-5]\s*:\s*(.+)',line,re.I)
                    if m:partial.append(m.group(1))
                proposals.append(partial)
            visuals=validar_microfrases(_parse_five_visuals(raw),narration['script'],narration['title'],narration['fact'],narration['lesson'])
            visual_model=f'{provider}:{model}';break
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            problem=f'{provider}/{model}: {str(exc)[:150]}';print('IA etapa 2: '+problem,flush=True)
    if visuals is None:
        proposals.append([p for k in ('script','fact','lesson','title') for p in _proposiciones_breves(narration[k])])
        visuals=_recover_visuals(narration,proposals);visual_model='recuperación local'
    result=dict(ep)
    result.update(title=narration['title'],script=narration['script'],fact=narration['fact'],lesson=narration['lesson'],visuals=visuals,
       visual_title=visuals[0],visual_lesson=visuals[-1],source='',suggested_sources=[],ai_model=chosen,visual_ai_model=visual_model,
       generated_at=now(),verified=False,verification_note='Contenido generado por IA, no verificado independientemente')
    return result

# ---------- GitHub state / episode selection ----------
class Github:
    def __init__(self):
        self.repo=os.environ['GITHUB_REPOSITORY'];self.token=os.environ['GH_TOKEN']
        self.base=f'https://api.github.com/repos/{self.repo}'
        self.branch=os.getenv('GITHUB_REF_NAME','main')
        self.s=requests.Session()
        self.s.headers.update({'Authorization':f'Bearer {self.token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    def request(self,method,route,**kwargs):
        r=self.s.request(method,self.base+route,timeout=40,**kwargs)
        if r.status_code>=400:raise RuntimeError(f'GitHub HTTP {r.status_code}: {r.text[:450]}')
        return r.json()
    def read(self,path):
        r=self.s.get(self.base+'/contents/'+urllib.parse.quote(path,safe='/'),params={'ref':self.branch},timeout=40)
        if r.status_code==404:return None,None
        if r.status_code>=400:raise RuntimeError(f'Lectura GitHub HTTP {r.status_code}')
        data=r.json()
        if not isinstance(data,dict) or not data.get('content'):raise RuntimeError('GitHub: contenido no es un archivo')
        return base64.b64decode(data['content']),data['sha']
    def write(self,path,content,previous_sha=None):
        payload={'message':f'AeroDatos: {path}','branch':self.branch,'content':base64.b64encode(content).decode()}
        if previous_sha:payload['sha']=previous_sha
        return self.request('PUT','/contents/'+urllib.parse.quote(path,safe='/'),json=payload)
    def assert_public(self):
        if self.request('GET','').get('private') is not False:
            raise RuntimeError('El repositorio de videos debe ser público')

STATE_PATH='aerodatos/state.json'
def load_state(gh):
    raw,sha=gh.read(STATE_PATH)
    state=json.loads(raw) if raw is not None else {'schema':1,'episodes':{}}
    if not isinstance(state,dict) or not isinstance(state.get('episodes'),dict):
        raise RuntimeError('Estado remoto inválido: revisión manual necesaria')
    return state,sha

def select_episode(episodes,gh=None,requested=None):
    if requested:return next((x for x in episodes if x['id']==requested),None)
    state,_=load_state(gh) if gh else ({'episodes':{}},None)
    states=state['episodes'];blocked={'publicado','enviando','incierto'}
    by_cat={};counts={};recent=[]
    for ep in episodes:
        cat=ep['category']; row=states.get(ep['id'],{})
        if not isinstance(row,dict):raise RuntimeError('Estado inválido: '+ep['id'])
        statuses=[row.get(k) for k in ('reel','foto','feed_video','story')]
        if any(x in blocked for x in statuses):
            if 'publicado' in statuses:
                counts[cat]=counts.get(cat,0)+1
                if row.get('updated_at'):recent.append((str(row['updated_at']),cat))
            continue
        by_cat.setdefault(cat,[]).append(ep);counts.setdefault(cat,0)
    if not by_cat:raise RuntimeError('No quedan episodios sin publicar o bloquear')
    minimum=min(counts[c] for c in by_cat)
    cats=[c for c in by_cat if counts[c]==minimum]
    if recent and len(cats)>1:
        last=max(recent)[1];cats=[c for c in cats if c!=last] or cats
    rng=random.SystemRandom();cat=rng.choice(cats);ep=rng.choice(by_cat[cat])
    print(f'Episodio elegido: {ep["id"]} ({cat})',flush=True)
    return ep

# ---------- UNIQUE photo selection ----------
# URL AND normalized-pixel SHA256 AND perceptual dHash saved across published posts.
# dHash threshold 6 rejects resized/recompressed near-identical photographs.
IMAGE_LICENSES={'cc0','pdm'}
IMAGE_HEADERS={'User-Agent':'AeroDatosEducationalBot/1.3 (https://github.com/acesped/aero_datos; contact via GitHub issues)',
               'Accept':'application/json, image/jpeg, image/png, image/webp, */*;q=0.5'}
AIRLINER_POSITIVE=re.compile(r'\b(?:airliners?|passenger\s+(?:aircraft|airplanes?|jets?)|commercial\s+(?:aircraft|airplanes?|aviation|jets?)|civil(?:ian)?\s+(?:aircraft|airplanes?|aviation)|airbus|boeing|embraer|bombardier|atr\s?\d{2}|a(?:220|319|320|321|330|340|350|380)|b?7(?:17|27|37|47|57|67|77|87)|e(?:170|175|190|195)|crj(?:700|900)|dc-?(?:8|9|10)|md-?(?:80|81|82|83|87|88|90|11)|concorde|airlines?|aerolineas?|avion\s+(?:comercial|de\s+pasajeros))\b',re.I)
AIRLINER_NEGATIVE=re.compile(r'\b(?:military|warplane|warbird|fighter|bomber|combat|air\s*force|usaf|helicopter|helicoptero|chopper|rotorcraft|drone|uav|mig-?\d+|su-?\d+|f-?(?:14|15|16|18|22|35)|eurofighter|rafale|spitfire|messerschmitt|toy|model\s+kit|illustration|drawing|diagram|infographic|logo|poster|silhouette|simulation|cockpit\s+only|interior\s+only|engine\s+only|avion\s+militar|caza\s+militar)\b',re.I)
AIRLINER_STRONG=re.compile(r'\b(?:airliners?|passenger\s+(?:aircraft|airplanes?|jets?)|commercial\s+(?:aircraft|airplanes?|jets?)|airbus\s+a?\d{3}|boeing\s+b?7\d{2}|embraer\s+e?-?\d{3}|atr\s?\d{2}|airline\s+(?:aircraft|airplane|jet)|avion\s+(?:comercial|de\s+pasajeros))\b',re.I)

def _image_request(url,*,params=None,stream=False,timeout=20):
    for attempt in range(2):
        r=requests.get(url,params=params,headers=IMAGE_HEADERS,timeout=timeout,stream=stream)
        if r.status_code in (429,502,503,504) and attempt==0:
            r.close();time.sleep(2);continue
        r.raise_for_status();return r
    raise RuntimeError('Servicio de imágenes no disponible')

def _strip_html(value):return re.sub(r'<[^>]*>','',str(value or '')).strip()

def _commons_candidates(query):
    params={'action':'query','format':'json','generator':'search','gsrsearch':'filetype:bitmap '+query,
            'gsrnamespace':6,'gsrlimit':35,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1000}
    with _image_request('https://commons.wikimedia.org/w/api.php',params=params) as r:
        pages=r.json().get('query',{}).get('pages',{})
    for page in pages.values():
        info=(page.get('imageinfo') or [{}])[0];meta=info.get('extmetadata') or {}
        lic=_strip_html((meta.get('LicenseShortName') or {}).get('value','')).lower().replace(' ','')
        free=('cc0' in lic or 'publicdomain' in lic or lic in ('pd','pdm','dominiopublico','dominiopúblico') or lic.startswith('pd-'))
        if not free or any(s in lic for s in ('cc-by','-nc','-nd')):continue
        url=info.get('thumburl') or info.get('url')
        if url:yield {'url':url,'title':page.get('title',''),'author':_strip_html((meta.get('Artist') or {}).get('value','')),
           'description':_strip_html((meta.get('ImageDescription') or {}).get('value',''))[:500],
           'license':lic,'source':info.get('descriptionurl','')}

def _openverse_candidates(query):
    with _image_request('https://api.openverse.org/v1/images/',params={'q':query,'license':'cc0,pdm','page_size':40},timeout=25) as r:
        items=r.json().get('results',[])
    for item in items:
        lic=str(item.get('license') or '').lower()
        if lic not in IMAGE_LICENSES:continue
        url=item.get('url') or item.get('thumbnail')
        if url:yield {'url':url,'title':item.get('title',''), 'description':str(item.get('description') or '')[:500],
          'author':item.get('creator',''),'license':lic,'source':item.get('foreign_landing_url','')}

def _airliner_metadata_valid(c):
    text=' '.join(str(c.get(k) or '') for k in ('title','description'))
    if AIRLINER_NEGATIVE.search(text):return False
    return bool(AIRLINER_STRONG.search(text) or (AIRLINER_POSITIVE.search(text) and
       re.search(r'\b(?:aircraft|airplane|jet|airport|airliner|landing|takeoff|flight|avion)\b',text,re.I)))

def _image_queries(ep):
    subject=' '.join(str(ep.get(k) or '') for k in ('title','image_query','script'))
    models=re.findall(r'\b(?:A220|A319|A320|A321|A330|A340|A350|A380|B?717|B?727|B?737|B?747|B?757|B?767|B?777|B?787|E170|E175|E190|E195|CRJ700|CRJ900|ATR42|ATR72|Concorde)\b',subject,re.I)
    specific=[f'{m.upper()} passenger airliner aircraft' for m in dict.fromkeys(models)]
    general=['Boeing 737 passenger airliner','Airbus A320 commercial airplane','Boeing 787 passenger airliner',
       'Embraer E190 passenger airliner','ATR 72 passenger aircraft','Airbus A350 commercial airplane',
       'Boeing 747 passenger airliner','Airbus A380 passenger airliner',
       'Boeing 777 passenger airliner','Airbus A330 commercial airplane',
       'airliner airport runway passenger jet','commercial passenger aircraft airport']
    # Shuffle per episode: previously we always picked the FIRST result of the FIRST query.
    random.SystemRandom().shuffle(general)
    return list(dict.fromkeys(specific+general))

def _dhash(img):
    small=ImageOps.grayscale(img).resize((9,8),Image.Resampling.LANCZOS)
    px=list(small.getdata()); result=0
    for y in range(8):
        for x in range(8):result=(result<<1)|int(px[y*9+x]>px[y*9+x+1])
    return f'{result:016x}'

def _image_fingerprint(img):
    normalized=ImageOps.fit(img.convert('RGB'),(256,256),method=Image.Resampling.LANCZOS)
    return {'photo_sha256':hashlib.sha256(normalized.tobytes()).hexdigest(), 'photo_dhash':_dhash(img)}

def _used_photo_records(state,except_id=None):
    result=[]
    for eid,row in state.get('episodes',{}).items():
        if eid==except_id or not isinstance(row,dict):continue
        # Count photos of published or in-flight/uncertain posts. Unknown outcomes remain reserved.
        if not any(row.get(k) in ('publicado','enviando','incierto') for k in ('reel','story','foto','feed_video')):continue
        photo=row.get('image') if isinstance(row.get('image'),dict) else row
        if any(photo.get(k) for k in ('photo_sha256','photo_dhash','photo_url','photo_source')):
            result.append(photo)
    return result

def _photo_unique(fingerprint,candidate,records):
    url=candidate.get('url','');source=candidate.get('source','')
    for record in records:
        if url and url==record.get('photo_url'):return False
        if source and source==record.get('photo_source'):return False
        if fingerprint['photo_sha256']==record.get('photo_sha256'):return False
        other=record.get('photo_dhash','')
        if isinstance(other,str) and re.fullmatch(r'[0-9a-fA-F]{16}',other):
            if (int(fingerprint['photo_dhash'],16)^int(other,16)).bit_count()<=6:return False
    return True

def _safe_photo_download(url,target):
    parsed=urllib.parse.urlparse(url);host=(parsed.hostname or '').lower()
    # Restrict remote hosts: thumbnails often live on Wikimedia; Openverse can link
    # to third-party hosts, so require public HTTPS and reject private resolutions.
    if parsed.scheme!='https' or not host or host=='localhost' or host.endswith('.local'):return False
    import ipaddress, socket
    try:
        for row in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM):
            address=ipaddress.ip_address(row[4][0])
            if not address.is_global:return False
        with _image_request(url,stream=True,timeout=22) as r:
            if not any(t in r.headers.get('Content-Type','').lower() for t in ('image/jpeg','image/png','image/webp')):return False
            # requests follows HTTPS redirects; reject private/HTTP final destinations.
            final=urllib.parse.urlparse(r.url)
            if final.scheme!='https':return False
            final_host=(final.hostname or '').lower()
            if not final_host:return False
            for row in socket.getaddrinfo(final_host,443,type=socket.SOCK_STREAM):
                if not ipaddress.ip_address(row[4][0]).is_global:return False
            content=bytearray()
            for block in r.iter_content(65536):
                content.extend(block)
                if len(content)>10_000_000:return False
        with Image.open(io.BytesIO(content)) as im:
            img=ImageOps.exif_transpose(im)
            if img.width<420 or img.height<300:return False
            converted=img.convert('RGB');fp=_image_fingerprint(converted)
            converted.save(target,'JPEG',quality=86)
            return fp
    except Exception as exc:
        print(f'Fotografía descartada ({type(exc).__name__}): {str(exc)[:100]}',flush=True)
        return False

def prepare_photos(ep,folder,used_records=()):
    """One unique CC0/PD civilian airliner photograph per episode.

    Samples results randomly rather than always taking the first match. Both
    source identifiers and visual fingerprints are checked against history.
    """
    dest=folder/'foto_avion_comercial.jpg';dest.unlink(missing_ok=True)
    credits=[];seen_urls=set();rejected=0;duplicate=0;failures=0
    for query in _image_queries(ep):
        backends=[_commons_candidates,_openverse_candidates]
        random.SystemRandom().shuffle(backends)
        for backend in backends:
            try:
                candidates=list(backend(query));random.SystemRandom().shuffle(candidates)
                print(f'Fotos: {backend.__name__}: {len(candidates)} candidatas para {query}',flush=True)
                for candidate in candidates:
                    url=candidate['url']
                    if url in seen_urls:continue
                    seen_urls.add(url)
                    if not _airliner_metadata_valid(candidate):rejected+=1;continue
                    fp=_safe_photo_download(url,dest)
                    if not fp:failures+=1;continue
                    if not _photo_unique(fp,candidate,used_records):
                        duplicate+=1;dest.unlink(missing_ok=True);continue
                    chosen=dict(candidate)
                    chosen.update(fp,photo_url=url,photo_source=candidate.get('source',''),matched_query=query)
                    credits=[chosen]
                    (folder/'creditos_imagenes.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2),encoding='utf-8')
                    print(f'FOTO NUEVA: {chosen.get("title", "")} SHA={fp["photo_sha256"][:12]}',flush=True)
                    return [dest],credits
            except (requests.RequestException,ValueError,KeyError,RuntimeError) as exc:
                print(f'Fotos: {backend.__name__} falló: {str(exc)[:140]}',flush=True)
    (folder/'creditos_imagenes.json').write_text('[]',encoding='utf-8')
    raise RuntimeError('No hay foto civil CC0/PD diferente de las reservadas o publicadas. '
       f'Descartadas={rejected}, repetidas={duplicate}, descargas fallidas={failures}. NO publicar.')

# ---------- Video generation ----------
def font(size,bold=False):
    paths=(['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
           if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'])
    for path in paths:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def wrap_text(draw,text,text_font,width):
    rows=[];current=''
    for word in text.split():
        trial=f'{current} {word}'.strip()
        if draw.textbbox((0,0),trial,font=text_font)[2]<=width:current=trial
        else:
            if current:rows.append(current)
            current=word
    if current:rows.append(current)
    return rows

def texto_centrado_seguro(draw,texto,*,centro_y,ancho=560,max_lineas=3):
    for size in range(66,27,-2):
        f=font(size,True);lines=wrap_text(draw,texto.upper(),f,ancho)
        if not lines or len(lines)>max_lineas:continue
        boxes=[draw.textbbox((0,0),s,font=f,stroke_width=1) for s in lines]
        if any(b[2]-b[0]>ancho for b in boxes):continue
        step=size+17;height=len(lines)*step
        if height>320:continue
        y=centro_y-height//2
        for line,b in zip(lines,boxes):
            x=(720-(b[2]-b[0]))/2
            draw.text((x,y),line,font=f,fill=(255,255,255),stroke_width=1,stroke_fill=(4,7,22))
            y+=step
        return
    raise ValueError('El mensaje no cabe en la zona segura')

def palette(i):
    return ([(12,12,32),(9,23,38),(27,15,28),(14,26,25),(20,17,45)][i%5],
            [(186,93,253),(39,217,241),(255,193,92),(69,231,169),(252,105,174)][i%5])

def scene(ep,number,dest,photo=None):
    if not photo or not Path(photo).is_file():raise RuntimeError('Se exige foto de avión civil')
    with Image.open(photo) as source:
        img=ImageOps.fit(source.convert('RGB'),(720,1280),method=Image.Resampling.LANCZOS)
    img=ImageEnhance.Brightness(img).enhance(.48)
    d=ImageDraw.Draw(img,'RGBA');_,accent=palette(number+int(ep['id'][-3:]))
    d.rounded_rectangle((46,420,674,825),radius=26,fill=(3,12,28,148))
    d.rounded_rectangle((52,72,668,152),radius=24,fill=(255,255,255,18),outline=(*accent,200),width=3)
    d.text((77,91),BRAND,font=font(33,True),fill=(255,255,255))
    d.text((55,187),ep['category'].upper(),font=font(19,True),fill=accent)
    texto_centrado_seguro(d,microfrases(ep)[number],centro_y=610,ancho=560,max_lineas=3)
    d.line((58,1128,662,1128),fill=accent,width=5)
    d.text((92,1154),'aero datos - conocimiento en 20 segundos',font=font(21,True),fill='white')
    img.save(dest,quality=92)

def ambient(path,seconds=20):
    import array
    rate=16000;buff=array.array('h')
    for i in range(rate*seconds):
        t=i/rate;fade=max(0,min(1.,t/.8,(seconds-t)/1.3))
        v=math.sin(2*math.pi*110*t)*.17+math.sin(2*math.pi*164.81*t)*.07+math.sin(2*math.pi*220*t)*.05
        buff.append(int(32767*fade*v))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(buff.tobytes())

async def narrate(script,path):
    import edge_tts
    await edge_tts.Communicate(script,voice=os.getenv('AERO_VOICE','es-ES-AlvaroNeural'),rate='+12%').save(str(path))
    if not path.exists() or path.stat().st_size<500:raise RuntimeError('Narración inválida')

def render(ep,out,require_voice=False,used_records=()):
    out.mkdir(parents=True,exist_ok=True)
    if not ep.get('script'):raise ValueError('Falta guion')
    folder=out/ep['id'];folder.mkdir(parents=True,exist_ok=True)
    photos,credits=prepare_photos(ep,folder,used_records=used_records)
    ep['image_credits']=credits
    frames=[]
    for i in range(5):
        dest=folder/f'escena_{i}.jpg';scene(ep,i,dest,photos[0]);frames.append(dest)
    cover=out/f"{ep['id']}.jpg";cover.write_bytes(frames[0].read_bytes())
    background=folder/'ambient.wav';ambient(background)
    narration=folder/'voz.mp3'
    try:asyncio.run(narrate(ep['script'],narration))
    except Exception as exc:
        if require_voice:raise RuntimeError(f'Narración obligatoria falló: {exc}') from exc
        print(f'Vista previa sin voz: {exc}',file=sys.stderr)
    args=['ffmpeg','-hide_banner','-loglevel','error','-y']
    for frame in frames:args+=['-loop','1','-framerate','30','-t','4','-i',str(frame)]
    args+=['-i',str(background)]
    voice=narration.exists() and narration.stat().st_size>500
    if voice:args+=['-i',str(narration)]
    motion=os.getenv('AERO_SUBTLE_ZOOM','true').lower() in ('1','true','yes','on')
    if motion:
        vf=''.join(f"[{i}:v]zoompan=z='min(1+on*0.0002,1.024)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=30,setsar=1[v{i}];" for i in range(5))
    else:
        vf=''.join(f'[{i}:v]fps=30,scale=720:1280,setsar=1[v{i}];' for i in range(5))
    vf+=''.join(f'[v{i}]' for i in range(5))+'concat=n=5:v=1:a=0[v];'
    vf+='[5:a]volume=0.28[amb];[6:a]volume=1.4[voice];[amb][voice]amix=inputs=2:duration=first:dropout_transition=0[a]' if voice else '[5:a]volume=0.5[a]'
    movie=out/f"{ep['id']}.mp4"
    args+=['-filter_complex',vf,'-map','[v]','-map','[a]','-c:v','libx264','-pix_fmt','yuv420p',
           '-preset','veryfast','-crf','24','-r','30','-c:a','aac','-b:a','128k','-t','20','-movflags','+faststart',str(movie)]
    subprocess.run(args,check=True,timeout=240)
    print(f'Video: {movie} ({movie.stat().st_size:,} bytes); portada: {cover}',flush=True)
    return movie,cover

# ---------- Instagram publication ----------
def ig_api(method,path,*,token,**kwargs):
    url=f'https://graph.instagram.com/{GRAPH_VERSION}/{path}'
    data=dict(kwargs.pop('data',{}) or {});data['access_token']=token
    r=requests.get(url,params=data,timeout=50) if method=='GET' else requests.post(url,data=data,timeout=60)
    try:obj=r.json()
    except ValueError:raise RuntimeError(f'Instagram HTTP {r.status_code}, respuesta no JSON')
    if not r.ok or obj.get('error'):raise RuntimeError(f'Instagram HTTP {r.status_code}: {obj.get("error",obj)}')
    return obj

def check_instagram_identity(token=None,user_id=None,expected=None):
    token=token if token is not None else credential('INSTAGRAM_TOKEN')
    user_id=str(user_id if user_id is not None else credential('INSTAGRAM_USER_ID')).strip()
    expected=(expected if expected is not None else os.getenv('IG_EXPECTED_USERNAME','')).strip().lstrip('@').lower()
    if not expected:raise RuntimeError('Falta IG_EXPECTED_USERNAME')
    if not user_id.isdigit():raise RuntimeError('INSTAGRAM_USER_ID debe ser numérico')
    try:me=ig_api('GET','me',token=token,data={'fields':'id,user_id,username'})
    except RuntimeError as exc:
        detail=str(exc).lower()
        if 'user_id' not in detail or not any(s in detail for s in ('nonexisting field','non-existing field','unknown field','field is not supported')):raise
        me=ig_api('GET','me',token=token,data={'fields':'id,username'})
    username=str(me.get('username','')).strip().lstrip('@').lower()
    if username!=expected:raise RuntimeError(f'Token de otra cuenta: esperado @{expected}, autorizado @{username}')
    ids={str(me.get(k,'')).strip() for k in ('id','user_id') if str(me.get(k,'')).strip().isdigit()}
    if user_id not in ids:raise RuntimeError('INSTAGRAM_USER_ID no coincide con la cuenta autorizada')
    print(f'Instagram verificado: @{username}',flush=True)
    return me

def _publish_container(user_id,token,video_url,caption=None,story=False):
    data={'media_type':'STORIES' if story else 'REELS','video_url':video_url}
    if not story:data.update(caption=caption,share_to_feed='true')
    container=ig_api('POST',f'{user_id}/media',token=token,data=data)['id']
    for _ in range(30):
        time.sleep(10)
        status=ig_api('GET',container,token=token,data={'fields':'status_code,status'})
        if status.get('status_code')=='FINISHED':break
        if status.get('status_code') in ('ERROR','EXPIRED'):raise RuntimeError(f'Contenedor IG {container}: {status}')
    else:raise RuntimeError(f'Timeout contenedor {container}; reconciliar antes de reintentar')
    return ig_api('POST',f'{user_id}/media_publish',token=token,data={'creation_id':container})['id']

def publish_container(user_id,token,video_url,caption):return _publish_container(user_id,token,video_url,caption=caption)
def publish_story_container(user_id,token,video_url):return _publish_container(user_id,token,video_url,story=True)

def upload_video_to_public_github(gh,movie,episode_id):
    data=movie.read_bytes();digest=hashlib.sha256(data).hexdigest()[:16];filename=f'{episode_id}-{digest}.mp4'
    for root in ('aerodatos_assets/media','aerodatos_video_assets/media','aerodatos_public_videos/media'):
        remote=f'{root}/{filename}'
        old,_=gh.read(remote)
        if old is not None:
            if old!=data:raise RuntimeError(f'Colisión de archivos: {remote}')
            commit=gh.request('GET',f'/commits/{gh.branch}')['sha']
            return remote,commit
        try:result=gh.write(remote,data)
        except RuntimeError as exc:
            if 'HTTP 409' in str(exc) and any(s in str(exc) for s in ('subdirectory','file exists')):continue
            raise
        return remote,result['commit']['sha']
    raise RuntimeError('Rutas de videos incompatibles con el árbol GitHub')

def _photo_info(ep):
    images=ep.get('image_credits') or []
    if len(images)!=1:raise RuntimeError('Falta metadato de foto única')
    c=images[0]
    return {k:c.get(k,'') for k in ('photo_url','photo_source','photo_sha256','photo_dhash','title','license','matched_query')}

def publish(ep,movie,cover,approval,gh=None):
    if approval!=ep['id']:raise ValueError('Aprobación no coincide con episodio')
    if not ep.get('script'):raise ValueError('No se publica sin narración')
    token=credential('INSTAGRAM_TOKEN');user_id=credential('INSTAGRAM_USER_ID')
    check_instagram_identity(token,user_id)
    gh=gh or Github();gh.assert_public()
    state,sha=load_state(gh);row=state['episodes'].get(ep['id'],{})
    if any(row.get(k) in ('publicado','enviando','incierto') for k in ('reel','foto','feed_video','story')):
        raise RuntimeError('Publicación previa o incierta: bloqueada')
    photo=_photo_info(ep)
    if not _photo_unique(photo,{'url':photo['photo_url'],'source':photo['photo_source']},_used_photo_records(state,ep['id'])):
        raise RuntimeError('FOTO YA UTILIZADA: el estado cambió desde el renderizado; NO publicar')
    def save():
        nonlocal sha
        result=gh.write(STATE_PATH,json.dumps(state,ensure_ascii=False,indent=2).encode(),sha)
        sha=result['content']['sha']
    remote,commit=upload_video_to_public_github(gh,movie,ep['id'])
    video_url=f'https://raw.githubusercontent.com/{gh.repo}/{commit}/{remote}'
    response=requests.get(video_url,timeout=60)
    if not response.ok or len(response.content)!=movie.stat().st_size:raise RuntimeError('MP4 no accesible públicamente')
    caption=f"{ep['title']}\n\n{ep['script'].strip()}"
    fact=str(ep.get('fact') or '').strip();lesson=str(ep.get('lesson') or '').strip()
    if fact and fact.casefold() not in ep['script'].casefold():caption+=f'\n\nDato clave: {fact}'
    if lesson and lesson.casefold() not in ep['script'].casefold():caption+=f'\n\nPara recordar: {lesson}'
    if ep.get('source'):caption+=f'\n\nReferencias sugeridas (no verificadas): {ep["source"]}'
    caption+='\n\n¿Qué detalle de este mecanismo te gustaría entender mejor?\n\n#AeroDatos #Aviacion #ConocimientoAeronautico'
    state['episodes'][ep['id']]=row
    # Persist image reservation BEFORE contacting Meta. CAS/sha protects from
    # concurrent workflows: if another run updated state, write fails 409/422.
    row.update(reel='enviando',image=photo,updated_at=now());save()
    try:reel_id=publish_container(user_id,token,video_url,caption)
    except BaseException:
        row.update(reel='incierto',updated_at=now())
        try:save()
        except Exception as exc:print(f'ALERTA: no se guardó estado incierto: {exc}',file=sys.stderr)
        raise
    row.update(reel='publicado',share_to_feed=True,reel_id=reel_id,video_url=video_url,updated_at=now());save()
    print(f'Reel y feed publicados: {reel_id}',flush=True)
    row.update(story='enviando',updated_at=now());save()
    try:story_id=publish_story_container(user_id,token,video_url)
    except BaseException:
        row.update(story='incierto',updated_at=now())
        try:save()
        except Exception as exc:print(f'ALERTA: no se guardó estado Story: {exc}',file=sys.stderr)
        print('Reel publicado. Story incierta; NO volver a publicar el Reel.',file=sys.stderr)
        raise
    row.update(story='publicado',story_id=story_id,updated_at=now());save()
    print(f'Story publicada: {story_id}',flush=True)

# ---------- CLI ----------
def main():
    ap=argparse.ArgumentParser(description='AERO_DATOS: 500 ideas, video e Instagram con foto única por publicación')
    ap.add_argument('--list',action='store_true')
    ap.add_argument('--check-instagram',action='store_true')
    ap.add_argument('--episode',default='',help='ID exacto; vacío selecciona aleatorio equilibrado')
    ap.add_argument('--out',default='output')
    ap.add_argument('--publish',action='store_true',help='Publicar Reel/feed + Story')
    ap.add_argument('--approved-id',default='')
    ap.add_argument('--auto-publish',action='store_true')
    args=ap.parse_args()
    if args.check_instagram:check_instagram_identity();return 0
    episodes=catalog()
    if len(episodes)!=500 or len({e['id'] for e in episodes})!=500:raise RuntimeError('Catálogo de 500 corrupto')
    if args.list:
        for ep in episodes:print(f"{ep['id']}: {ep['title']}")
        return 0
    # In publication mode always read history (even with explicit --episode).
    if args.publish:check_instagram_identity()
    gh=Github() if args.publish else None
    ep=select_episode(episodes,gh,args.episode or None)
    if ep is None:ap.error('ID de episodio desconocido')
    if args.publish and not args.auto_publish and args.approved_id!=ep['id']:
        ap.error('Sin --auto-publish se exige --approved-id igual al episodio seleccionado')
    used_records=_used_photo_records(load_state(gh)[0],ep['id']) if gh else []
    generated=create_ai_episode(ep)
    out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
    (out/f"{ep['id']}-guion.json").write_text(json.dumps(generated,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/f"{ep['id']}-experimento.json").write_text(json.dumps({
      'episode_id':ep['id'],'category':ep['category'],'creative_variant':'aero_hook_technical_clean_zoom_unique_photo_v2',
      'hook_visual':generated['visuals'][0],'duration_seconds':20,'scene_count':5,'ai_model':generated.get('ai_model'),
      'metrics':None,'note':'Instagram Insights se consulta por separado.'},ensure_ascii=False,indent=2),encoding='utf-8')
    movie,cover=render(generated,out,require_voice=args.publish,used_records=used_records)
    # Persist the complete metadata including selected picture locally too.
    (out/f"{ep['id']}-guion.json").write_text(json.dumps(generated,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.publish:publish(generated,movie,cover,generated['id'],gh=gh)
    else:print('VISTA PREVIA: no publicado. Sin GitHub no se comprueba historial remoto.',flush=True)
    return 0

if __name__=='__main__':sys.exit(main())
