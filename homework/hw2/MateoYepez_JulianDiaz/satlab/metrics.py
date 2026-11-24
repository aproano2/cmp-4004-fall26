"""Descriptive statistics without treating repeats as distinct problems."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .dataset import load_dataset, ROOT, structural
from .taxonomy import evaluate


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for arm, group in df.groupby('arm',sort=False):
        good = group.correctness.eq('correct')
        failures = ~good
        total = group.estimated_cost_usd.sum(min_count=len(group))
        rows.append({'arm':arm,'attempts':len(group),'instances':group.problem_id.nunique(),
            'repeats':group['repeat'].nunique(),'correct_answers':int(good.sum()),
            'incorrect_answers':int(group.correctness.eq('incorrect').sum()),
            'no_answers':int(group.correctness.eq('no-answer').sum()),'accuracy':good.mean(),
            'no_answer_rate':group.correctness.eq('no-answer').mean(),
            'semantic_model_error_rate':group.error_category.eq('semantic_error').mean() if arm in ('B','B-prime') else np.nan,
            'silent_semantic_models':int((group.error_category.eq('semantic_error') & ~group.detectable_error).sum()) if arm in ('B','B-prime') else 0,
            'error_detection_rate':group.loc[failures,'detectable_error'].mean() if failures.any() else np.nan,
            'total_tokens':group.total_tokens.sum(),'total_cost':total,'cost_per_attempt':total/len(group),
            'cost_per_correct_answer':total/good.sum() if good.any() else np.nan,
            **{f'{col}_{stat}':float(getattr(group[col],stat)()) for col in
               ('wall_clock_seconds','pipeline_time_seconds','llm_time_seconds','solver_time_seconds')
               for stat in ('mean','median','std')},
            'latency_p90':group.pipeline_time_seconds.quantile(.9) if len(group)>=10 else np.nan})
    return pd.DataFrame(rows)


def analyze(root: Path = ROOT) -> dict:
    results = root/'results'
    df = pd.read_csv(results/'runs.csv')
    # Do not silently combine protocols or independent reruns of the same instance/repetition.
    llm = df[df.arm.ne('A')]
    if llm.campaign_id.nunique()>1:
        raise ValueError('Mixed LLM campaigns: use separate output directories for different configurations')
    if df.duplicated(['arm','problem_id','repeat']).any():
        raise ValueError('Duplicate experimental units; separate configurations before analysis')
    df['detectable_error'] = df.detectable_error.astype(str).str.lower().eq('true')
    summary = summarize(df)
    summary.to_csv(results/'summary.csv',index=False)
    summary[['arm','total_cost','cost_per_attempt','cost_per_correct_answer']].to_csv(results/'costs.csv',index=False)
    for keys,name in [(['arm','problem_id','difficulty'],'by_instance'),(['arm','repeat'],'by_repeat'),(['arm','difficulty'],'by_difficulty')]:
        grouped = df.assign(correct=df.correctness.eq('correct')).groupby(keys).agg(
            accuracy=('correct','mean'),attempts=('correct','size'),latency=('pipeline_time_seconds','mean'))
        grouped.to_csv(results/f'{name}.csv')
    problems = {p['id']:p for p in load_dataset(root/'problems')}
    pd.DataFrame([structural(p) for p in problems.values()]).to_csv(results/'dataset_structure.csv',index=False)
    errors, refinements, all_attempts = [], [], []
    review_path = results/'posthoc_reviews.json'
    reviews = json.loads(review_path.read_text()) if review_path.exists() else {}
    for row in df.to_dict('records'):
        artifact = json.loads((results/'artifacts'/f"{row['run_id']}.json").read_text())
        attempts = artifact['attempts']
        for attempt in attempts:
            evaluated = evaluate(problems[row['problem_id']],attempt)
            entry = {'run_id':row['run_id'],'problem_id':row['problem_id'],'difficulty':row['difficulty'],
                'arm':row['arm'],'repeat':row['repeat'],'iteration':attempt['iteration'],
                'raw_output':attempt['call']['raw'],'solver_status':attempt['solver_status'],
                'expected_status':row['expected_status'],'predicted_status':attempt['predicted_status'],
                'detectable_error':attempt['detectable_error'],'refinement_result':row['convergence'],**evaluated}
            if row['arm']=='B':
                paired_final = df[df.arm.eq('B-prime') & df.problem_id.eq(row['problem_id']) & df['repeat'].eq(row['repeat'])]
                entry['refinement_result'] = paired_final.iloc[0]['convergence'] if len(paired_final) else 'Pending B-prime'
            review = reviews.get(attempt['call']['call_id'])
            if review: entry['review_note'] = review['note']
            all_attempts.append(entry)
            if evaluated['correctness']!='correct' or evaluated['taxonomy_category']:
                errors.append(entry)
        if row['arm']=='B-prime':
            initial = evaluate(problems[row['problem_id']],attempts[0])
            correct_iterations = [a['iteration'] for a in attempts if evaluate(problems[row['problem_id']],a)['correctness']=='correct']
            refinements.append({'problem_id':row['problem_id'],'repeat':row['repeat'],
                'initial_correct':initial['correctness']=='correct','final_correct':row['correctness']=='correct',
                'initial_category':initial['taxonomy_category'], 'final_category':row.get('taxonomy_category',''),
                'improved':initial['correctness']!='correct' and row['correctness']=='correct',
                'regressed':initial['correctness']=='correct' and row['correctness']!='correct',
                'observable_convergence':row['observable_convergence'],'outcome':row['convergence'],
                'iterations':row['refinement_iterations'],
                'first_correct_iteration':min(correct_iterations) if correct_iterations else None,
                'budget_exhausted':row['convergence']=='budget_exhausted'})
    columns = ['run_id','problem_id','difficulty','arm','repeat','iteration','raw_output','solver_status',
               'expected_status','predicted_status','detectable_error','refinement_result','correctness','taxonomy_category','error_category']
    pd.DataFrame(errors,columns=columns+['semantic_category','reference_solutions','generated_solutions','lost_solutions',
        'added_solutions','lost_counterexample','added_counterexample','missing_clauses','extra_clauses','review_note']).to_csv(results/'errors.csv',index=False)
    pd.DataFrame(all_attempts,columns=columns).to_csv(results/'attempts.csv',index=False)
    pd.DataFrame(refinements,columns=['problem_id','repeat','initial_correct','final_correct','improved','regressed',
        'observable_convergence','outcome','iterations','first_correct_iteration','budget_exhausted','initial_category','final_category']).to_csv(results/'refinement.csv',index=False)
    paired = df[df.arm.eq('B')][['problem_id','repeat','correctness']].merge(
        df[df.arm.eq('B-prime')][['problem_id','repeat','correctness']],on=['problem_id','repeat'],suffixes=('_B','_Bp'))
    delta = float((paired.correctness_Bp.eq('correct').astype(int)-paired.correctness_B.eq('correct').astype(int)).mean()*100) if len(paired) else None
    # Physical calls are deduplicated: B and B-prime share generation zero.
    calls_path = results/'calls.jsonl'
    calls = [json.loads(s) for s in calls_path.read_text().splitlines()] if calls_path.exists() else []
    paid = [c for c in calls if not c['cache_hit']]
    ledger_total = sum(c['charged_cost_usd'] for c in paid) if all(c['charged_cost_usd'] is not None for c in paid) else None
    facts = {'paired_units':len(paired),'refinement_delta_percentage_points':delta,
             'physical_provider_requests':len(paid),'physical_cost_usd':ledger_total,
             'physical_llm_seconds':sum(c['llm_time_seconds'] for c in paid),
             'physical_input_tokens':sum(c['input_tokens'] for c in paid),
             'physical_output_tokens':sum(c['output_tokens'] for c in paid),
             'estimated_token_calls':sum(c['token_source']!='provider' for c in paid),
             'note':'Arm costs are standalone policy costs; never sum B and B-prime as actual spend.'}
    (results/'analysis.json').write_text(json.dumps(facts,indent=2))
    return {'runs':df,'summary':summary,'errors':errors,'refinements':refinements,'attempts':all_attempts,'facts':facts}
