"""Persistent paired runs. Evaluation happens only after arm execution."""
import json
import platform
import os
import importlib.metadata
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from . import arm_a, arm_b, arm_b_refinement, arm_c
from .dataset import public_problem, hashes, validate_dataset, ROOT
from .llm_client import LLMClient, atomic_json, digest
from .prompts import VERSION
from .taxonomy import evaluate


def _sum_cost(calls, key):
    values = [c[key] for c in calls]
    return sum(values) if all(v is not None for v in values) else None


def _row(problem, arm, repeat, run_id, cfg, attempts, wall):
    final = attempts[-1]
    evaluation = evaluate(problem,final)
    calls = [a['call'] for a in attempts]
    refinements = len(attempts)-1
    if arm != 'B-prime': convergence = ''
    elif final['detectable_error']: convergence = 'budget_exhausted' if refinements == 3 else 'infrastructure_stop'
    elif evaluation['correctness'] != 'correct': convergence = 'silent_incorrect'
    else: convergence = 'initial_success' if refinements == 0 else f'corrected_{refinements}'
    return {'run_id':run_id,'problem_id':problem['id'],'difficulty':problem['difficulty'],'arm':arm,'repeat':repeat,
            'provider':cfg.provider,'model':cfg.model,'model_size':cfg.model_size,'temperature':cfg.temperature,
            'expected_status':problem['ground_truth']['status'],'predicted_status':final['predicted_status'],
            **evaluation,'detectable_error':final['detectable_error'],'error_message':final['error_message'],
            'llm_time_seconds':sum(c['llm_time_seconds'] for c in calls),
            'solver_time_seconds':sum(a['solver_time_seconds'] for a in attempts),
            'parse_validation_seconds':sum(a['parse_validation_seconds'] for a in attempts),
            'wall_clock_seconds':wall,
            'pipeline_time_seconds':sum(c['llm_time_seconds'] for c in calls)+sum(a['processing_seconds'] for a in attempts),
            'cache_access_seconds':sum(c['access_seconds'] for c in calls if c['cache_hit']),
            'input_tokens':sum(c['input_tokens'] for c in calls),'output_tokens':sum(c['output_tokens'] for c in calls),
            'total_tokens':sum(c['input_tokens']+c['output_tokens'] for c in calls),
            'token_source':','.join(sorted({c['token_source'] for c in calls})),
            'estimated_cost_usd':_sum_cost(calls,'estimated_cost_usd'),
            'charged_cost_usd':_sum_cost(calls,'charged_cost_usd'),
            'solver_status':final['solver_status'],'refinement_iterations':refinements,'final_iteration':refinements,
            'refinement_time_seconds':sum(a['call']['llm_time_seconds']+a['processing_seconds'] for a in attempts[1:]),
            'cache_hit':any(c['cache_hit'] for c in calls),'initial_call_id':calls[0]['call_id'],
            'observable_convergence':not final['detectable_error'],'convergence':convergence,
            'timestamp':datetime.now(timezone.utc).isoformat()}


def run_experiment(problems, arms, repeats, cfg, root=ROOT, resume=True, client=None):
    if repeats < 1: raise ValueError('repeats must be positive')
    if any(a != 'A' for a in arms): cfg.require_llm()
    results = root/'results'
    results.mkdir(parents=True,exist_ok=True)
    # Full dataset validation belongs to CLI before selection; all selected references checked here by A.
    for p in problems:
        hand = arm_a.run(p,cfg.solver_timeout)
        if hand['status'] != p['ground_truth']['status']:
            raise ValueError(f"Arm A gate failed: {p['id']} {hand['status']}")
    client = client or LLMClient(cfg,root)
    public_config = cfg.public()
    public_config.pop('cache', None)
    protocol = {'config':public_config,'prompt_version':VERSION,'policy':'observable-errors-only-v1',
                'solver_sha256':digest((ROOT/'satlab/vendor/week07_dpll.py').read_text()),
                'dataset':hashes(root/'problems')}
    campaign = digest(protocol)
    metadata_path = results/'experiment_metadata.json'
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {'campaigns':{}}
    metadata['campaigns'][campaign] = {**protocol,'python':sys.version,'platform':platform.platform(),
        'processor':platform.processor(),'cpu_count':os.cpu_count(),
        'dependencies':{name:importlib.metadata.version(name) for name in ('numpy','pandas','matplotlib','requests','python-dotenv')},'timestamp':datetime.now(timezone.utc).isoformat(),
        'selected_problems':[p['id'] for p in problems],'requested_arms':arms,'requested_repeats':repeats,
        'determinism':'Seed is best effort; provider determinism is not guaranteed.'}
    snapshot = results/'provider_snapshot.json'
    if snapshot.exists(): metadata['campaigns'][campaign]['provider_snapshot'] = json.loads(snapshot.read_text())
    atomic_json(metadata_path,metadata)
    path = results/'runs.csv'
    existing = pd.read_csv(path).to_dict('records') if path.exists() else []
    records = {r['run_id']:r for r in existing}
    for artifact in (results/'artifacts').glob('*.json'):
        saved = json.loads(artifact.read_text())['row']
        records[saved['run_id']] = saved
    for repeat in range(repeats):
        for p in problems:
            public = public_problem(p)
            pair_id = digest({'campaign':campaign,'problem':p['id'],'repeat':repeat})
            first_path = results/'checkpoints'/f'{pair_id}-B.json'
            first = None
            for arm in ('A','B','B-prime','C'):
                if arm not in arms: continue
                identity = {'problem':digest(p),'arm':arm,'repeat':repeat,
                            'protocol':protocol if arm != 'A' else {'solver':protocol['solver_sha256'],'timeout':cfg.solver_timeout}}
                run_id = digest(identity)
                if resume and run_id in records: continue
                start = time.perf_counter()
                event_offset = len(client.events)
                paired_reused = False
                if arm == 'A':
                    result = arm_a.run(p,cfg.solver_timeout)
                    fake = {'predicted_status':result['status'],'error_category':('solver_timeout' if result['status']=='TIMEOUT' else 'solver_error' if result['status']=='ERROR' else ''),'clauses':None}
                    row = {k:0 for k in ('llm_time_seconds','input_tokens','output_tokens','total_tokens',
                        'estimated_cost_usd','charged_cost_usd','parse_validation_seconds','cache_access_seconds','refinement_time_seconds')}
                    row.update(run_id=run_id,problem_id=p['id'],difficulty=p['difficulty'],arm=arm,repeat=repeat,
                        provider='none',model='Week7 DPLL',model_size='N/A',temperature=None,
                        expected_status=p['ground_truth']['status'],predicted_status=result['status'],
                        **evaluate(p,fake),detectable_error=bool(fake['error_category']),error_message=result['error'],solver_time_seconds=result['seconds'],
                        wall_clock_seconds=time.perf_counter()-start,pipeline_time_seconds=result['seconds'],
                        solver_status=result['status'],refinement_iterations=0,final_iteration=0,cache_hit=False,
                        token_source='not_applicable',initial_call_id='',observable_convergence=True,convergence='',
                        timestamp=datetime.now(timezone.utc).isoformat())
                    attempts = []
                else:
                    if arm in ('B','B-prime'):
                        if first is None:
                            if first_path.exists() and (resume or arm == 'B-prime'):
                                first = json.loads(first_path.read_text())
                                paired_reused = True
                            else:
                                first = arm_b.run(public,client,repeat,cfg.solver_timeout)
                                atomic_json(first_path,first)
                        if arm == 'B-prime': paired_reused = True
                        attempts = [first]
                        if arm == 'B-prime':
                            repair_path = results/'checkpoints'/f'{pair_id}-repairs.json'
                            prior = json.loads(repair_path.read_text()) if resume and repair_path.exists() else None
                            attempts = arm_b_refinement.run(public,client,repeat,cfg.solver_timeout,first,
                                checkpoint=lambda value:atomic_json(repair_path,value),prior=prior)
                    else:
                        attempts = [arm_c.run(public,client,repeat,cfg.solver_timeout)]
                    row = _row(p,arm,repeat,run_id,cfg,attempts,time.perf_counter()-start)
                row['campaign_id'] = campaign
                row['paired_checkpoint_reused'] = paired_reused
                row['charged_cost_usd'] = _sum_cost(client.events[event_offset:], 'charged_cost_usd')
                # Each record is an atomic durable unit; CSV can be reconstructed from artifacts.
                artifact_path = results/'artifacts'/f'{run_id}.json'
                if artifact_path.exists():
                    previous_artifact = json.loads(artifact_path.read_text())
                    atomic_json(results/'history'/f'{run_id}-{digest(previous_artifact)}.json', previous_artifact)
                atomic_json(artifact_path,{'row':row,'attempts':attempts})
                records[run_id] = row
                pd.DataFrame(records.values()).to_csv(path.with_suffix('.tmp'),index=False)
                path.with_suffix('.tmp').replace(path)
                print(f'{arm} {p["id"]} repeat={repeat}: {row["predicted_status"]} ({row["correctness"]})', flush=True)
                if arm == 'A' and row['correctness'] != 'correct':
                    raise ValueError(f'Arm A failed during measured execution: {p["id"]}')
                if row['error_category'] in ('api_error','llm_timeout'):
                    raise ValueError('Infrastructure failure saved; stopping campaign to avoid repeated failing requests. Resolve provider and explicitly rerun the failed unit.')
    frame = pd.DataFrame(records.values())
    frame.to_csv(path.with_suffix('.tmp'),index=False)
    path.with_suffix('.tmp').replace(path)
    return frame
