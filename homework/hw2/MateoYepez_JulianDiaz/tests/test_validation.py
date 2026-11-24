from satlab.validation import verify_assignment
from satlab.taxonomy import compare

def test_witness_and_set_inclusion():
    assert verify_assignment([], {})
    assert not verify_assignment([[]],{1:True})
    assert compare([[1]],[[1],[2]],[1,2])['semantic_category']=='Valid syntax, over-constrained'
    assert compare([[1],[2]],[[1]],[1,2])['semantic_category']=='Valid syntax, under-constrained'
    result=compare([[1]],[[2]],[1,2])
    assert result['semantic_category']=='Valid model of the wrong problem'
    assert result['added_counterexample'] and result['lost_counterexample']
    assert compare([[1]],[[1],[1,2]],[1,2])['semantic_category']=='Equivalent model'
