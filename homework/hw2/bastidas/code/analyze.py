"""Análisis: resúmenes, taxonomía, refinamiento, costo y figuras.

    python code/analyze.py        (después de run_all.py; no llama al modelo)

Lee results/runs.csv, results/arm_b_attempts.jsonl y problems/problems.json y
escribe los CSV de resumen, taxonomy.md y fig/*.png.
"""
import csv
import json
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arms import coverage_ok                            # noqa: E402
from taxonomy import CATEGORIES, NOMINAL, classify     # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# Precios de referencia de un proveedor hospedado (USD por millón de tokens,
# consultados en noviembre de 2026). qwen2.5:3b no se ofrece hospedado; se usan
# el Qwen más cercano (Together) y el modelo pequeño más barato (Groq).
PRICES = {"together_qwen2.5_7b": (0.30, 0.30), "groq_llama3.1_8b": (0.05, 0.08)}
ARMS = ["A", "B", "B'", "C"]
CAT_ES = {"malformed_syntax": "Sintaxis mala (no parsea)",
          "over_constrained": "Sobre-restringido (sin solución)",
          "under_constrained": "Sub-restringido (varias soluciones, devolvió otra)",
          "wrong_problem": "Modelo válido del problema equivocado",
          "scope_arity": "Alcance / aridad",
          "timeout": "Timeout del solver"}


def load():
    rows = list(csv.DictReader(open(RES / "runs.csv", encoding="utf-8")))
    for r in rows:
        for k in ("level", "n_vars", "n_clues", "rep", "llm_calls", "iterations",
                  "tokens_in", "tokens_out", "prompt_chars", "truncated"):
            r[k] = int(float(r[k])) if r[k] not in ("", None) else 0
        for k in ("llm_time_s", "solver_time_s", "wall_s"):
            r[k] = float(r[k]) if r[k] else 0.0
    attempts = [json.loads(l) for l in open(RES / "arm_b_attempts.jsonl", encoding="utf-8")]
    problems = {p["id"]: p for p in json.loads(
        (ROOT / "problems" / "problems.json").read_text(encoding="utf-8"))["problems"]}
    return rows, attempts, problems


def pct(x, n):
    return 100.0 * x / n if n else 0.0


def p95(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))] if xs else 0.0


def billed_tokens_in(r):
    # Ollama no vuelve a contar el prefijo que ya tiene en su caché KV; un
    # proveedor hospedado cobra todo el prompt. Estimación: 1 token ≈ 4 caracteres.
    return max(r["tokens_in"], r["prompt_chars"] // 4)


def write_csv(name, rows):
    if not rows:
        return
    with open(RES / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# ------------------------------------------------------------------ resumen --
def summarize(rows):
    out = []
    reps = sorted({r["rep"] for r in rows if r["arm"] != "A"})
    for arm in ARMS:
        for label, sel in [("T=0 (principal)", lambda r: r["rep"] == 0),
                           (f"T=0.7 ({len(reps) - 1} réplicas)", lambda r: r["rep"] > 0)]:
            rs = [r for r in rows if r["arm"] == arm and (arm == "A" or sel(r))]
            if not rs or (arm == "A" and label != "T=0 (principal)"):
                continue
            n = len(rs)
            c = sum(r["outcome"] == "correct" for r in rs)
            inc = sum(r["outcome"] == "incorrect" for r in rs)
            na = sum(r["outcome"] == "no_answer" for r in rs)
            fails = [r for r in rs if r["outcome"] != "correct"]
            det = sum(r["detectable"] == "True" for r in fails)
            per_rep = [pct(sum(r["outcome"] == "correct" for r in rs if r["rep"] == k),
                           sum(1 for r in rs if r["rep"] == k)) for k in reps if k > 0] \
                if label.startswith("T=0.7") else []
            out.append({
                "arm": arm, "run": label, "instances": n, "correct": c, "incorrect": inc,
                "no_answer": na, "accuracy_pct": round(pct(c, n), 1),
                "acc_min_rep": round(min(per_rep), 1) if per_rep else "",
                "acc_max_rep": round(max(per_rep), 1) if per_rep else "",
                "failures": len(fails), "failures_detectable": det,
                "detectable_pct": round(pct(det, len(fails)), 1) if fails else "",
                "wall_median_s": round(st.median(r["wall_s"] for r in rs), 3),
                "wall_p95_s": round(p95([r["wall_s"] for r in rs]), 3),
                "llm_time_total_s": round(sum(r["llm_time_s"] for r in rs), 1),
                "solver_time_total_ms": round(1000 * sum(r["solver_time_s"] for r in rs), 2),
                "solver_time_median_ms": round(1000 * st.median(r["solver_time_s"] for r in rs), 3),
                "llm_calls": sum(r["llm_calls"] for r in rs),
                "tokens_in": sum(r["tokens_in"] for r in rs),
                "tokens_in_billed": sum(billed_tokens_in(r) for r in rs),
                "tokens_out": sum(r["tokens_out"] for r in rs),
                "replies_truncated": sum(r["truncated"] for r in rs),
            })
    return out


def by_level(rows):
    out = []
    for arm in ARMS:
        for lv in range(1, 5):
            for rep in sorted({r["rep"] for r in rows if r["arm"] == arm}):
                rs = [r for r in rows if r["arm"] == arm and r["level"] == lv and r["rep"] == rep]
                if rs:
                    out.append({"arm": arm, "level": lv, "rep": rep, "n": len(rs),
                                "correct": sum(r["outcome"] == "correct" for r in rs),
                                "accuracy_pct": round(pct(sum(r["outcome"] == "correct"
                                                              for r in rs), len(rs)), 1)})
    return out


def cost(summary):
    out = []
    for s in summary:
        row = {"arm": s["arm"], "run": s["run"], "correct": s["correct"],
               "instances": s["instances"],
               "tokens_per_attempt": round((s["tokens_in_billed"] + s["tokens_out"]) / s["instances"]),
               "tokens_per_correct": round((s["tokens_in_billed"] + s["tokens_out"]) / s["correct"])
               if s["correct"] else "inf",
               "llm_seconds_per_correct": round(s["llm_time_total_s"] / s["correct"], 2)
               if s["correct"] else "inf"}
        for name, (pin, pout) in PRICES.items():
            usd = (s["tokens_in_billed"] * pin + s["tokens_out"] * pout) / 1e6
            row[f"usd_per_1000_attempts_{name}"] = round(1000 * usd / s["instances"], 4)
            row[f"usd_per_1000_correct_{name}"] = round(1000 * usd / s["correct"], 4) \
                if s["correct"] else "inf"
        out.append(row)
    return out


# ------------------------------------------------------------------ taxonomía --
def taxonomy(rows, attempts, problems):
    """Clasifica CADA falla del brazo B (primer intento) y la respuesta final de B′."""
    by_key = defaultdict(list)
    for a in attempts:
        by_key[(a["problem"], a["rep"])].append(a)
    entries = []
    for (pid, rep), atts in sorted(by_key.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        atts.sort(key=lambda a: a["iteration"])
        p = problems[pid]
        for which, a in (("B", atts[0]), ("B'", atts[-1])):
            cat, info = classify(a, p)
            if a["stage"] == "solved" and a["correct"]:
                if a["n_solutions"] > 1:
                    entries.append({"arm": which, "problem": pid, "rep": rep,
                                    "level": p["level"], "temperature": a["temperature"],
                                    "category": "lucky_under_constrained", "info": info or {},
                                    "attempt": a, "detectable": True, "signal": "non_unique"})
                continue
            if a["stage"] != "solved":
                signal = a["stage"]
            elif a["n_solutions"] > 1:
                signal = "non_unique"
            else:
                signal = coverage_ok(a["solution"], p)[1]
            det = bool(signal)
            entries.append({"arm": which, "problem": pid, "rep": rep, "level": p["level"],
                            "temperature": a["temperature"], "category": cat, "info": info,
                            "attempt": a, "detectable": det, "signal": signal})
    return entries


def taxonomy_counts(entries):
    out = []
    for arm in ("B", "B'"):
        for run, sel in [("T=0", lambda e: e["rep"] == 0), ("T=0.7", lambda e: e["rep"] > 0)]:
            es = [e for e in entries if e["arm"] == arm and sel(e)
                  and e["category"] != "lucky_under_constrained"]
            for cat in CATEGORIES:
                ce = [e for e in es if e["category"] == cat]
                out.append({"arm": arm, "run": run, "category": cat, "count": len(ce),
                            "detectable": sum(e["detectable"] for e in ce),
                            "nominal_detectable": NOMINAL[cat]})
    return out


def causes_counts(entries):
    out = []
    for arm in ("B", "B'"):
        es = [e for e in entries if e["arm"] == arm and e["category"] != "lucky_under_constrained"]
        c = Counter()
        for e in es:
            info = e["info"] or {}
            for key in ("hallucinated", "reversed", "dropped", "alldiff_issues", "missing", "extra"):
                if info.get(key):
                    c[key] += 1
        for key, v in c.most_common():
            out.append({"arm": arm, "cause": key, "failures_with_cause": v, "failures": len(es)})
    return out


def write_taxonomy_md(entries, problems):
    lines = ["# Taxonomía de fallas del brazo B", "",
             "Cada falla del brazo B (primer intento del modelo, sin corrección) en las",
             "cinco corridas (rep 0 a temperatura 0 y reps 1–4 a temperatura 0.7),",
             "clasificada automáticamente por `code/taxonomy.py` y con la salida del modelo",
             "tal cual. Al final están las fallas que sobrevivieron al bucle B′.", "",
             "**Detectable sin la verdad** = el propio sistema lo nota: el JSON no carga, el",
             "solver lo rechaza o prueba que no hay solución, se agota el tiempo, el modelo",
             "admite más de una solución (el enunciado promete una sola) o falta un nombre",
             "del enunciado. Las causas (inventada / invertida / perdida / alldiff) sí usan",
             "el modelo a mano y solo sirven para el análisis.", ""]
    es = [e for e in entries if e["arm"] == "B" and e["category"] != "lucky_under_constrained"]
    lines += ["| Categoría | Fallas (todas las corridas) | Detectables sin verdad |",
              "|---|---|---|"]
    for cat in CATEGORIES:
        ce = [e for e in es if e["category"] == cat]
        lines.append(f"| {CAT_ES[cat]} | {len(ce)} | {sum(e['detectable'] for e in ce)} |")
    lines.append(f"| **Total** | **{len(es)}** | **{sum(e['detectable'] for e in es)}** |")
    lucky = [e for e in entries if e["arm"] == "B" and e["category"] == "lucky_under_constrained"]
    lines += ["", f"Además, {len(lucky)} respuestas de B fueron correctas **por suerte**: el modelo "
              "admitía varias soluciones y el solver devolvió justo la buena.", ""]
    # patrones de causa (comparando con el modelo a mano)
    pat = Counter()
    for e in es:
        info = e["info"] or {}
        kinds = {key: {x.split("(")[0] for x in info.get(key, [])} for key in
                 ("hallucinated", "reversed", "dropped")}
        if "offset" in kinds["reversed"]:
            pat["offset con la dirección invertida (A = B + 1 en vez de B = A + 1)"] += 1
        if "eq" in kinds["hallucinated"]:
            pat["eq inventado entre dos variables o con un número (p. ej. 'next to' → eq)"] += 1
        if any("alldiff del grupo" in x for x in info.get("dropped", [])):
            pat["omitió el alldiff de un grupo ('cada casa es distinta')"] += 1
        if kinds["dropped"] & {"lt", "offset", "next_to", "eq", "neq"}:
            pat["perdió al menos una pista (alguna solución del modelo la viola)"] += 1
        if info.get("missing"):
            pat["no declaró una variable para algún nombre del enunciado"] += 1
        if info.get("alldiff_issues"):
            pat["alldiff con alcance equivocado (mezcla grupos o deja miembros fuera)"] += 1
    lines += ["### Patrones de causa en las fallas de B", "",
              "Una falla puede tener varias causas a la vez, así que la suma pasa del total.", "",
              "| Patrón | Fallas con ese patrón |", "|---|---|"]
    lines += [f"| {k} | {v} de {len(es)} |" for k, v in pat.most_common()]
    lines.append("")

    def entry_md(e, n):
        a, info = e["attempt"], e["info"] or {}
        out = [f"### {n}. {e['problem']} · rep {e['rep']} (T={e['temperature']}) · "
               f"{CAT_ES.get(e['category'], e['category'])}", ""]
        out.append(f"- **Detectable sin verdad:** {'sí' if e['detectable'] else 'no'}"
                   + (f" (señal: `{e['signal']}`)" if e["signal"] else ""))
        if a["stage"] != "solved":
            out.append(f"- **Mensaje del parser/solver:** {a['error']}")
        else:
            out.append(f"- **Soluciones del modelo:** {'≥2' if a['n_solutions'] > 1 else '1'}; "
                       f"devolvió `{json.dumps(a['solution'])}`")
            gold = problems[e["problem"]]["gold"]
            out.append(f"- **Respuesta correcta:** `{json.dumps(gold)}`")
        for key, label in (("missing", "Nombres del enunciado sin variable"),
                           ("alldiff_issues", "Problemas de alcance en alldiff"),
                           ("hallucinated", "Restricciones inventadas (la verdad las viola)"),
                           ("reversed", "Restricciones invertidas"),
                           ("dropped", "Pistas perdidas")):
            if info.get(key):
                out.append(f"- **{label}:** " + "; ".join(f"`{x}`" for x in info[key]))
        text = a["text"] if len(a["text"]) <= 4000 else a["text"][:4000] + "\n... [recortado]"
        out += ["", "<details><summary>Salida del modelo</summary>", "", "```",
                text.replace("```", "'''"), "```", "</details>", ""]
        return out

    n = 0
    for cat in CATEGORIES:
        ce = [e for e in es if e["category"] == cat]
        if not ce:
            continue
        lines += [f"## {CAT_ES[cat]} ({len(ce)})", ""]
        for e in ce:
            n += 1
            lines += entry_md(e, n)
    ep = [e for e in entries if e["arm"] == "B'" and e["category"] != "lucky_under_constrained"]
    lines += [f"## Fallas que sobrevivieron al refinamiento (B′, {len(ep)})", "",
              "| Problema | Rep | Categoría | Detectable | Rondas |", "|---|---|---|---|---|"]
    for e in ep:
        lines.append(f"| {e['problem']} | {e['rep']} | {CAT_ES[e['category']]} | "
                     f"{'sí' if e['detectable'] else 'no'} | {e['attempt']['iteration']} |")
    (ROOT / "taxonomy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ refinamiento --
def refinement(attempts, rows):
    by_key = defaultdict(list)
    for a in attempts:
        by_key[(a["problem"], a["rep"])].append(a)
    out = []
    for (pid, rep), atts in by_key.items():
        atts.sort(key=lambda a: a["iteration"])
        first, last = atts[0], atts[-1]
        if first["stage"] == "solved":
            kind = "solved_first_try" if first["correct"] else "wrong_first_try (no feedback)"
            it_success = 0 if first["correct"] else ""
        else:
            ok_at = next((a["iteration"] for a in atts if a["stage"] == "solved" and a["correct"]), None)
            if ok_at is not None:
                kind, it_success = "fixed_by_feedback", ok_at
            elif last["stage"] == "solved":
                kind, it_success = "feedback_to_wrong_answer", ""
            else:
                kind, it_success = "never_converged", ""
        out.append({"problem": pid, "rep": rep, "level": int(pid[1]),
                    "first_stage": first["stage"], "final_stage": last["stage"],
                    "rounds": len(atts) - 1, "kind": kind, "iterations_to_success": it_success,
                    "stages": " > ".join(a["stage"] for a in atts)})
    out.sort(key=lambda r: (r["rep"], r["problem"]))
    return out


def refinement_by_category(ref, entries):
    """¿Las fallas que se arreglan en 1 ronda son de otra clase que las que
    sobreviven 3? Cruza la categoría del PRIMER intento con lo que pasó en B′."""
    cat = {(e["problem"], e["rep"]): e["category"] for e in entries if e["arm"] == "B"}
    table = defaultdict(Counter)
    for r in ref:
        c = cat.get((r["problem"], r["rep"]))
        if c is None or c == "lucky_under_constrained":
            continue
        k = r["kind"]
        if k == "fixed_by_feedback":
            k = f"fixed_in_{r['iterations_to_success']}"
        table[c][k] += 1
    kinds = ["fixed_in_1", "fixed_in_2", "fixed_in_3", "feedback_to_wrong_answer",
             "never_converged", "wrong_first_try (no feedback)"]
    return [{"first_category": c, **{k: table[c][k] for k in kinds},
             "total": sum(table[c].values())} for c in CATEGORIES if table[c]]


def reproducibility(rows):
    out = []
    for arm in ("B", "B'", "C"):
        per = defaultdict(list)
        for r in rows:
            if r["arm"] == arm and r["rep"] > 0:
                per[r["problem"]].append(r["answer"] or r["outcome"])
        distinct = [len(set(v)) for v in per.values()]
        n = max((len(v) for v in per.values()), default=0)
        out.append({"arm": arm, "problems": len(per), "runs_per_problem_T0.7": n,
                    "median_distinct_answers": st.median(distinct) if distinct else "",
                    "problems_all_runs_identical": sum(d == 1 for d in distinct)})
    return out


def main():
    rows, attempts, problems = load()
    summary = summarize(rows)
    write_csv("summary_by_arm.csv", summary)
    write_csv("accuracy_by_level.csv", by_level(rows))
    write_csv("cost.csv", cost(summary))
    entries = taxonomy(rows, attempts, problems)
    write_csv("taxonomy_counts.csv", taxonomy_counts(entries))
    write_csv("taxonomy_causes.csv", causes_counts(entries))
    write_csv("taxonomy_entries.csv", [
        {"arm": e["arm"], "problem": e["problem"], "rep": e["rep"], "level": e["level"],
         "category": e["category"], "detectable": e["detectable"], "signal": e["signal"],
         "stage": e["attempt"]["stage"], "iteration": e["attempt"]["iteration"],
         "error": e["attempt"]["error"],
         "hallucinated": "; ".join((e["info"] or {}).get("hallucinated", [])),
         "reversed": "; ".join((e["info"] or {}).get("reversed", [])),
         "dropped": "; ".join((e["info"] or {}).get("dropped", [])),
         "alldiff_issues": "; ".join((e["info"] or {}).get("alldiff_issues", [])),
         "missing": "; ".join((e["info"] or {}).get("missing", []))} for e in entries])
    write_taxonomy_md(entries, problems)
    ref = refinement(attempts, rows)
    write_csv("refinement.csv", ref)
    write_csv("refinement_by_category.csv", refinement_by_category(ref, entries))
    write_csv("reproducibility.csv", reproducibility(rows))
    import plots
    plots.main()
    for s in summary:
        print(f"{s['arm']:<3} {s['run']:<20} {s['correct']:>3}/{s['instances']:<3} "
              f"({s['accuracy_pct']}%)  fallas detectables {s['failures_detectable']}/{s['failures']}")


if __name__ == "__main__":
    main()
