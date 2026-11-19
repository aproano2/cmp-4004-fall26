"""Only public problem fields are accepted by generation functions."""
import json
VERSION = 'sat-v1'

def initial(problem: dict, arm: str) -> list[dict]:
    if arm == 'C':
        instruction = ('Resuelve el problema de satisfacibilidad. Responde exclusivamente con JSON: '
                       '{"answer":"SAT" o "UNSAT", "explanation":"justificación breve"}.')
        content = problem['prompt']
    else:
        instruction = ('Traduce todas las reglas a CNF proposicional sin resolverlas. Responde exclusivamente '
                       'con un objeto JSON {"clauses":[[1,-2],[3]]}. Cada lista interior es una disyunción; '
                       'la lista exterior es una conjunción. Usa enteros positivos para variables y negativos '
                       'para negaciones, exclusivamente del mapa dado. No añadas variables ni premisas. '
                       'Una cláusula vacía significa falso; una lista sin cláusulas significa verdadero. '
                       'No incluyas markdown ni explicación.')
        content = json.dumps({'problem':problem['prompt'],'variables':problem['variables']},ensure_ascii=False)
    return [{'role':'system','content':instruction},{'role':'user','content':content}]


def feedback(messages: list[dict], raw: str, error: str) -> list[dict]:
    return [*messages, {'role':'assistant','content':raw},
            {'role':'user','content':f'Error observable: {error}. Corrige la traducción de las reglas originales. Devuelve solamente el JSON requerido.'}]
