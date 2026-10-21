"""Rutas compartidas. Todo script de ``code/`` importa esto primero.

Los archivos del curso viven intactos en ``curso/week03`` y ``curso/week04``
(huellas en ``SOURCE_MANIFEST.json``); aquí los ponemos en ``sys.path`` para
importarlos como ``search`` y ``gridworld`` sin copiarlos ni editarlos.
"""
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
RAIZ = CODE.parent                       # carpeta del grupo
RESULTS = RAIZ / "results"
FIG = RAIZ / "fig"
CACHE = RAIZ / ".llm_cache"
CURSO_W3 = CODE / "curso" / "week03"
CURSO_W4 = CODE / "curso" / "week04"


def preparar_rutas():
    for p in (CODE, CURSO_W3, CURSO_W4):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
