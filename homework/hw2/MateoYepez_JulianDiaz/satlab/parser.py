"""Strict JSON schema validation, with no semantic repairs."""
import json
from .validation import validate_cnf

class ParseError(ValueError):
    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


def _unique(pairs):
    result = {}
    for k,v in pairs:
        if k in result:
            raise ValueError(f'duplicate JSON key: {k}')
        result[k] = v
    return result


def parse(raw: str, variables: dict, direct: bool = False) -> dict:
    try:
        data = json.loads(raw,object_pairs_hook=_unique,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'invalid JSON constant: {x}')))
    except (ValueError,TypeError) as exc:
        raise ParseError('parse_error',str(exc)) from exc
    try:
        required = {'answer','explanation'} if direct else {'clauses'}
        if not isinstance(data,dict) or set(data) != required:
            raise ValueError(f'expected exactly these keys: {sorted(required)}')
        if direct:
            if data['answer'] not in ('SAT','UNSAT') or not isinstance(data['explanation'],str):
                raise ValueError('answer must be SAT/UNSAT and explanation must be a string')
        else:
            validate_cnf(data['clauses'],set(variables.values()))
    except (ValueError,TypeError) as exc:
        raise ParseError('schema_error',str(exc)) from exc
    return data
