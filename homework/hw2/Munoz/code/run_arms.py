import argparse
import importlib.util
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "dpll", BASE.parents[2] / "studios/week-07/dpll.py"
)
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)

PROMPTS = {
    "B": (
        'Traduce las condiciones del evento a CNF. No resuelvas el problema. '
        'Devuelve solo JSON: {"clauses": [[1, -2], [3]]}. '
        'Usa exclusivamente los identificadores dados. Un entero positivo significa '
        'incluir la actividad; uno negativo, excluirla. Cada lista es OR y el conjunto '
        'es AND. Incluye todas las condiciones, sin agregar otras.'
    ),
    "C": (
        'Resuelve el problema directamente. Devuelve solo JSON: '
        '{"status": "SAT", "assignment": {"1": true, "2": false}}. '
        'Incluye todos los identificadores dados con valores booleanos. '
        'Si no existe solucion, devuelve {"status": "UNSAT"}.'
    ),
}


class Ollama:
    def __init__(self, model="llama3.2:3b", url="http://localhost:11434", timeout=120):
        self.model = model
        self.url = url.rstrip("/")
        self.timeout = timeout

    def __call__(self, messages):
        payload = {
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 2048},
        }
        request = urllib.request.Request(
            self.url + "/api/chat", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        start = time.perf_counter()
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            data = json.load(response)
        elapsed = time.perf_counter() - start
        cache = BASE / ".llm_cache"
        cache.mkdir(exist_ok=True)
        path = cache / f"{time.time_ns()}.json"
        path.write_text(json.dumps({"request": payload, "response": data,
                                    "llm_time_s": elapsed}, indent=2) + "\n", encoding="utf-8")
        return {
            "raw_output": data["message"]["content"], "llm_time_s": elapsed,
            "input_tokens": data.get("prompt_eval_count"),
            "output_tokens": data.get("eval_count"), "cache_file": str(path.relative_to(BASE)),
        }


def parse_cnf(raw, n):
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("clauses"), list):
        raise ValueError("Se requiere un objeto con una lista clauses.")
    clauses = data["clauses"]
    for clause in clauses:
        if not isinstance(clause, list):
            raise ValueError("Cada clausula debe ser una lista.")
        if any(type(lit) is not int or not 1 <= abs(lit) <= n for lit in clause):
            raise ValueError("Literal invalido: se requieren enteros no nulos entre -n y n.")
    return clauses


def parse_answer(raw, n):
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Se requiere un objeto JSON.")
    if data.get("status") == "UNSAT":
        return None
    assignment = data.get("assignment")
    if data.get("status") != "SAT" or not isinstance(assignment, dict):
        raise ValueError("Se requiere status SAT y assignment, o status UNSAT.")
    if set(assignment) != {str(i) for i in range(1, n + 1)}:
        raise ValueError("La respuesta debe incluir todas las variables y ninguna adicional.")
    if any(type(value) is not bool for value in assignment.values()):
        raise ValueError("Los valores deben ser true o false.")
    return assignment


def solve(clauses, n):
    start = time.perf_counter()
    assignment = solver.dpll([frozenset(clause) for clause in clauses])
    elapsed = time.perf_counter() - start
    if assignment is not None:
        assignment = {str(i): assignment.get(i, False) for i in range(1, n + 1)}
    return assignment, elapsed


def evaluate(assignment, truth):
    if assignment is None:
        return "correct" if truth["status"] == "UNSAT" else "incorrect"
    valid = truth["status"] == "SAT" and all(
        any(assignment[str(abs(lit))] == (lit > 0) for lit in clause)
        for clause in truth["cnf"]
    )
    return "correct" if valid else "incorrect"


def build_messages(arm, problem):
    return [
        {"role": "system", "content": PROMPTS[arm]},
        {"role": "user", "content": problem["prompt"] + "\nIdentificadores: " +
         json.dumps(problem["variables"])},
    ]


def run_attempt(arm, problem, truth, client=None, messages=None):
    start = time.perf_counter()
    n = problem["n_variables"]
    row = {
        "problem_id": problem["id"], "difficulty": problem["difficulty"], "arm": arm,
        "model": None if arm == "A" else client.model,
        "status": "no-answer", "answer_status": None, "assignment": None,
        "llm_time_s": 0.0, "solver_time_s": 0.0,
        "input_tokens": None, "output_tokens": None,
        "raw_output": None, "error": None, "cache_file": None,
        "ground_truth_reviewed": truth["human_reviewed"],
    }
    if arm not in ("A", "B", "C"):
        raise ValueError("Brazo no admitido.")
    if arm == "A":
        assignment, row["solver_time_s"] = solve(truth["cnf"], n)
    else:
        if messages is None:
            messages = build_messages(arm, problem)
        llm_start = time.perf_counter()
        try:
            row.update(client(messages))
        except (OSError, ValueError, KeyError) as exc:
            row["llm_time_s"] = time.perf_counter() - llm_start
            row["error"] = f"llm_error: {exc}"
            row["total_time_s"] = time.perf_counter() - start
            return row
        try:
            if arm == "B":
                clauses = parse_cnf(row["raw_output"], n)
                assignment, row["solver_time_s"] = solve(clauses, n)
            else:
                assignment = parse_answer(row["raw_output"], n)
        except ValueError as exc:
            row["error"] = f"parse_error: {exc}"
            row["total_time_s"] = time.perf_counter() - start
            return row
    row["assignment"] = assignment
    row["answer_status"] = "SAT" if assignment is not None else "UNSAT"
    row["status"] = evaluate(assignment, truth)
    if arm == "B" and assignment is None:
        row["error"] = "solver_unsat"
    row["total_time_s"] = time.perf_counter() - start
    return row


def run_arm(arm, problem, truth, client=None, initial=None):
    if arm != "Bp":
        return run_attempt(arm, problem, truth, client)
    start = time.perf_counter()
    messages = build_messages("B", problem)
    first = initial if initial is not None else run_attempt("B", problem, truth, client, messages)
    attempts = [dict(first, iteration=0)]
    for iteration in range(1, 4):
        previous = attempts[-1]
        error = previous["error"] or ""
        if not (error.startswith("parse_error:") or error == "solver_unsat"):
            break
        messages = messages + [
            {"role": "assistant", "content": previous["raw_output"]},
            {"role": "user", "content": f"Error del validador/solver: {error}. Corrige el modelo y devuelve solo el JSON requerido."},
        ]
        result = run_attempt("B", problem, truth, client, messages)
        attempts.append(dict(result, iteration=iteration))
    row = dict(attempts[-1], arm="Bp", attempts=attempts, refinements=len(attempts) - 1)
    for key in ("llm_time_s", "solver_time_s", "input_tokens", "output_tokens"):
        values = [attempt[key] for attempt in attempts]
        row[key] = sum(values) if all(value is not None for value in values) else None
    row["total_time_s"] = time.perf_counter() - start + (first["total_time_s"] if initial is not None else 0)
    row["success_iteration"] = next((a["iteration"] for a in attempts if a["status"] == "correct"), None)
    return row


def print_summary(row, problem):
    labels = {"correct": "Correcto", "incorrect": "Incorrecto", "no-answer": "Sin respuesta valida"}
    print(f"  Resultado: {labels[row['status']]}")
    if row["arm"] == "Bp":
        print(f"  Reintentos: {row['refinements']} de 3")
        for attempt in row["attempts"]:
            print(f"  Intento {attempt['iteration']}: {labels[attempt['status']]}")
    if row["assignment"] is not None:
        for variable, included in row["assignment"].items():
            print(f"  {problem['variables'][variable]}: {'incluir' if included else 'excluir'}")
    elif row["answer_status"] == "UNSAT":
        print("  Respuesta: no existe solucion (UNSAT)")
    if row["error"]:
        kind = row["error"].split(":", 1)[0]
        messages = {
            "parse_error": "La salida no cumple el formato requerido.",
            "solver_unsat": "Las clausulas generadas no tienen solucion.",
            "llm_error": "No se pudo obtener la respuesta de Ollama.",
        }
        print(f"  Error: {messages.get(kind, row['error'])}")
    print(f"  Tiempo: {row['total_time_s']:.2f} s (IA: {row['llm_time_s']:.2f} s; solver: {row['solver_time_s']:.6f} s)")
    if row["input_tokens"] is not None:
        print(f"  Tokens: {row['input_tokens']} entrada / {row['output_tokens']} salida")
    print(f"  Revision manual: {'si' if row['ground_truth_reviewed'] else 'pendiente'}")
    if row["cache_file"]:
        print(f"  Salida original: {row['cache_file']}")
    print(flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=["A", "B", "Bp", "C", "all"], required=True)
    parser.add_argument("--id", help="Ejemplo: SAT-01. Sin este argumento se usan los 20 casos.")
    parser.add_argument("--model", default="llama3.2:3b")
    parser.add_argument("--url", default="http://localhost:11434")
    parser.add_argument("--json", action="store_true", help="Mostrar el registro JSON completo.")
    args = parser.parse_args()
    problems = json.loads((BASE / "problems/problems.json").read_text(encoding="utf-8"))
    truths = {t["id"]: t for t in json.loads(
        (BASE / "problems/ground_truth.json").read_text(encoding="utf-8"))}
    if args.id:
        problems = [p for p in problems if p["id"] == args.id]
        if not problems:
            parser.error("ID de problema inexistente.")
    client = Ollama(args.model, args.url)
    arms = ("A", "B", "Bp", "C") if args.arm == "all" else (args.arm,)
    for problem in problems:
        initial_b = None
        for arm in arms:
            if not args.json:
                label = "B'" if arm == "Bp" else arm
                print(f"{problem['id']} | Brazo {label} | Ejecutando...", flush=True)
            row = run_arm(arm, problem, truths[problem["id"]], client, initial=initial_b)
            if arm == "B":
                initial_b = row
            if args.json:
                print(json.dumps(row), flush=True)
            else:
                print_summary(row, problem)


if __name__ == "__main__":
    main()
