"""Unprivileged translation and solver pipeline."""
import time
from dataclasses import asdict
from .parser import parse, ParseError
from .solver import solve
from .prompts import initial
from .validation import cnf_warnings


def inspect_response(public: dict, call: dict, timeout: float, direct=False) -> dict:
    start = time.perf_counter()
    attempt = {'call':call,'iteration':call['iteration'],'predicted_status':'NO_ANSWER',
               'solver_status':'NOT_RUN','solver_time_seconds':0.0,'clauses':None,
               'error_category':call['error_category'],'error_message':call['error_message'],
               'warnings':[], 'assignment':None}
    if not attempt['error_category']:
        try:
            parsed = parse(call['raw'],public['variables'],direct=direct)
            if direct:
                attempt['predicted_status'] = parsed['answer']
            else:
                clauses = parsed['clauses']
                attempt['clauses'] = clauses
                attempt['warnings'] = cnf_warnings(clauses)
                result = solve(clauses, public['variables'].values(),timeout)
                attempt.update(solver_status=result.status,solver_time_seconds=result.seconds,
                               assignment=result.assignment,solver_stats=result.stats)
                if result.status in ('SAT','UNSAT'):
                    attempt['predicted_status'] = result.status
                else:
                    attempt['error_category'] = 'solver_timeout' if result.status == 'TIMEOUT' else 'solver_error'
                    attempt['error_message'] = result.error
        except ParseError as exc:
            attempt.update(error_category=exc.category,error_message=str(exc))
    attempt['detectable_error'] = bool(attempt['error_category'])
    attempt['processing_seconds'] = time.perf_counter()-start
    attempt['parse_validation_seconds'] = max(0,attempt['processing_seconds']-attempt['solver_time_seconds'])
    return attempt


def run(public: dict, client, repeat: int, timeout: float) -> dict:
    messages = initial(public,'B')
    call = client.call(messages,public['id'],'B',repeat,0)
    return inspect_response(public,call,timeout)
