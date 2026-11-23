"""Protocolo experimental común (lo usan los brazos B, B' y C por igual).

Un solo lugar para el protocolo: todos los brazos con LLM leen estos valores.
"""
MODELO = "qwen2.5:3b"          # el del curso (resources/setup.md); 3 mil millones de parámetros
TEMPERATURA = 0.7              # > 0 para que las repeticiones midan varianza de verdad
SEMILLAS = (0, 1, 2)           # 3 repeticiones por problema y brazo
MAX_REFINAMIENTOS = 3          # B': hasta 3 reintentos después del primer intento
LIMITE_LLAMADAS_SOLVER = 200_000
LIMITE_SEGUNDOS_SOLVER = 10.0
LIMITE_LLM_S = 300.0           # una llamada al LLM que pasa de 300 s cuenta como 'no_termina' (criterio del HW1)
