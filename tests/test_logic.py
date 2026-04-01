from functools import partial
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


def test_different_partials_differ():
    p1 = partial(wait_for_selector, selector=".title")
    p2 = partial(wait_for_selector, selector=".rating")
    assert func_hash((p1,), {}) != func_hash((p2,), {})


def test_equal_partials_are_equal():
    p1 = partial(wait_for_selector, selector=".title")
    p2 = partial(wait_for_selector2, selector=".title")
    assert func_hash((p1,), {}) == func_hash((p2,), {})


def wait_for_selector(p: "Page", selector: str) -> None:
    p.wait_for_selector(selector)


def wait_for_selector2(p: "Page", selector: str) -> None:
    p.wait_for_selector(selector)
