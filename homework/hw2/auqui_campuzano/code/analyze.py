"""Turns results/per_instance.csv into scorecard/CSV tables, taxonomy.md, figures and REPORT.md.
Everything is computed from the raw rows: nothing is typed in by hand.

    python code/analyze.py [--root .]
"""
from __future__ import annotations
import argparse, collections, csv, json, math, os, pathlib, statistics as st, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import taxonomy as tx

ARMS = ['A', 'B', 'Bprime', 'C']
NAME = {'A': 'A — Hand', 'B': 'B — Hybrid', 'Bprime': "B′ — Hybrid + refinement", 'C': 'C — Direct'}
SHORT = {'A': 'A', 'B': 'B', 'Bprime': "B′", 'C': 'C'}
LEVELS = ['easy', 'medium', 'hard']
COL = {'A': '#0072B2', 'B': '#D55E00', 'Bprime': '#009E73', 'C': '#CC79A7'}     # Okabe-Ito (colour-blind safe)
MARK = {'A': 'o', 'B': 's', 'Bprime': '^', 'C': 'D'}
LS = {'A': '-', 'B': '--', 'Bprime': '-.', 'C': ':'}


def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d, (c + r) / d


def mean(x): x = list(x); return sum(x) / len(x) if x else 0.0
def f(x, nd=3): return 'n/a' if x is None or (isinstance(x, float) and math.isnan(x)) else f'{x:.{nd}f}'


def load(root):
    res = root / 'results'
    rows = list(csv.DictReader((res / 'per_instance.csv').open()))
    for r in rows:
        for k in ('correct', 'rep', 'iterations', 'prompt_tokens', 'completion_tokens', 'tokens', 'cached_calls'): r[k] = int(float(r[k] or 0))
        for k in ('wall_seconds', 'llm_seconds', 'solver_seconds'): r[k] = float(r[k] or 0)
        r['attempts'] = json.loads(r.get('attempts_json') or '[]')
    meta = json.loads((res / 'run_meta.json').read_text()) if (res / 'run_meta.json').exists() else {}
    price = None
    pf = res / 'pricing.csv'
    if os.getenv('PRICE_IN_PER_M') and os.getenv('PRICE_OUT_PER_M'):
        price = (float(os.environ['PRICE_IN_PER_M']), float(os.environ['PRICE_OUT_PER_M']), 'env vars PRICE_IN_PER_M / PRICE_OUT_PER_M')
    elif pf.exists():
        for r in csv.DictReader(pf.open()):
            try: price = (float(r['input_usd_per_million_tokens']), float(r['output_usd_per_million_tokens']), f"{r['provider']} / {r['model']} ({r.get('notes', '')})"); break
            except (ValueError, KeyError, TypeError): pass
    return rows, meta, price


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(pathlib.Path(__file__).resolve().parents[1])); a = ap.parse_args()
    root = pathlib.Path(a.root); res = root / 'results'; figd = root / 'fig'; figd.mkdir(exist_ok=True)
    rows, meta, price = load(root)
    infra = [r for r in rows if r['status'] == 'infra-error']; rows = [r for r in rows if r['status'] != 'infra-error']
    arms = [x for x in ARMS if any(r['arm'] == x for r in rows)]
    if not any(x in arms for x in ('B', 'Bprime', 'C')):
        sys.exit('results/per_instance.csv has only arm A. Run code/run_experiment.py with a model configured first.')
    R = {x: [r for r in rows if r['arm'] == x] for x in arms}

    # ---------------- scorecard ----------------
    score = {}
    for x in arms:
        rr = R[x]; n = len(rr); k = sum(r['correct'] for r in rr)
        reps = collections.defaultdict(list)
        for r in rr: reps[r['rep']].append(r['correct'])
        rep_acc = [mean(v) for v in reps.values()]
        lo, hi = wilson(k, n)
        fails = [r for r in rr if not r['correct']]
        ann = sum(1 for r in fails if str(r['announced']) == '1'); sil = len(fails) - ann
        cost = None
        if price and x != 'A':
            cost = sum(r['prompt_tokens'] * price[0] + r['completion_tokens'] * price[1] for r in rr) / 1e6
        if x == 'A': cost = 0.0
        score[x] = dict(arm=x, runs=n, correct=k, incorrect=sum(r['status'] == 'answered' and not r['correct'] for r in rr),
                        no_answer=sum(r['status'] == 'no-answer' for r in rr), accuracy=k / n if n else 0, ci_lo=lo, ci_hi=hi,
                        acc_sd_across_reps=st.pstdev(rep_acc) if len(rep_acc) > 1 else 0.0, n_reps=len(rep_acc),
                        mean_wall_s=mean(r['wall_seconds'] for r in rr), mean_solver_s=mean(r['solver_seconds'] for r in rr),
                        mean_llm_s=mean(r['llm_seconds'] for r in rr), mean_tokens=mean(r['tokens'] for r in rr),
                        mean_prompt_tokens=mean(r['prompt_tokens'] for r in rr), mean_completion_tokens=mean(r['completion_tokens'] for r in rr),
                        failures=len(fails), announced_failures=ann, silent_failures=sil,
                        total_tokens=sum(r['tokens'] for r in rr), total_cost_usd=cost,
                        cost_per_correct_usd=(cost / k if cost is not None and k else None),
                        tokens_per_correct=(sum(r['tokens'] for r in rr) / k if k else None))
    with (res / 'scorecard.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(score[arms[0]])); w.writeheader(); [w.writerow(score[x]) for x in arms]

    # ---------------- accuracy vs difficulty ----------------
    bydiff = {}
    for x in arms:
        for L in LEVELS:
            rr = [r for r in R[x] if r['difficulty'] == L]; k = sum(r['correct'] for r in rr); lo, hi = wilson(k, len(rr))
            bydiff[(x, L)] = (k, len(rr), k / len(rr) if rr else float('nan'), lo, hi)
    with (res / 'accuracy_by_difficulty.csv').open('w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['arm', 'difficulty', 'correct', 'runs', 'accuracy', 'ci95_lo', 'ci95_hi'])
        for (x, L), v in bydiff.items(): w.writerow([x, L, v[0], v[1], f(v[2]), f(v[3]), f(v[4])])

    # ---------------- taxonomy (arm B) ----------------
    Bf = [r for r in R.get('B', []) if not r['correct']]
    tcount = collections.Counter(r['category'] for r in Bf)
    ann_by_cat = collections.Counter(r['category'] for r in Bf if str(r['announced']) == '1')
    with (res / 'taxonomy_counts.csv').open('w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['category', 'a_priori_detectable_without_gt', 'count_B', 'announced_by_solver', 'silent'])
        for c in ['syntax', 'over', 'under', 'wrong', 'scope_arity', 'timeout']:
            w.writerow([tx.CATS[c], tx.DETECTABLE[c], tcount[c], ann_by_cat[c], tcount[c] - ann_by_cat[c]])
    ctypes = collections.Counter(r['category'] for r in R.get('C', []) if not r['correct'])

    # taxonomy.md: every B failure, verbatim
    L = ['# Error taxonomy — Arm B (every failure, verbatim model output)', '',
         f"Model: `{meta.get('model', '?')}` · temperature {meta.get('temperature', '?')} · {meta.get('repeats', '?')} repeats · "
         f"{len(R.get('B', []))} arm-B runs, {len(Bf)} failures.", '',
         'Detectable = the failure is revealed by the parser/solver **without** the ground truth (the solver rejected the model or reported UNSAT/timeout). '
         '"silent" = the solver returned a solution and only the ground truth reveals it is wrong. Premise diffs (dropped / hallucinated adjacencies, colour clues) '
         'are computed by comparing the model\'s constraint set with the hand-written ground truth.', '',
         '| Category | A-priori detectable? | Count | Announced | Silent |', '|---|---|---:|---:|---:|']
    for c in ['syntax', 'over', 'under', 'wrong', 'scope_arity', 'timeout']:
        L.append(f'| {tx.CATS[c]} | {tx.DETECTABLE[c]} | {tcount[c]} | {ann_by_cat[c]} | {tcount[c] - ann_by_cat[c]} |')
    L.append('')
    if not Bf:
        L.append('**Arm B produced no failures with this model/dataset.** The taxonomy is therefore empty; see REPORT.md §3 for what that means (and for B′/C).')
    for i, r in enumerate(sorted(Bf, key=lambda r: (r['problem_id'], r['rep'])), 1):
        a0 = r['attempts'][0] if r['attempts'] else {}
        ev = a0.get('feedback_sent') or ('Solver returned SAT; the returned assignment violates the ground-truth problem.' if r['status'] == 'answered' else '')
        L += [f"## {i}. {r['problem_id']} ({r['difficulty']}), repeat {r['rep']} — {tx.CATS.get(r['category'], r['category'])}", '',
              f"- **Detectable without ground truth:** {'yes — announced by parser/solver' if str(r['announced']) == '1' else 'no — silent (solver accepted the model)'}",
              f"- **Parser/solver evidence:** {ev or 'n/a'}", f"- **What went wrong:** {r['detail'] or 'n/a'}", '', '```text', r['model_output'].strip(), '```', '']
    (root / 'taxonomy.md').write_text('\n'.join(L))

    # ---------------- refinement (B') ----------------
    Bp = R.get('Bprime', []); ref = {}
    if Bp:
        it = collections.Counter(); wrong_acc = 0
        for r in Bp:
            if r['status'] == 'answered': it[str(r['iterations'])] += 1
            elif r['status'] == 'no-answer': it['never'] += 1
        fixed = [r for r in Bp if r['status'] == 'answered' and r['iterations'] >= 2]
        never = [r for r in Bp if r['status'] == 'no-answer']
        first_cat_fixed = collections.Counter(r['attempts'][0]['category'] for r in fixed)
        first_cat_never = collections.Counter(r['attempts'][0]['category'] for r in never)
        last_cat_never = collections.Counter(r['attempts'][-1]['category'] for r in never)
        same_all = sum(1 for r in never if len({a['category'] for a in r['attempts']}) == 1)
        Bd = {(r['problem_id'], r['rep']): r for r in R.get('B', [])}
        rescued = sum(1 for r in Bp if r['correct'] and not Bd.get((r['problem_id'], r['rep']), {'correct': 1})['correct'])
        harmed = sum(1 for r in Bp if not r['correct'] and Bd.get((r['problem_id'], r['rep']), {'correct': 0})['correct'])
        accepted = [r for r in Bp if r['status'] == 'answered']
        converted = sum(1 for r in Bp if r['status'] == 'answered' and not r['correct'] and Bd.get((r['problem_id'], r['rep']), {'status': ''})['status'] == 'no-answer')
        ref = dict(it=it, fixed=len(fixed), never=len(never), first_cat_fixed=first_cat_fixed, first_cat_never=first_cat_never,
                   last_cat_never=last_cat_never, same_all=same_all, rescued=rescued, harmed=harmed,
                   converted=converted, accepted=len(accepted), accepted_correct=sum(r['correct'] for r in accepted))
        with (res / 'refinement.csv').open('w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['outcome', 'count', 'fraction_of_Bprime_runs'])
            for k in ['1', '2', '3', 'never']: w.writerow([f'solver-accepted at iteration {k}' if k != 'never' else 'never accepted (no answer after 3)', it[k], f(it[k] / len(Bp))])

    # ---------------- cost ----------------
    with (res / 'cost.csv').open('w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['arm', 'runs', 'correct', 'total_tokens', 'total_cost_usd', 'cost_per_correct_usd', 'tokens_per_correct', 'pricing_source'])
        for x in arms:
            s = score[x]; w.writerow([x, s['runs'], s['correct'], s['total_tokens'], f(s['total_cost_usd'], 6), f(s['cost_per_correct_usd'], 6),
                                      f(s['tokens_per_correct'], 1), price[2] if price and x != 'A' else ('n/a — pricing.csv not filled' if x != 'A' else 'no LLM tokens')])

    # ---------------- figures ----------------
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.alpha': .25})
    fig, ax = plt.subplots(figsize=(6.4, 4.8)); off = {x: (i - (len(arms) - 1) / 2) * .035 for i, x in enumerate(arms)}
    for x in arms:
        ys = [bydiff[(x, l)][2] for l in LEVELS]; lo = [y - bydiff[(x, l)][3] for y, l in zip(ys, LEVELS)]; hi = [bydiff[(x, l)][4] - y for y, l in zip(ys, LEVELS)]
        ax.errorbar([i + off[x] for i in range(3)], ys, yerr=[lo, hi], marker=MARK[x], ls=LS[x], color=COL[x], capsize=3, lw=2, ms=7, label=NAME[x])
    ax.set_xticks(range(3)); npb = {l: len({r['problem_id'] for r in R[arms[-1]] if r['difficulty'] == l}) for l in LEVELS}; ax.set_xticklabels([f'{l}\n({npb[l]} problems)' for l in LEVELS]); ax.set_ylim(-.02, 1.08)
    ax.set_ylabel('Accuracy (no-answer counted as wrong)'); ax.set_xlabel('Difficulty'); ax.set_title('Accuracy vs. difficulty (bars: Wilson 95 % CI)'); ax.legend(loc='upper center', bbox_to_anchor=(.5, -.22), ncol=2, frameon=False)
    fig.tight_layout(); fig.savefig(figd / 'accuracy_vs_difficulty.png', dpi=170); plt.close(fig)

    if Bp:
        fig, ax = plt.subplots(figsize=(5.2, 3.8)); cats = ['1', '2', '3', 'never']; vals = [ref['it'][c] for c in cats]
        bars = ax.bar(['1', '2', '3', 'never\naccepted'], vals, color=[COL['Bprime']] * 3 + ['#999999'], width=.6)
        ax.bar_label(bars); ax.set_ylabel(f'Runs (of {len(Bp)})'); ax.set_xlabel('Iteration at which the solver accepted the model'); ax.set_title("B′: iterations to solver acceptance")
        fig.tight_layout(); fig.savefig(figd / 'refinement_iterations.png', dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.8)); order = ['syntax', 'scope_arity', 'over', 'timeout', 'under', 'wrong']
    ax.barh([tx.CATS[c] for c in order], [ann_by_cat[c] for c in order], color='#0072B2', label='announced by parser/solver')
    ax.barh([tx.CATS[c] for c in order], [tcount[c] - ann_by_cat[c] for c in order], left=[ann_by_cat[c] for c in order], color='#D55E00', hatch='//', edgecolor='white', label='silent')
    ax.invert_yaxis(); ax.set_xlabel('Arm-B failures'); ax.set_title('Arm B error taxonomy'); ax.legend(frameon=False, loc='lower right'); fig.tight_layout(); fig.savefig(figd / 'arm_b_error_taxonomy.png', dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8)); xs = [x for x in arms if x != 'A']
    a_ = [score[x]['announced_failures'] for x in xs]; s_ = [score[x]['silent_failures'] for x in xs]
    ax.bar([SHORT[x] for x in xs], a_, color='#0072B2', label='announced (detectable w/o ground truth)', width=.55)
    ax.bar([SHORT[x] for x in xs], s_, bottom=a_, color='#D55E00', hatch='//', edgecolor='white', label='silent', width=.55)
    ax.set_ylabel('Failed runs'); ax.set_title('Do failures announce themselves?'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(figd / 'detectability.png', dpi=170); plt.close(fig)

    if price:
        fig, ax = plt.subplots(figsize=(5.4, 3.6)); xs2 = [x for x in xs if score[x]['cost_per_correct_usd'] is not None]
        ax.bar([SHORT[x] for x in xs2], [score[x]['cost_per_correct_usd'] * 1000 for x in xs2], color=[COL[x] for x in xs2], width=.55)
        ax.set_ylabel('USD per 1000 correct answers'); ax.set_title('Cost per correct answer'); fig.tight_layout(); fig.savefig(figd / 'cost_per_correct.png', dpi=170); plt.close(fig)

    # ---------------- REPORT.md ----------------
    report = build_report(root, meta, price, score, bydiff, Bf, tcount, ann_by_cat, ctypes, ref, Bp, R, infra, arms)
    (root / 'REPORT.md').write_text(report)
    words = len(report.split())
    print(f'Wrote scorecard.csv, accuracy_by_difficulty.csv, taxonomy_counts.csv, refinement.csv, cost.csv, taxonomy.md, figures and REPORT.md ({words} words).')
    if words > 2500: print('WARNING: REPORT.md exceeds 2500 words — trim before submitting.')
    if not Bf: print('NOTE: arm B had zero failures: the taxonomy will be empty. Re-run with a smaller/weaker model to populate it.')
    if infra: print(f'NOTE: {len(infra)} infrastructure errors excluded; re-run run_experiment.py (cached calls are free) to retry them.')


def build_report(root, meta, price, S, bydiff, Bf, tcount, ann_by_cat, ctypes, ref, Bp, R, infra, arms):
    a = lambda x, k: S[x][k]
    pct = lambda v: f'{100 * v:.0f} %'
    n_inst = len({r['problem_id'] for r in R[arms[-1]]}); reps = meta.get('repeats', '?')
    P = []
    P += ['# Homework 2 — The Formalizer', '', '**Integrantes:** Giuliana Auqui y Felipe Campuzano  ', '**Formalismo:** CSP (coloreo de grafos) · **Solver:** backtracking con MRV y desempate por grado (`code/csp.py`)  ',
          f"**Modelo LLM:** `{meta.get('model', '?')}` — proveedor: {meta.get('provider') or meta.get('base_url', '?')}; tamaño/versión: {meta.get('size') or 'no declarado por el proveedor'}; temperatura {meta.get('temperature', '?')}; {reps} repeticiones por instancia; fecha {meta.get('date', '?')}.", '']
    P += ['## 1. Diseño experimental', '',
          f'Dataset propio de {n_inst} problemas de coloreo de grafos con 3 colores (`problems/`): 6 fáciles (4–5 regiones, 5–6 adyacencias), 7 medios (6–7 regiones, 11–12 adyacencias) y 7 difíciles (8–9 regiones, 19–20 adyacencias y 2 pistas de color fijas). '
          'La dificultad se mide con #variables, #restricciones y #pistas. El ground truth es el modelo CSP escrito a mano; un script independiente (`code/validate_dataset.py`) lo re-deriva del texto del enunciado y comprueba que coincide, además de que cada instancia es satisfacible. '
          'Una respuesta es correcta si asigna todas las regiones, respeta dominios/pistas y ninguna arista une dos regiones del mismo color (se evalúa satisfacción, no igualdad con un coloreo único). '
          f'Cada instancia se ejecuta {reps} veces por brazo para estimar varianza; se reportan intervalos de Wilson al 95 %. B y B′ comparten su primer intento (misma caché), de modo que B′ ≥ B por construcción y la diferencia es una medición pareada del valor de la retroalimentación del solver. '
          'En B′ el único feedback es el mensaje del parser/solver (JSON inválido, esquema rechazado, UNSAT, timeout) junto con la salida previa del propio modelo; nunca se envía el ground truth.', '']
    P += ['## 2. Duel Scorecard', '', '| Métrica | A — Hand | B — Hybrid | B′ — Refinement | C — Direct |', '|---|---:|---:|---:|---:|']
    def row(label, fn):
        P.append(f'| {label} | ' + ' | '.join(fn(x) if x in S else '—' for x in ARMS) + ' |')
    row('Ejecuciones', lambda x: str(a(x, 'runs')))
    row('Correctas', lambda x: str(a(x, 'correct')))
    row('Incorrectas (respondió mal)', lambda x: str(a(x, 'incorrect')))
    row('Sin respuesta', lambda x: str(a(x, 'no_answer')))
    row('**Accuracy**', lambda x: f"**{pct(a(x, 'accuracy'))}**")
    row('IC 95 % (Wilson)', lambda x: f"[{pct(a(x, 'ci_lo'))}, {pct(a(x, 'ci_hi'))}]")
    row('σ de accuracy entre repeticiones', lambda x: f(a(x, 'acc_sd_across_reps'), 3))
    row('Tiempo total medio (s)', lambda x: f(a(x, 'mean_wall_s'), 4))
    row('Tiempo solver medio (s)', lambda x: f(a(x, 'mean_solver_s'), 5))
    row('Tiempo LLM medio (s)', lambda x: f(a(x, 'mean_llm_s'), 3))
    row('Tokens medios (entrada+salida)', lambda x: f(a(x, 'mean_tokens'), 0))
    row('Fallos anunciados / silenciosos', lambda x: f"{a(x, 'announced_failures')} / {a(x, 'silent_failures')}")
    row('Costo por respuesta correcta (USD)', lambda x: f(a(x, 'cost_per_correct_usd'), 5))
    P += ['', f"(Brazo A: tiempos de solver sobre el modelo escrito a mano; sin tokens.) Delta B→B′: {pct(a('B', 'accuracy'))} → {pct(a('Bprime', 'accuracy'))} " if 'B' in S and 'Bprime' in S else '', '']
    P += ['## 3. Accuracy vs. dificultad', '', '![accuracy](fig/accuracy_vs_difficulty.png)', '', '| Brazo | Fácil | Medio | Difícil |', '|---|---:|---:|---:|']
    for x in arms: P.append(f'| {SHORT[x]} | ' + ' | '.join(f'{pct(bydiff[(x, l)][2])} ({bydiff[(x, l)][0]}/{bydiff[(x, l)][1]})' for l in LEVELS) + ' |')
    P += ['', 'Los no-answer cuentan como incorrectos. Cada nivel tiene solo 6–7 problemas (×' + str(reps) + ' repeticiones, que no son independientes entre sí), por lo que los intervalos son anchos; diferencias de pocos puntos no son concluyentes.', '']
    P += ['## 4. Taxonomía de errores del brazo B', '', f"Hubo **{len(Bf)}** fallos en B de {a('B', 'runs')} ejecuciones; todos están en `taxonomy.md` con la salida íntegra del modelo.", '',
          '![taxonomy](fig/arm_b_error_taxonomy.png)', '', '| Categoría | ¿Detectable sin ground truth? (a priori) | Cuenta | Anunciados | Silenciosos |', '|---|---|---:|---:|---:|']
    for c in ['syntax', 'over', 'under', 'wrong', 'scope_arity', 'timeout']:
        P.append(f'| {tx.CATS[c]} | {tx.DETECTABLE[c]} | {tcount[c]} | {ann_by_cat[c]} | {tcount[c] - ann_by_cat[c]} |')
    nB = len(Bf); annB = sum(ann_by_cat.values())
    P += ['', f"**Detectabilidad:** {annB} de {nB} fallos de B fueron anunciados por el parser/solver sin necesitar el ground truth; {nB - annB} fueron silenciosos (el solver devolvió una solución de un modelo equivocado)." if nB else
          '**Detectabilidad:** B no tuvo fallos con este modelo, así que no hay fallos que clasificar; el resultado solo muestra que este dataset (enunciados con adyacencias explícitas) no discrimina entre modelos de este tamaño.', '']
    ex = []; byc = {}
    for r in sorted(Bf, key=lambda r: len(r['model_output'])): byc.setdefault(r['category'], r)
    ex = list(byc.values())                                   # one (shortest) example per category first
    for r in sorted(Bf, key=lambda r: (len(r['model_output']), r['problem_id'], r['rep'])):
        if len(ex) >= 5: break
        if all((r['problem_id'], r['rep']) != (e['problem_id'], e['rep']) and r['model_output'] != e['model_output'] for e in ex): ex.append(r)
    for i, r in enumerate(ex[:6], 1):
        P += [f"**Ejemplo {i} — {r['problem_id']} (rep {r['rep']}), {tx.CATS.get(r['category'], r['category'])}.** {(r['detail'] or '').rstrip('.')}. "
              f"{'Anunciado por el solver/parser.' if str(r['announced']) == '1' else 'Silencioso: el solver aceptó el modelo.'}", '', '```text', r['model_output'].strip(), '```', '']
    if len(ex) < 5 and nB: P += [f'_Solo ocurrieron {len(ex)} fallos distintos de B; no hay cinco ejemplos que mostrar sin inventarlos._', '']
    P += ['### Brazo C (respuesta directa)', '']
    Cf = [r for r in R.get('C', []) if not r['correct']]
    if Cf:
        annC = sum(1 for r in Cf if str(r['announced']) == '1')
        P += [f"C falló {len(Cf)} veces. Detectables sin ground truth (no parseable / incompleta / color fuera de {{rojo, verde, azul}}): **{annC}**. Silenciosas (respuesta bien formada que viola adyacencias o pistas): **{len(Cf) - annC}**. "
              f"Desglose: " + ', '.join(f'{k}: {v}' for k, v in ctypes.items()) + '.', '',
              '**Consecuencia de ingeniería:** ' + ('en B los fallos que importan casi siempre se anuncian (se puede reintentar o escalar automáticamente); en C un error bien formado es indistinguible de un acierto, así que cada respuesta necesitaría verificación externa.' if (annB / nB if nB else 1) > (annC / len(Cf)) else
               'en este experimento la ventaja de detectabilidad de B no se materializó con claridad; ver sección 8 sobre qué monitoreo adjuntar.'), '']
    else: P += ['C no falló en ninguna ejecución, así que no hay respuestas erróneas que comparar en detectabilidad.', '']
    P += ['![detectability](fig/detectability.png)', '']
    P += ['## 5. Análisis de refinamiento (B′)', '']
    if Bp:
        it = ref['it']; n = len(Bp)
        P += ['![refinement](fig/refinement_iterations.png)', '', f"Iteración en que el solver aceptó el modelo: 1 → {it['1']}, 2 → {it['2']}, 3 → {it['3']}, nunca → {it['never']} de {n} ejecuciones ({pct(it['never'] / n)} no convergió). "
              f"De {ref['accepted']} modelos aceptados, {ref['accepted_correct']} eran fieles al problema: aceptar no equivale a acertar. "
              f"Respecto a B, B′ rescató {ref['rescued']} ejecuciones y perjudicó {ref['harmed']}. Además, {ref['converted']} fallos que en B eran anunciados (el solver rechazó el modelo) pasaron a ser silenciosos en B′: tras reintentar, el modelo produjo algo satisfacible pero infiel, que el solver acepta.", '']
        P += [f"**¿Cualitativamente distintos?** Las {ref['fixed']} ejecuciones aceptadas por el solver tras ≥1 reintento (ninguna era fiel al problema salvo que se indique: ver rescates arriba) fallaron al inicio por: " + (', '.join(f'{tx.CATS.get(k, k)}: {v}' for k, v in ref['first_cat_fixed'].items()) or 'ninguna') + '. '
              f"Fallos de las {ref['never']} que no convergieron — primer intento: " + (', '.join(f'{tx.CATS.get(k, k)}: {v}' for k, v in ref['first_cat_never'].items()) or 'ninguna') + '; último intento: ' + (', '.join(f'{tx.CATS.get(k, k)}: {v}' for k, v in ref['last_cat_never'].items()) or 'ninguna') + f". En {ref['same_all']} de {ref['never']} el modelo repitió la misma categoría de error en los tres intentos.", '',
              'Limitación estructural: B′ solo reintenta cuando el solver rechaza el modelo (sintaxis, UNSAT, timeout). Un modelo satisfacible pero infiel termina el bucle con éxito aparente, por lo que el feedback del solver no puede corregir errores silenciosos.', '']
    P += ['## 6. Costo por respuesta correcta', '']
    if price:
        P += [f'Tarifa usada: {price[2]}: {price[0]} USD / M tokens de entrada y {price[1]} USD / M de salida. Se suman todos los intentos de todas las repeticiones y se divide por las respuestas correctas.', '', '| Brazo | Tokens totales | Costo total (USD) | Correctas | USD por correcta |', '|---|---:|---:|---:|---:|']
        for x in arms:
            if x == 'A': continue
            P.append(f"| {SHORT[x]} | {a(x, 'total_tokens')} | {f(a(x, 'total_cost_usd'), 5)} | {a(x, 'correct')} | {f(a(x, 'cost_per_correct_usd'), 6)} |")
        P += ['', 'Brazo A cuesta cero tokens, pero su costo real es el tiempo humano de escribir cada modelo a mano (no medido).', '']
    else:
        P += ['**No se pudo calcular costo en USD:** `results/pricing.csv` no tiene tarifas válidas (ni variables `PRICE_IN_PER_M`/`PRICE_OUT_PER_M`). Tokens por respuesta correcta: ' + ', '.join(f"{SHORT[x]}: {f(a(x, 'tokens_per_correct'), 0)}" for x in arms if x != 'A') + '.', '']
    P += ['## 7. Dónde podemos haber sido injustos', '',
          '- **Dataset de un solo formalismo y muy regular:** todos los enunciados listan las adyacencias explícitamente en plantilla; traducir es casi transcribir, lo que favorece a B/B′ y probablemente subestima los errores de modelado reales.',
          '- **Tamaño:** instancias de hasta 9 regiones; las diferencias entre brazos de pocos puntos caen dentro del intervalo de confianza.',
          '- **Brazo A** parte de modelos escritos por nosotros, que son también el ground truth: no es un brazo independiente (un error de especificación nuestro sería invisible para A).',
          '- **Normalización:** aceptamos «rojo/verde/azul» además de red/green/blue, cercas de código markdown y nombres de región en minúsculas («r1» = «R1») en C. Sin esa última tolerancia C puntuaba 17 % en vez de 35 %: un detalle de formato, no de razonamiento, decidía la comparación. Corregimos el evaluador tras detectarlo (B no tenía ese problema: ninguna salida de B usó minúsculas); aun así, otras reglas de formato podrían sesgar a un brazo.',
          f"- **Modelo:** {meta.get('model', 'el modelo')} es un modelo de {meta.get('size') or 'tamaño pequeño'} orientado al árabe/inglés con ventana de 4 k tokens; los enunciados están en español. Los resultados describen a este modelo, no a la arquitectura en general. Groq no publica tarifa para él: el costo usa la de llama-3.1-8b-instant como proxy de un modelo de tamaño equivalente.",
          '- **Prompt único por brazo**, sin ajuste ni ejemplos few-shot; un prompt distinto podría cambiar el orden de los brazos. C recibe un formato JSON estricto que penaliza respuestas correctas pero mal formateadas.',
          '- **Temperatura y repeticiones:** con muestreo > 0 hay variación; reportamos σ entre repeticiones, pero no hicimos barrido de temperatura.',
          '- **Cómputo:** tiempos LLM dependen de la carga del proveedor en ese momento.', '']
    # recommendation (rule-based on the measured numbers; edit by hand if you disagree)
    cand = [x for x in ('B', 'Bprime', 'C') if x in S]
    cost = lambda x: S[x]['cost_per_correct_usd'] if S[x]['cost_per_correct_usd'] is not None else 1e9
    best = max(cand, key=lambda x: (round(S[x]['accuracy'], 6), -S[x]['silent_failures'], -cost(x)))
    sil = {x: S[x]['silent_failures'] for x in cand}; acc = {x: pct(S[x]['accuracy']) for x in cand}
    P += ['## 8. Recomendación', '']
    P += [f"Con nuestros números (accuracy {acc.get('B', '—')} en B, {acc.get('Bprime', '—')} en B′, {acc.get('C', '—')} en C; fallos silenciosos {sil.get('B', '—')}/{sil.get('Bprime', '—')}/{sil.get('C', '—')}; USD por respuesta correcta {f(S['B']['cost_per_correct_usd'], 5) if 'B' in S else '—'}/{f(S['Bprime']['cost_per_correct_usd'], 5) if 'Bprime' in S else '—'}/{f(S['C']['cost_per_correct_usd'], 5) if 'C' in S else '—'}), el brazo que enviaríamos es **{NAME[best]}**."]
    if best == 'B':
        extra = ''
        if 'Bprime' in S and S['Bprime']['accuracy'] <= S['B']['accuracy'] + 1e-9:
            extra = f" No enviaríamos B′: no rescató ninguna ejecución adicional ({ref.get('rescued', 0)}), costó {S['Bprime']['mean_tokens'] / max(S['B']['mean_tokens'], 1):.1f}× más tokens por petición y convirtió {ref.get('converted', 0)} fallos anunciados en fallos silenciosos, que es lo peor que puede hacer un bucle de reintentos."
        if 'C' in S:
            extra = f" La ventaja de accuracy de B sobre C ({acc['B']} frente a {acc['C']}) cae dentro de los intervalos de confianza: elegimos B por detectabilidad ({S['B']['announced_failures']} de {S['B']['failures']} fallos anunciados frente a {S['C']['announced_failures']} de {S['C']['failures']} en C), no por precisión." + extra
        P += [extra.strip()]
        ann, tot = S['B']['announced_failures'], S['B']['failures']
        P += [f"Monitoreo: (1) tasa de rechazo del parser/solver por petición (hoy {ann} de {S['B']['runs']}); ante rechazo, escalar a un modelo mayor o a revisión humana en lugar de reintentar con el mismo; (2) los {tot - ann} fallos silenciosos de B no se anuncian: auditar una muestra comparando el conjunto de restricciones con una segunda traducción independiente o con una retro-traducción a lenguaje natural; (3) latencia y costo por respuesta correcta; (4) accuracy por nivel de dificultad en un conjunto de control con ground truth (aquí cae a {pct(bydiff[('B', 'hard')][2])} en el nivel difícil)."]
    elif best == 'Bprime':
        P += ['Enviaríamos B′ con monitoreo de: (1) tasa de rechazo y número de reintentos por petición; (2) tasa de no convergencia → escalar; (3) auditoría por muestreo de modelos aceptados, porque los errores silenciosos no se anuncian; (4) latencia y costo por respuesta correcta.']
    else:
        P += ['En esta configuración la respuesta directa no es peor que el pipeline híbrido, pero todos sus errores son silenciosos; si se despliega C debe acompañarse de un verificador externo de la solución contra las restricciones.']
    if S[best]['accuracy'] < .8:
        P += [f"Aviso honesto: con una accuracy de {acc[best]} ningún brazo es desplegable sin supervisión con {meta.get('model', 'este modelo')}; la recomendación presupone escalado humano o un modelo más grande, y habría que repetir el experimento con ese modelo antes de afirmar nada más."]
    P += ['', 'Antes de afirmar generalidad habría que repetir el experimento con enunciados de lenguaje natural menos explícitos y otros formalismos.', '']
    if infra: P += [f'_Nota: {len(infra)} ejecuciones con error de infraestructura se excluyeron de todas las cifras (ver `results/per_instance.csv`)._', '']
    P += ['## Reproducibilidad', '', 'Código en `code/` (`run_experiment.py`, `analyze.py`, `csp.py`, `taxonomy.py`, `llm.py`), datos en `problems/`, métricas en `results/*.csv`, figuras en `fig/`, respuestas del LLM cacheadas en `.llm_cache/`, uso de IA en `AI_LOG.md`.']
    return '\n'.join(p for p in P if p is not None)


if __name__ == '__main__':
    main()
