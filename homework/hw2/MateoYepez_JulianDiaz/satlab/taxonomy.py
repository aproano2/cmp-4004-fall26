"""Privileged post-hoc analysis, never imported by generation or refinement."""
from .validation import solutions

CATEGORIES = ['Malformed syntax','Valid syntax, over-constrained','Valid syntax, under-constrained',
              'Valid model of the wrong problem','Quantifier scope / arity errors','Solver timeout']


def compare(reference: list, generated: list, variables: list) -> dict:
    ref = solutions(reference,variables)
    gen = solutions(generated,variables)
    lost, added = ref-gen, gen-ref
    if not lost and not added: category = 'Equivalent model'
    elif lost and not added: category = 'Valid syntax, over-constrained'
    elif added and not lost: category = 'Valid syntax, under-constrained'
    else: category = 'Valid model of the wrong problem'
    canonical = lambda cs: {tuple(sorted(set(c))) for c in cs}
    return {'semantic_category':category,'reference_solutions':len(ref),'generated_solutions':len(gen),
            'lost_solutions':len(lost),'added_solutions':len(added),
            'lost_counterexample':dict(zip(variables,min(lost))) if lost else None,
            'added_counterexample':dict(zip(variables,min(added))) if added else None,
            'missing_clauses':sorted(canonical(reference)-canonical(generated)),
            'extra_clauses':sorted(canonical(generated)-canonical(reference)),
            'review_note':'Set inclusion is exhaustive evidence; clause differences alone do not identify linguistic causes. Quantifier/arity category is not applicable to propositional syntax.'}


def evaluate(problem: dict, attempt: dict) -> dict:
    predicted = attempt['predicted_status']
    correctness = ('no-answer' if predicted not in ('SAT','UNSAT') else
                   'correct' if predicted == problem['ground_truth']['status'] else 'incorrect')
    error = attempt['error_category']
    detail = {}
    if attempt.get('clauses') is not None:
        detail = compare(problem['clauses'],attempt['clauses'],sorted(problem['variables'].values()))
    if error in ('parse_error','schema_error'): category = 'Malformed syntax'
    elif error == 'solver_timeout': category = 'Solver timeout'
    elif error: category = error
    elif detail and detail['semantic_category'] != 'Equivalent model': category = detail['semantic_category']
    elif correctness == 'incorrect': category = 'Wrong SAT/UNSAT result'
    else: category = ''
    return {'correctness':correctness,'taxonomy_category':category,**detail,
            'error_category':error or ('semantic_error' if category else '')}
