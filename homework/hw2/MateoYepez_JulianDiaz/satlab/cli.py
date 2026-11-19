"""Terminal entry point: python -m satlab.cli --help."""
import argparse
import json
import os
from pathlib import Path
from .config import Config
from .dataset import ROOT, load_dataset, validate_dataset
from .llm_client import atomic_json


def main(argv=None):
    config = Config.from_env()
    parser = argparse.ArgumentParser(description='Homework 2 SAT experiment; no web UI')
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('validate',help='Check original CNF, witnesses, DPLL and exhaustive truth tables')
    run = sub.add_parser('run',help='Run selected arms; resume completed units by default')
    choice = run.add_mutually_exclusive_group(required=True)
    choice.add_argument('--arm',choices=['A','B','B-prime','C'])
    choice.add_argument('--all',action='store_true')
    run.add_argument('--repeats',type=int,default=int(os.getenv('REPEATS','3')))
    run.add_argument('--problems',nargs='+')
    run.add_argument('--levels',nargs='+',choices=['easy','medium','hard'])
    run.add_argument('--provider',choices=['openai-compatible','ollama'])
    run.add_argument('--model')
    run.add_argument('--cache',action=argparse.BooleanOptionalAction,default=True)
    run.add_argument('--resume',action=argparse.BooleanOptionalAction,default=True)
    run.add_argument('--llm-timeout',type=float)
    run.add_argument('--solver-timeout',type=float)
    for cmd in ('analyze','plot','report'): sub.add_parser(cmd,help=f'{cmd} saved results without LLM calls')
    args = parser.parse_args(argv)
    try:
        if args.command in ('validate','run'):
            problems = load_dataset()
            validation = validate_dataset(problems)
            atomic_json(ROOT/'results/dataset_validation.json',validation)
            if not all(row['valid'] for row in validation): raise ValueError('Dataset inconsistencies: see results/dataset_validation.json')
            if args.command=='validate':
                print('20/20 reference statuses and witnesses validated by independent enumeration and Week 7 DPLL')
                return 0
            cfg = config
            for arg,field in [('provider','provider'),('model','model'),('llm_timeout','timeout'),('solver_timeout','solver_timeout'),('cache','cache')]:
                value = getattr(args,arg)
                if value is not None: setattr(cfg,field,value)
            if args.problems:
                unknown = set(args.problems)-{p['id'] for p in problems}
                if unknown: raise ValueError(f'Unknown problems: {sorted(unknown)}')
                problems = [p for p in problems if p['id'] in args.problems]
            if args.levels: problems = [p for p in problems if p['difficulty'] in args.levels]
            if not problems: raise ValueError('Selection contains no problems')
            from .experiment import run_experiment
            frame = run_experiment(problems,['A','B','B-prime','C'] if args.all else [args.arm],args.repeats,cfg,resume=args.resume)
            print(f'{len(frame)} total persisted runs; selection={len(problems)} instances')
        elif args.command=='analyze':
            from .metrics import analyze
            print(analyze()['summary'].to_string(index=False))
        elif args.command=='plot':
            from .plotting import plot
            plot(); print('Four figures generated in fig/')
        else:
            from .reporting import report
            report(); print('REPORT.md and taxonomy.md regenerated from saved evidence')
        return 0
    except (ValueError,FileNotFoundError) as exc:
        parser.exit(2,f'Error: {exc}\n')

if __name__=='__main__':
    raise SystemExit(main())
