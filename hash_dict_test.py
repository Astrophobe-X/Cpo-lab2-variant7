import itertools
import pytest
from hypothesis import given
import hypothesis.strategies as st

import hash_dict as hm


def test_api():
    """Mandatory API tests for Variant 7."""
    empty_dict = hm.empty()

    # Build structures
    l1 = hm.cons(
        None, "c", hm.cons(2, "b", hm.cons("a", 1, empty_dict))
    )
    l2 = hm.cons(
        "a", 1, hm.cons(None, "c", hm.cons(2, "b", empty_dict))
    )

    # String serialization and equality checks
    assert str(empty_dict) == "{}"
    assert str(l1) in [
        "{'a': 1, 2: 'b', None: 'c'}",
        "{'a': 1, None: 'c', 2: 'b'}",
        "{2: 'b', 'a': 1, None: 'c'}",
        "{2: 'b', None: 'c', 'a': 1}",
        "{None: 'c', 2: 'b', 'a': 1}",
        "{None: 'c', 'a': 1, 2: 'b'}",
    ]
    assert empty_dict != l1
    assert empty_dict != l2
    assert l1 == l2

    # Length and membership
    assert hm.length(empty_dict) == 0
    assert hm.length(l1) == 3
    assert hm.length(l2) == 3

    assert str(hm.remove(l1, None)) in [
        "{2: 'b', 'a': 1}",
        "{'a': 1, 2: 'b'}"
    ]
    assert str(hm.remove(l1, "a")) in [
        "{2: 'b', None: 'c'}",
        "{None: 'c', 2: 'b'}"
    ]

    assert not hm.member(None, empty_dict)
    assert hm.member(None, l1)
    assert hm.member("a", l1)
    assert hm.member(2, l1)
    assert not hm.member(3, l1)

    # Conversion checks
    perms1 = list(
        map(
            list,
            itertools.permutations([("a", 1), (2, "b"), (None, "c")])
        )
    )
    assert hm.to_list(l1) in perms1

    assert l1 == hm.from_list([("a", 1), (2, "b"), (None, "c")])
    assert l1 == hm.from_list([
        (2, "B"), ("a", 1), (2, "b"), (None, "c")
    ])

    # Concat check
    assert hm.concat(l1, l2) == hm.from_list([
        (2, "B"), ("a", 1), (2, "b"), (None, "c")
    ])

    # Iterator check
    buf = []
    for e in l1:
        buf.append(e)
    perms2 = list(
        map(list, itertools.permutations(["a", 2, None]))
    )
    assert buf in perms2

    # Complex map and remove check
    lst1 = list(map(lambda e: e[0], hm.to_list(l1)))
    lst2 = list(map(lambda e: e[0], hm.to_list(l2)))
    lst = lst1 + lst2

    for e in l1:
        lst.remove(e)
    for e in l2:
        lst.remove(e)
    assert lst == []


def test_immutability():
    """Ensure operations do not pollute original memory state."""
    d1 = hm.empty()
    d2 = hm.cons("x", 1, d1)
    d3 = hm.cons("y", 2, d2)

    assert hm.length(d1) == 0
    assert hm.length(d2) == 1
    assert hm.member("x", d2) and not hm.member("x", d1)

    d4 = hm.remove(d3, "x")
    assert hm.member("x", d3) and not hm.member("x", d4)


def test_filter_map_reduce():
    """Validate higher-order functions loop."""
    d = hm.from_list([("a", 1), ("b", 2), ("c", 3), ("d", 4)])

    # Filter
    filtered = hm.filter(d, lambda kv: kv[1] % 2 == 0)
    assert hm.length(filtered) == 2
    assert hm.member("b", filtered) and hm.member("d", filtered)

    # Map
    mapped = hm.map_dict(d, lambda kv: (kv[0], kv[1] + 10))
    assert hm.find(d, lambda kv: kv[0] == "a") == ("a", 1)
    assert hm.find(mapped, lambda kv: kv[0] == "a") == ("a", 11)

    # Reduce
    total = hm.reduce(d, lambda acc, kv: acc + kv[1], 0)
    assert total == 10

    # Find
    assert hm.find(d, lambda kv: kv[1] == 2) == ("b", 2)
    assert hm.find(d, lambda kv: kv[1] == 99) is None


# Strategy definition for Property-Based Testing
kv_strategy = st.tuples(
    st.one_of(st.integers(), st.text(), st.none()),
    st.one_of(st.integers(), st.text())
)


@given(st.lists(kv_strategy))
def test_pbt_conversion_identity(pairs):
    """Property: Idempotence of conversion."""
    d = hm.from_list(pairs)
    assert hm.length(d) <= len(pairs)
    assert d == hm.from_list(hm.to_list(d))


@given(
    st.lists(kv_strategy),
    st.lists(kv_strategy),
    st.lists(kv_strategy)
)
def test_pbt_monoid_associativity(pairs1, pairs2, pairs3):
    """Property: Monoid associativity."""
    d1 = hm.from_list(pairs1)
    d2 = hm.from_list(pairs2)
    d3 = hm.from_list(pairs3)

    left_assoc = hm.concat(d1, hm.concat(d2, d3))
    right_assoc = hm.concat(hm.concat(d1, d2), d3)
    assert left_assoc == right_assoc


@given(st.lists(kv_strategy))
def test_pbt_monoid_identity(pairs):
    """Property: Monoid identity law."""
    d = hm.from_list(pairs)
    empty_d = hm.empty()

    assert hm.concat(d, empty_d) == d
    assert hm.concat(empty_d, d) == d
