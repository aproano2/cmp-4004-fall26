import pytest
from satlab.parser import parse, ParseError
from satlab.validation import cnf_warnings

@pytest.mark.parametrize('raw',['not json','```json\n{}\n```','{"clauses":[],"clauses":[]}','{"clauses":[[NaN]]}'])
def test_invalid_json(raw):
    with pytest.raises(ParseError) as exc: parse(raw,{'a':1})
    assert exc.value.category=='parse_error'

@pytest.mark.parametrize('raw',['[]','{}','{"clauses":[[true]]}','{"clauses":[[0]]}','{"clauses":[[2]]}','{"clauses":[[1.0]]}','{"clauses":[1]}'])
def test_invalid_schema(raw):
    with pytest.raises(ParseError) as exc: parse(raw,{'a':1})
    assert exc.value.category=='schema_error'


def test_empty_clauses_tautologies_preserved():
    assert parse(' {"clauses":[[],[1,-1,1]]} ',{'a':1})['clauses']==[[],[1,-1,1]]
    assert len(cnf_warnings([[],[1,-1,1],[1,-1,1]]))==4


def test_direct():
    assert parse('{"answer":"SAT","explanation":"ok"}',{},True)['answer']=='SAT'
    with pytest.raises(ParseError): parse('{"answer":"maybe","explanation":""}',{},True)
