import json


def translation_prompt(problem, feedback=None, previous=None):
    vertices, colors = problem["vertices"], problem["colors"]
    n, k = len(vertices), len(colors)
    vmap = ", ".join(f"{v}={i}" for i, v in enumerate(vertices))
    cmap = ", ".join(f"{c}={i}" for i, c in enumerate(colors))
    text = f"""Eres un traductor de problemas de coloreado de grafos a SAT (CNF). Responde SOLO con un objeto JSON válido, sin Markdown ni explicaciones.

Problema:
{problem['prompt_es']}

Codificación obligatoria:
- Hay {n*k} variables booleanas numeradas de 1 a {n*k}: {k} por vértice.
- Índice de cada vértice (desde 0): {vmap}.
- Índice de cada color: {cmap}.
- La variable "el vértice de índice i tiene el color de índice c" es {k}*i + c + 1.
  Ejemplo: el vértice de índice 0 con el color de índice 0 es la variable 1; con el color de índice 2 es la variable {k*0+2+1}.
- Una variable positiva significa que el vértice tiene ese color.
- Cada vértice debe tener al menos un color y como máximo uno.
- Los extremos de cada arista no pueden compartir color.

Formato exacto (los números son solo un ejemplo del formato):
{{"num_vars": {n*k}, "clauses": [[1, 2, 3], [-1, -2]]}}
Cada cláusula es una lista de enteros con signo; no uses variables fuera de 1..{n*k}. No inventes restricciones.
"""
    if feedback:
        text += f"\nEl solver reportó este error en el intento anterior: {feedback}\n"
        text += "Corrige únicamente el modelo formal. No tienes acceso a la solución de referencia.\n"
        prev = previous if isinstance(previous, str) else json.dumps(previous, ensure_ascii=False)
        text += "Salida anterior (para corregir): " + (prev or "")[:4000] + "\n"
    return text


def direct_prompt(problem):
    colors = ", ".join(problem["colors"])
    return f"""Resuelve el siguiente problema de coloreado de grafos. Responde SOLO con un objeto JSON válido, sin explicaciones:
{{"colors": {{"A": "{problem['colors'][0]}", "B": "{problem['colors'][1]}"}}}}
Incluye exactamente todos los vértices, usando solo estos colores: {colors}. Los extremos de cada arista deben tener colores distintos.
Problema: {problem['prompt_es']}
"""


def extract_json(raw):
    """First JSON object in the text (tolerates ```json fences and leading prose). Raises ValueError."""
    s = (raw or "").strip()
    i = s.find("{")
    if i < 0:
        raise ValueError("La respuesta no contiene un objeto JSON")
    try:
        obj, _ = json.JSONDecoder().raw_decode(s[i:])
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido: {exc.msg} (posición {exc.pos})") from exc
    if not isinstance(obj, dict):
        raise ValueError("El JSON no es un objeto")
    return obj
