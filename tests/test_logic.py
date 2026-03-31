from func_hash import func_hash


def test_lambda_stability():
    # Two identical lambdas should have the same hash
    l1 = lambda x: x + 1
    l2 = lambda x: x + 1
    assert func_hash((l1,), {}) == func_hash((l2,), {})


def test_logic_invalidation():
    # Changing the logic must change the hash
    l1 = lambda x: x + 1
    l2 = lambda x: x + 2
    assert func_hash((l1,), {}) != func_hash((l2,), {})
