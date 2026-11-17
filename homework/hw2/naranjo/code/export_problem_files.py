"""Regenerate every derived problem file from the single source of truth.

    python code/export_problem_files.py

Reads   problems/ground_truth/ground_truth.json   (PRIVATE: model + solution)
Writes  problems/public/problems.json            (PUBLIC: what the LLM arms may see)
        problems/public/problems.md              (PUBLIC, human-readable)
        problems/ground_truth/formulations.md    (PRIVATE: variables, constraints, solution, how to verify)
        problems/difficulty_metrics.csv          (difficulty metrics, no answers)
"""
from __future__ import annotations

import ast
import csv
import json
import math
from pathlib import Path

from csp_spec import load_spec, solve, check_assignment

ROOT = Path(__file__).resolve().parent.parent
GT = ROOT / "problems" / "ground_truth" / "ground_truth.json"
PUB_DIR = ROOT / "problems" / "public"
LEVEL = {"facil": "Fácil", "intermedio": "Intermedio", "dificil": "Difícil"}


def statement(p) -> str:
    rules = "\n".join(f"{i}. {r}" for i, r in enumerate(p["rules_nl"], 1))
    return f"{p['context']}\n\nReglas:\n{rules}\n\nPregunta: {p['question']}"


def answer_format(p) -> dict:
    return {"keys": list(p["model"]["variables"]),
            "allowed_values": {k: v for k, v in p["model"]["variables"].items()}}


def classify(expr: str, scope) -> str:
    if "alldiff(" in expr:
        return "todos-distintos"
    if "implies(" in expr:
        return "condicional"
    if "*" in expr:
        return "capacidad ponderada"
    if "count(" in expr:
        return "conteo/cobertura"
    if " or " in expr:
        return "disyuntiva (no solapamiento)"
    if len(scope) == 1:
        return "unaria (restricción de dominio)"
    if "abs(" in expr:
        return "distancia/adyacencia"
    if any(op in expr for op in ("<", ">")):
        return "precedencia/orden"
    if "==" in expr:
        return "igualdad (agrupación)"
    return "exclusión (≠)"


def metrics(p) -> dict:
    variables, domains, cons = load_spec(p["model"])
    r = solve(p["model"], max_solutions=None)
    types = sorted({classify(e, s) for _, e, _, s in cons})
    return {
        "n_variables": len(variables),
        "domain_size": "/".join(sorted({str(len(d)) for d in domains.values()})),
        "search_space": math.prod(len(d) for d in domains.values()),
        "n_rules_nl": len(p["rules_nl"]),
        "n_constraints": len(cons),
        "max_arity": max(len(s) for *_, s in cons),
        "constraint_types": types,
        "solver_nodes": r["nodes"],
    }


class _Sub(ast.NodeTransformer):
    def __init__(self, values):
        self.values = values

    def visit_Name(self, node):
        if node.id in self.values:
            return ast.copy_location(ast.Constant(self.values[node.id]), node)
        return node


def substituted(expr: str, sol: dict) -> str:
    tree = _Sub(sol).visit(ast.parse(expr, mode="eval"))
    return ast.unparse(tree)


def md_cell(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def main():
    data = json.loads(GT.read_text(encoding="utf-8"))
    probs = data["problems"]
    PUB_DIR.mkdir(parents=True, exist_ok=True)

    public = [{"id": p["id"], "title": p["title"], "area": p["area"], "difficulty": p["difficulty"],
               "statement": statement(p), "answer_format": answer_format(p)} for p in probs]
    (PUB_DIR / "problems.json").write_text(json.dumps(
        {"_readme": ("Enunciados PUBLICOS de HW2 (20 problemas CSP de Ingeniería Industrial). Esto es lo único que "
                     "pueden ver los brazos B, B' y C. 'answer_format' lista las claves y valores permitidos de la "
                     "respuesta; decidan como equipo si se muestra al LLM (y háganlo igual en B y en C)."),
         "problems": public}, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = ["# HW2 — Enunciados públicos (20 problemas CSP de Ingeniería Industrial)", "",
             "> Este archivo **no** contiene modelos ni soluciones. Es seguro mostrarlo a los LLM de los brazos B, B′ y C.", ""]
    for p in public:
        lines += [f"## {p['id']} — {p['title']}", "",
                  f"**Área:** {p['area']} · **Dificultad:** {LEVEL[p['difficulty']]}", "",
                  p["statement"].replace("\nReglas:\n", "\n**Reglas:**\n\n").replace("\nPregunta:", "\n**Pregunta:**"),
                  "", "---", ""]
    (PUB_DIR / "problems.md").write_text("\n".join(lines), encoding="utf-8")

    rows, out = [], ["# HW2 — Formulaciones CSP y ground truth (PRIVADO)", "",
                     "> ⚠️ **No enviar a ningún LLM.** Contiene modelos y soluciones. Generado por "
                     "`code/export_problem_files.py` desde `ground_truth.json`.", "",
                     "Formato de las restricciones: expresiones del DSL de `code/csp_spec.py` "
                     "(`alldiff`, `count(valor, ...)`, `implies(a, b)`, `abs`, comparaciones, `and/or/not`). "
                     "En las expresiones de capacidad, `(X == 'L1')*4` vale 4 si X = L1 y 0 en caso contrario.", ""]
    for p in probs:
        m = metrics(p)
        rows.append({"id": p["id"], "difficulty": p["difficulty"], **{k: (";".join(v) if isinstance(v, list) else v)
                                                                       for k, v in m.items()}})
        sol = p["solution"]
        out += [f"## {p['id']} — {p['title']}", "",
                f"**Área:** {p['area']} · **Dificultad:** {LEVEL[p['difficulty']]} · "
                f"**Estado de revisión manual:** {p['review']['manual_review']}"
                + (f" ({p['review']['reviewed_by']})" if p['review'].get('reviewed_by') else ""), "",
                "### Contexto industrial", "", p["context"], "",
                "### Variables y dominios", "", "| Variable | Dominio | Significado |", "|---|---|---|"]
        for v, dom in p["model"]["variables"].items():
            out.append(f"| `{v}` | {{{', '.join(map(str, dom))}}} | {md_cell(p['variable_descriptions'][v])} |")
        out += ["", "### Restricciones", "", "| ID | Regla del enunciado | Expresión |", "|---|---|---|"]
        for c in p["model"]["constraints"]:
            out.append(f"| {c['id']} | {md_cell(p['rules_nl'][c['rule'] - 1])} | `{md_cell(c['expr'])}` |")
        out += ["", "### Solución propuesta (ground truth)", "", "| Variable | Valor |", "|---|---|"]
        out += [f"| `{k}` | **{v}** |" for k, v in sol.items()]
        checks = {cid: ok for cid, _, ok in check_assignment(p["model"], sol)}
        out += ["", "### Cómo verificarla", "",
                "**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):", "",
                "| ID | Con los valores sustituidos | ¿Se cumple? |", "|---|---|---|"]
        for c in p["model"]["constraints"]:
            out.append(f"| {c['id']} | `{md_cell(substituted(c['expr'], sol))}` | {'✓' if checks[c['id']] else '✗'} |")
        out += ["", "**2. Unicidad — deducción manual:**", "", p["deduction"], ""]
        if p["review"].get("notes"):
            out += [f"**Notas de la revisión manual ({p['review'].get('reviewed_by') or 'sin nombre'}):** "
                    + p["review"]["notes"], ""]
        out += [

                "**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las "
                "soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en "
                "`results/ground_truth_check.csv`.", "",
                "### Justificación de la dificultad", "",
                f"{m['n_variables']} variables, dominios de tamaño {m['domain_size']} "
                f"(espacio de búsqueda de {m['search_space']:,} asignaciones), {m['n_rules_nl']} reglas en lenguaje "
                f"natural que se traducen en {m['n_constraints']} restricciones atómicas, aridad máxima {m['max_arity']}. "
                f"Tipos de restricción: {', '.join(m['constraint_types'])}. "
                f"El solver de referencia (MRV + forward checking) exploró {m['solver_nodes']} nodos para enumerarlas todas.",
                "", "---", ""]
    (ROOT / "problems" / "ground_truth" / "formulations.md").write_text("\n".join(out), encoding="utf-8")

    with open(ROOT / "problems" / "difficulty_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"exported {len(probs)} problems")


if __name__ == "__main__":
    main()
