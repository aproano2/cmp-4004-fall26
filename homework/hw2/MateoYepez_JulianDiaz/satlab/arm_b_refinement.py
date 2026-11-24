"""At most three repairs; no reference data and no UNSAT-as-error policy."""
from .arm_b import inspect_response
from .prompts import initial, feedback

REPAIRABLE = {'parse_error','schema_error','solver_error','solver_timeout'}


def run(public: dict, client, repeat: int, timeout: float, first: dict,
        max_repairs: int = 3, checkpoint=None, prior=None) -> list[dict]:
    if not 0 <= max_repairs <= 3:
        raise ValueError('max_repairs must be between 0 and 3')
    attempts = list(prior) if prior else [first]
    if attempts[0] != first:
        raise ValueError('refinement must reuse exact B initial attempt')
    messages = initial(public,'B')
    for old in attempts[:-1]:
        messages = feedback(messages,old['call']['raw'],old['error_message'])
    while len(attempts) <= max_repairs and attempts[-1]['error_category'] in REPAIRABLE:
        previous = attempts[-1]
        messages = feedback(messages,previous['call']['raw'],previous['error_message'])
        call = client.call(messages,public['id'],'B-prime',repeat,len(attempts))
        attempts.append(inspect_response(public,call,timeout))
        if checkpoint: checkpoint(attempts)
    return attempts
