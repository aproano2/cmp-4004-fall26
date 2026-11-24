"""Read-only acceptance audit of persisted evidence and public prompt boundaries."""
import json
from pathlib import Path
import pandas as pd
from .dataset import ROOT, hashes, load_dataset, public_problem
from .prompts import initial, feedback


def audit(root: Path = ROOT) -> dict:
    problems = {p['id']:p for p in load_dataset(root/'problems')}
    df = pd.read_csv(root/'results/runs.csv')
    issues = []
    for row in df.to_dict('records'):
        path = root/'results/artifacts'/f"{row['run_id']}.json"
        artifact = json.loads(path.read_text())
        attempts = artifact['attempts']
        if row['arm']=='A':
            if attempts or row['total_tokens'] != 0 or row['llm_time_seconds'] != 0:
                issues.append(f"{row['run_id']}: Arm A has LLM activity")
            continue
        if len(attempts)>4 or (row['arm']!='B-prime' and len(attempts)!=1):
            issues.append(f"{row['run_id']}: invalid iteration budget")
        public = public_problem(problems[row['problem_id']])
        messages = initial(public,'C' if row['arm']=='C' else 'B')
        for index,attempt in enumerate(attempts):
            call = attempt['call']
            if call['messages'] != messages:
                issues.append(f"{row['run_id']}: unexpected prompt at iteration {index}")
            if call['iteration']!=index or call['problem_id']!=row['problem_id'] or call['repeat']!=row['repeat']:
                issues.append(f"{row['run_id']}: inconsistent call identity")
            messages = feedback(messages,call['raw'],attempt['error_message'])
        if row['total_tokens'] != sum(a['call']['input_tokens']+a['call']['output_tokens'] for a in attempts):
            issues.append(f"{row['run_id']}: inconsistent token total")
        if abs(row['llm_time_seconds']-sum(a['call']['llm_time_seconds'] for a in attempts))>1e-8:
            issues.append(f"{row['run_id']}: inconsistent model time")
        if row['arm']=='B-prime':
            paired = df[df.arm.eq('B') & df.problem_id.eq(row['problem_id']) & df['repeat'].eq(row['repeat'])]
            if len(paired):
                first = json.loads((root/'results/artifacts'/f"{paired.iloc[0].run_id}.json").read_text())['attempts'][0]
                if attempts[0]!=first: issues.append(f"{row['run_id']}: initial B response was not reused exactly")
    original = ROOT.parent/'HW2-SAT-dataset/problems'
    if original.exists() and hashes(root/'problems') != hashes(original): issues.append('original dataset differs')
    report = root/'REPORT.md'
    if report.exists() and len(report.read_text().split())>2500: issues.append('report exceeds 2500 words')
    for name in ['accuracy_vs_difficulty','latency_by_arm','error_taxonomy','refinement_success']:
        path = root/'fig'/f'{name}.png'
        if not path.exists() or not path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            issues.append(f'missing/invalid figure: {name}')
    coverage = {arm:{'runs':len(group),'instances':int(group.problem_id.nunique()),'repeats':int(group['repeat'].nunique())}
                for arm,group in df.groupby('arm')}
    return {'valid':not issues,'issues':issues,'coverage':coverage,
            'report_words':len(report.read_text().split()) if report.exists() else None,
            'expected_main_runs':240,'completed_main_runs':len(df),
            'all_four_arms_three_repeats_complete':all(len(df[df.arm.eq(a)])==60 for a in ['A','B','B-prime','C'])}

if __name__=='__main__':
    result = audit()
    (ROOT/'results/acceptance_audit.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['valid'] else 1)
