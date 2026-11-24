"""Regenerate technical reports solely from saved experimental artifacts."""
from collections import Counter
import json
from pathlib import Path
import pandas as pd
from .dataset import ROOT
from .metrics import analyze
from .taxonomy import CATEGORIES


def fmt(value):
    if value is None or pd.isna(value): return 'N/A'
    return f'{value:.6g}' if isinstance(value,(int,float)) else str(value)


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,r))+' |' for r in rows])


def report(root: Path = ROOT):
    data = analyze(root)
    df, summary = data['runs'], data['summary'].set_index('arm')
    arms = ['A','B','B-prime','C']
    score = [('Accuracy','accuracy'),('Correct answers','correct_answers'),('Incorrect answers','incorrect_answers'),
             ('No answers','no_answers'),('Mean wall-clock (s)','wall_clock_seconds_mean'),
             ('Mean solver time (s)','solver_time_seconds_mean'),('Mean LLM time (s)','llm_time_seconds_mean'),
             ('Total tokens','total_tokens'),('Total cost (USD)','total_cost'),('Cost per correct (USD)','cost_per_correct_answer')]
    scorecard = table(['Metric','A','B','B′','C'],[[label]+[fmt(summary.loc[a,key]) if a in summary.index else 'Pending' for a in arms] for label,key in score])
    missing = [a for a in arms if a not in summary.index]
    execution = '; '.join(f"{a}: {int(r['attempts'])} runs, {int(r['instances'])} instances, {int(r['repeats'])} repeats" for a,r in summary.iterrows())
    model_info = df[df.arm.ne('A')][['provider','model','model_size','temperature']].drop_duplicates().to_dict('records')
    model_text = json.dumps(model_info) if model_info else 'No LLM was configured or used in the main experiment.'
    metadata = json.loads((root/'results/experiment_metadata.json').read_text())
    active_llm = df[df.arm.ne('A')]
    actual_config = metadata['campaigns'][active_llm.iloc[-1].campaign_id]['config'] if len(active_llm) else {}
    protocol_text = json.dumps({key:actual_config.get(key) for key in ('timeout','max_tokens','solver_timeout','seed','temperature')}) if actual_config else 'No measured LLM configuration yet.'
    pilot = root/'results/pilot_timeout120/runs.csv'
    pilot_text = 'A separate real preflight call timed out after 120 seconds and is preserved in results/pilot_timeout120; the subsequent protocol uses a 300-second LLM deadline. This failed preflight is not pooled into main-protocol accuracy.' if pilot.exists() else ''
    detection_rows = []
    for a in ['B','C']:
        if a in summary.index:
            failures = int(summary.loc[a,'incorrect_answers']+summary.loc[a,'no_answers'])
            detected = int(df.loc[df.arm.eq(a)&df.correctness.ne('correct'),'detectable_error'].sum())
            detection_rows.append([a,failures,detected,fmt(summary.loc[a,'error_detection_rate'])])
        else: detection_rows.append([a,'Pending','Pending','Pending'])
    detection = table(['Arm','Failed attempts','Observable failures','Detection rate'],detection_rows)
    errors = [e for e in data['errors'] if e['arm']=='B']
    counts = Counter(e['taxonomy_category'] for e in errors)
    categories = list(dict.fromkeys(CATEGORIES+list(counts)))
    catrows = [[c,counts[c],f'{100*counts[c]/len(errors):.1f}%' if errors else 'N/A',
                'Yes' if c in ('Malformed syntax','Solver timeout','api_error','llm_timeout','solver_error') else
                'Not applicable' if c=='Quantifier scope / arity errors' else 'No: reference comparison required'] for c in categories]
    taxonomy = '# Error taxonomy\n\n'+('Arm B has not been executed; zero observations must not be interpreted as zero error rate.\n\n' if 'B' not in summary.index else '')
    taxonomy += table(['Category','Count','Share of B flagged cases','Production detectability'],catrows)
    taxonomy += '''\n\nEach case is one instance/repetition. The table includes all status failures and semantic model mismatches even when SAT/UNSAT is correct. `results/errors.csv` contains every flagged attempt in B and B′ with raw output and exhaustive evidence. `results/attempts.csv` contains all model attempts. Infrastructure failures are separate from reasoning failures.

Over-constrained means the generated solution set is a strict subset of the reference set; under-constrained means a strict superset. Incomparable sets identify a different problem. The analysis enumerates all assignments and saves lost/added counterexamples. Missing/extra clauses are supporting evidence only, because redundant clauses need not change semantics. Linguistic causes (reversed implication, dropped premise, incorrect negation) require manual review of the original prompt and are not inferred from a status mismatch. No quantifiers or predicate arities exist in this propositional output language; that category is not applicable. Invalid variable IDs are schema errors.

A legitimate UNSAT answer does not establish over-constraint or an error. Contrary to a literal reading of the assignment's generic table, UNSAT is observable but its incorrectness is not. Neither solution multiplicity nor a generated SAT witness establishes faithfulness to the Spanish prompt.

## B versus C detectability

'''+detection+'''

Detection rate uses incorrect plus no-answer attempts as its denominator; N/A means no failures or no observations. C detects malformed or absent responses but does not claim to verify free-text reasoning contradictions. Well-formed incorrect SAT/UNSAT answers are silent. B additionally checks variable references, solver errors, deadlines and generated-model witnesses. Semantic comparisons are privileged post-hoc analysis, never production detectors.

## Refinement

Only parse/schema/solver errors and solver timeouts trigger up to three repairs. API failures and LLM timeouts stop as infrastructure failures. A valid SAT or UNSAT result stops immediately. Therefore an equivalent UNSAT model is not pressured toward SAT, while semantic errors may survive silently. Observable convergence and ground-truth correctness are stored separately.

'''
    taxonomy += f"Paired improvement (percentage points): {fmt(data['facts']['refinement_delta_percentage_points'])}.\n\n"
    if data['refinements']:
        rc = Counter(r['outcome'] for r in data['refinements'])
        taxonomy += table(['Outcome','Count'],list(rc.items()))+'\n\n'
    candidates = errors + [a for a in data['attempts'] if a not in errors]
    selected, seen = [], set()
    for e in candidates:
        if not e['raw_output'].strip(): continue
        key = (e['problem_id'],e['repeat'],e['arm'],e['iteration'])
        if key not in seen:
            selected.append(e); seen.add(key)
        if len(selected)>=5: break
    taxonomy += f'## Verbatim examples\n\nThere are {len(errors)} flagged B cases. {len(selected)} real output examples are available below. No outputs are synthesized to meet the requested five-example target.\n\n'
    for i,e in enumerate(selected,1):
        taxonomy += f"### Example {i}: {'flagged B case' if e in errors else 'additional representative observation'}\n\n"
        for label,key in [('Problem ID','problem_id'),('Difficulty','difficulty'),('Arm','arm'),('Iteration','iteration')]:
            taxonomy += f'{label}: {e[key]}  \n'
        # Indentation retains literal model text without allowing output to terminate Markdown fences.
        taxonomy += '\nOriginal LLM output:\n\n'+'\n'.join('    '+line for line in e['raw_output'].splitlines())+'\n\n'
        taxonomy += f"Solver result: {e['solver_status']}  \nGround truth: {e['expected_status']}  \nError category: {e['taxonomy_category'] or 'none'}  \nDetectable without ground truth: {e['detectable_error']}  \nExplanation: {e.get('review_note','Status evaluated separately; no reference-based production detector.')}  \nRefinement result: {e['refinement_result']}\n\n"
    (root/'taxonomy.md').write_text(taxonomy)
    structure = pd.read_csv(root/'results/dataset_structure.csv')
    difficulty = table(['Difficulty','Variables (range)','Clauses (range)','Mean literals','Mean clause length','Unit fraction'],[
        [level,f'{g.variables.min()}–{g.variables.max()}',f'{g.clauses.min()}–{g.clauses.max()}',fmt(g.literals.mean()),fmt(g.mean_clause_length.mean()),fmt(g.unit_clause_ratio.mean())]
        for level in ['easy','medium','hard'] for g in [structure[structure.difficulty.eq(level)]]])
    convergence = Counter(r['outcome'] for r in data['refinements'])
    refinement_text = ('No paired B/B′ observations exist; improvement, regression and convergence rates are pending.' if not data['refinements'] else
        f"Paired accuracy difference B′ − B: {fmt(data['facts']['refinement_delta_percentage_points'])} percentage points across {data['facts']['paired_units']} pairs. Outcomes: {dict(convergence)}. Improvements: {sum(r['improved'] for r in data['refinements'])}; regressions: {sum(r['regressed'] for r in data['refinements'])}.")
    if data['refinements']:
        repairs = data['refinements']
        n = len(repairs)
        persistent = Counter(r['initial_category'] for r in repairs if not r['final_correct'])
        repaired = Counter(r['initial_category'] for r in repairs if r['improved'])
        refinement_text += f' Observable non-convergence: {100*sum(not r["observable_convergence"] for r in repairs)/n:.1f}%; exhausted three-repair budgets: {100*sum(r["budget_exhausted"] for r in repairs)/n:.1f}%. Status-incorrect cases that stopped without a detectable error: {sum(r["outcome"]=="silent_incorrect" for r in repairs)}. Repaired initial categories: {dict(repaired)}; persistent status-failure categories: {dict(persistent)}.'
    semantic_text = '; '.join(f'{a}: {int(summary.loc[a,"silent_semantic_models"])} silent semantic mismatches' for a in ['B','B-prime'] if a in summary.index) or 'Semantic model mismatch counts are pending.'
    accuracy = pd.read_csv(root/'results/by_difficulty.csv')
    accuracy_text = '; '.join(f"{r.arm}/{r.difficulty}: {100*r.accuracy:.1f}% ({r.attempts} runs)" for r in accuracy.itertuples())
    comparison_text = 'No empirical ranking among the LLM arms is available.'
    if all(a in summary.index for a in ['B','B-prime','C']):
        best = max(['B','B-prime','C'],key=lambda a:summary.loc[a,'accuracy'])
        comparison_text = f'Among observed LLM runs, {best} has the highest accuracy ({100*summary.loc[best,"accuracy"]:.1f}%; ties resolved by listing order). This is descriptive, not a significance result. Compare coverage and silent failures before deployment.'
    conclusion = 'The supplied references and reused DPLL are independently validated. ' + ('The LLM campaign is incomplete; observed metrics describe only the reported coverage and do not establish a full-dataset comparison.' if missing or any(summary.loc[a,'attempts']<60 for a in summary.index) else f'Across 20 instances and three repeats, observed accuracy was '+', '.join(f'{a}: {100*summary.loc[a,"accuracy"]:.1f}%' for a in arms)+f'. B′ − B was {fmt(data["facts"]["refinement_delta_percentage_points"])} percentage points. Status accuracy must be interpreted alongside the recorded silent semantic mismatches.')
    output = f'''# Homework 2 — The Formalizer (SAT)

Team members: [complete with existing studio-group names]

## 1. Duel Scorecard

{scorecard}

Accuracy is correct / all attempts; no-answer counts against accuracy and is also reported separately. N/A denotes undefined or unpriced quantities. Pending arms: {', '.join(missing) or 'none'}. These are not zero-accuracy arms.

## 2. Experimental Methodology

The 20 supplied Spanish problems and their CNF references were copied byte-for-byte. There are six easy, eight medium and six hard instances, balanced overall between SAT and UNSAT. Every documented SAT witness was checked independently. Exhaustive truth tables verified every status and agreed with the unmodified Week 7 DPLL engine. No reference was corrected. Validation concerns CNF and witnesses; it does not independently prove that every Spanish premise was encoded faithfully.

{difficulty}

DPLL performs unit propagation, pure literal elimination, conflict detection and backtracking. A POSIX deadline adapter reports SAT, UNSAT, TIMEOUT or ERROR and checks returned witnesses. The vendored source is unchanged; its hash and dataset hashes appear in experiment metadata. The default deadline is 10 seconds. Tests also compare randomized formulas against an exhaustive oracle.

Actual execution: {execution}. Repetitions are repeated measurements of the same 20 problems, not additional independent problems. The solver is deterministic; repeated solver runs quantify timing variation only. Model configuration: {model_text} Measured LLM settings: {protocol_text}

{pilot_text}

A uses the reference CNF. B receives only the Spanish prompt and variable map and generates strict JSON CNF. B′ reuses exactly B's first response and performs at most three repairs. C receives the Spanish prompt and a JSON answer format. Default temperature is zero, output budget 2048 tokens, request timeout 120 seconds and prompt version sat-v1. Optional seeds vary by repetition; provider determinism is not guaranteed. Exact configuration, environment and timestamps are recorded per campaign.

Raw responses, prompts, usage and provenance are persisted. Tokens come from provider usage when available, otherwise a labeled characters/4 estimate. Cache keys include model, endpoint, prompt, parameters, seed and repetition. Original model latency is kept separate from file access and observed invocation wall time. Pipeline time includes the shared initial B attempt for B′; measured B′ invocation wall time may exclude work already completed by B. Arm costs are standalone-policy estimates, while the physical call ledger avoids double-counting shared generations.

## 3. Accuracy vs Difficulty

![Accuracy](fig/accuracy_vs_difficulty.png)

{accuracy_text}. Missing series are explicitly marked pending. More variables and clauses support structural difficulty labels but do not prove computational hardness. This small dataset cannot establish causal effects of difficulty.

## 4. Error Taxonomy

See [taxonomy.md](taxonomy.md) for all categories, available verbatim examples and the production/analysis distinction. Every flagged attempt is saved in results/errors.csv. Exhaustive solution-set inclusion distinguishes over-constraint, under-constraint and incomparable models. Identical SAT/UNSAT status is weaker than semantic equivalence. Quantifier scope/arity is not applicable here.

{detection}

{len(errors)} flagged B cases are currently recorded. {semantic_text}. If B has not run, this is an absence of evidence. UNSAT is a legitimate observation and never itself proves mistranslation. C's free-text explanations are retained but no unverifiable contradiction detector is claimed.

## 5. Refinement Analysis

{refinement_text}

Only observable parser/schema errors, solver errors and solver deadlines trigger correction. Infrastructure failures stop and remain separately labeled. Valid SAT and UNSAT both terminate the loop. Consequently, silent semantic failures are not repaired by this policy. The refinement CSV distinguishes observable convergence, real correctness, iteration count and exhausted budgets. Repair-specific effects require real B/B′ observations.

![Refinement](fig/refinement_success.png)

## 6. Cost Accounting

Token cost is input tokens × input price / 1,000,000 plus output tokens × output price / 1,000,000. Local compute may instead use measured model seconds × configured hourly price / 3600. Prices, source and date are external configuration; no current tariff is assumed. Missing tariffs remain N/A. Cost per correct answer includes all attempts and repairs and is undefined when there are no correct answers. A has zero LLM token cost; hardware/energy costs are not claimed to be zero and are outside this accounting.

Physical provider requests: {data['facts']['physical_provider_requests']}. Physical estimated monetary cost: {fmt(data['facts']['physical_cost_usd'])} USD. B and B′ standalone costs must not be added to estimate actual experiment spending because their initial generations are shared.

![Latency](fig/latency_by_arm.png)

## 7. Where We May Have Been Unfair

The dataset is small, synthetic, balanced and Spanish-only. Related SAT/UNSAT pairs may reduce effective diversity. Hand-written references have a strong information advantage. Labels reflect structure rather than proven hardness. Low temperature reduces diversity but cannot guarantee reproducibility. Translation and direct-answer prompts impose different cognitive and output burdens, despite equal generation budgets. Repeated outputs are clustered by instance; no significance claim treats 60 runs as 60 problems. SAT/UNSAT accuracy can hide semantically wrong translations. Our conservative repair policy leaves valid but wrong models untouched and does not test alternative UNSAT-review policies. Deadline behavior and timing depend on hardware and provider load. Arms run in a fixed sequential order, so warm-up and provider prompt-cache effects may influence latency; no random-order latency claim is made. API errors are infrastructure failures, not evidence of poor SAT reasoning. Real model results and five examples remain unavailable until a provider is configured if those arms are pending.

## 8. Deployment Recommendation

The validated hand-model pipeline is the only empirically supported choice when trusted CNF specifications are already available. This does not establish the best architecture for unseen natural-language inputs. {comparison_text} Selection among B, B′ and C requires completed accuracy, silent-error, latency and cost measurements. A deployed translator should retain raw outputs, validate schemas and witnesses, monitor timeouts and provider failures, and use independent semantic review or clarification for high-impact specifications. Refinement can address observable failures, but valid-looking translations still require monitoring; superiority of B′ is not assumed.

## 9. Conclusion

{conclusion}
'''
    if len(output.split())>2500: raise ValueError('report exceeds 2500 words')
    destination = root/'REPORT.md'
    if destination.exists():
        old = destination.read_text()
        # Keep an existing member line instead of overwriting names.
        names = next((line for line in old.splitlines() if line.startswith('Team members:')),None)
        if names: output = output.replace('Team members: [complete with existing studio-group names]',names)
    destination.write_text(output)
    return data
