"""Entrada unica para HW2. Ejecutar desde terminal: python EJECUTAR.py verificar"""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'code'))


def verificar():
    from persona3 import bank, evaluate
    from arm_a_p1 import MODELS as M1
    from arm_a_p2 import MODELS as M2
    from logic_lm import build_csp
    from csp import backtrack_search
    problems = bank()
    if len(problems) != 20:
        raise RuntimeError(f'Se esperaban 20 problemas, hay {len(problems)}')
    ok = 0
    for pid, puzzle in sorted(problems.items()):
        if pid in M1:
            spec = M1[pid]()
        elif pid in M2:
            spec = M2[pid]()
        else:
            spec = puzzle['spec']
        result = evaluate(json.dumps(spec, ensure_ascii=False))
        good = result['signal'] == 'none' and result['answer'] == puzzle['gold']
        print(f'{pid}: {"OK" if good else "ERROR"} ({result["signal"]})')
        if not good:
            raise RuntimeError(f'Fallo del modelo A {pid}: {result}')
        ok += 1
    print(f'VERIFICACION CORRECTA: {ok}/20 modelos A coinciden con gold.')


def bc(model):
    from persona3 import bank
    bank()
    target = ROOT / 'results' / 'bc_p3.csv'
    cmd = [sys.executable, str(ROOT / 'code' / 'run_bc.py'), '--bank', str(ROOT / 'problems' / 'problems_p3.json'), '--output', str(target), '--model', model]
    print('Ejecutando B y C para q15-q20 (requiere Ollama).', flush=True)
    subprocess.run(cmd, cwd=str(ROOT), check=True)
    print('Guardado en:', target)


def refinar(model, ids):
    from persona3 import run_refinement
    results, traces = run_refinement(ids=ids, model=model)
    print('B-prima:', len(results), 'problemas; salidas en results/bprime_results.csv y results/bprime_traces.csv')


def analizar():
    from persona3 import combined_results, scorecard, make_figures, taxonomy, cost_per_correct
    df = combined_results()
    if df.empty:
        raise RuntimeError('No hay resultados para analizar.')
    df.to_csv(ROOT / 'results' / 'all_arms_combined.csv', index=False)
    summary = scorecard(df)
    summary.to_csv(ROOT / 'results' / 'scorecard.csv', index=False)
    print('\nSCORECARD:\n', summary.to_string(index=False))
    print('\nGRAFICAS:')
    for f in make_figures(df):
        print(' -', f.relative_to(ROOT))
    failures = taxonomy(df)
    print('\nErrores B por revisar:', len(failures))
    print('Costo USD: requiere tarifas reales. Tiempos/tokens guardados en CSV.')
    print('\nRevisa el documento taxonomy.md manualmente: los errores semanticos no se deducen solos.')


def ollama_status(model):
    import urllib.request
    try:
        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=3) as response:
            data = json.load(response)
        models = [m.get('name', '') for m in data.get('models', [])]
        print('Ollama disponible. Modelos:', ', '.join(models) if models else '(ninguno)')
        if model not in models:
            print(f'El modelo {model} no esta instalado. Ejecuta: ollama pull {model}')
            return False
        return True
    except Exception as exc:
        print('Ollama no responde:', exc)
        print('Abre Ollama y verifica con: ollama list')
        return False


def main():
    parser = argparse.ArgumentParser(description='HW2: verificar, ollama, bc, refinar, analizar, todo')
    parser.add_argument('accion', choices=['verificar', 'ollama', 'bc', 'refinar', 'analizar', 'todo'])
    parser.add_argument('--model', default='qwen2.5:3b')
    parser.add_argument('--ids', nargs='+', help='Para una prueba corta de B-prima, p.ej. --ids q01')
    args = parser.parse_args()
    if args.accion == 'verificar': verificar()
    elif args.accion == 'ollama': ollama_status(args.model)
    elif args.accion == 'bc':
        if not ollama_status(args.model): sys.exit(1)
        bc(args.model)
    elif args.accion == 'refinar':
        if not ollama_status(args.model): sys.exit(1)
        refinar(args.model, args.ids)
    elif args.accion == 'analizar': analizar()
    elif args.accion == 'todo':
        verificar()
        if not ollama_status(args.model): sys.exit(1)
        bc(args.model)
        refinar(args.model, None)
        analizar()

if __name__ == '__main__':
    main()
