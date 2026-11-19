from satlab.dataset import load_dataset, validate_dataset, hashes, ROOT

def test_originals_and_ground_truth():
    assert hashes() == hashes(ROOT.parent / 'HW2-SAT-dataset/problems')
    rows = validate_dataset(load_dataset())
    assert len(rows) == 20
    assert all(r['valid'] for r in rows), rows
