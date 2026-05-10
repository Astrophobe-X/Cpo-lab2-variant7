import itertools
import hash_dict as hm


# Variant 7 Mandatory API Test
def test_api():
    empty_dict = hm.empty()
    l1 = hm.cons(None, "c", hm.cons(2, "b", hm.cons("a", 1, empty_dict)))
    l2 = hm.cons("a", 1, hm.cons(None, "c", hm.cons(2, "b", empty_dict)))
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

    assert hm.length(empty_dict) == 0
    assert hm.length(l1) == 3
    assert hm.length(l2) == 3

    assert str(hm.remove(l1, None)) in [
        "{2: 'b', 'a': 1}", "{'a': 1, 2: 'b'}"
    ]
    assert str(hm.remove(l1, "a")) in [
        "{2: 'b', None: 'c'}", "{None: 'c', 2: 'b'}"
    ]

    assert not hm.member(None, empty_dict)
    assert hm.member(None, l1)
    assert hm.member("a", l1)
    assert hm.member(2, l1)
    assert not hm.member(3, l1)

    perms1 = list(map(
        list, itertools.permutations([("a", 1), (2, "b"), (None, "c")])
    ))
    assert hm.to_list(l1) in perms1

    assert l1 == hm.from_list([("a", 1), (2, "b"), (None, "c")])
    assert l1 == hm.from_list([
        (2, "B"), ("a", 1), (2, "b"), (None, "c")
    ])

    assert hm.concat(l1, l2) == hm.from_list([
        (2, "B"), ("a", 1), (2, "b"), (None, "c")
    ])

    buf = []
    for e in l1:
        buf.append(e)
    perms2 = list(map(
        list, itertools.permutations(["a", 2, None])
    ))
    assert buf in perms2

    lst = list(map(lambda e: e[0], hm.to_list(l1))) + \
        list(map(lambda e: e[0], hm.to_list(l2)))
    for e in l1:
        lst.remove(e)
    for e in l2:
        lst.remove(e)
    assert lst == []


# Additional Tests: Immutability & Monoid
def test_immutability():
    """Ensure operations do not modify the original instance"""
    d1 = hm.empty()
    d2 = hm.cons("x", 1, d1)
    d3 = hm.cons("y", 2, d2)

    assert hm.length(d1) == 0
    assert hm.length(d2) == 1
    assert hm.member("x", d2) and not hm.member("x", d1)

    d4 = hm.remove(d3, "x")
    assert hm.member("x", d3) and not hm.member("x", d4)


def test_monoid_associativity():
    """Monoid: concat(d1, concat(d2, d3)) == concat(concat(d1, d2), d3)"""
    d1 = hm.from_list([("a", 1)])
    d2 = hm.from_list([("b", 2)])
    d3 = hm.from_list([("c", 3)])

    left = hm.concat(d1, hm.concat(d2, d3))
    right = hm.concat(hm.concat(d1, d2), d3)
    assert left == right


def test_monoid_identity():
    """Monoid: concat(d, empty) == d and concat(empty, d) == d"""
    d = hm.from_list([("a", 1)])
    assert hm.concat(d, hm.empty()) == d
    assert hm.concat(hm.empty(), d) == d


# Additional Tests: Higher-Order Functions
def test_filter_map_reduce():
    d = hm.from_list([("a", 1), ("b", 2), ("c", 3), ("d", 4)])

    # Filter even values
    filtered = hm.filter(d, lambda kv: kv[1] % 2 == 0)
    perms3 = list(map(
        list, itertools.permutations([("b", 2), ("d", 4)])
    ))
    assert hm.to_list(filtered) in perms3

    # Map values by adding 10
    mapped = hm.map(d, lambda kv: (kv[0], kv[1] + 10))
    perms4 = list(map(
        list,
        itertools.permutations([("a", 11), ("b", 12), ("c", 13), ("d", 14)])
    ))
    assert hm.to_list(mapped) in perms4

    # Reduce to sum of values
    total = hm.reduce(d, lambda acc, kv: acc + kv[1], 0)
    assert total == 10


def test_find():
    d = hm.from_list([("a", 1), ("b", 2)])
    assert hm.find(d, lambda kv: kv[1] == 2) == ("b", 2)
    assert hm.find(d, lambda kv: kv[1] == 99) is None


# Property-Based Testing Simulation
def test_pbt_conversion():
    """Property: from_list(to_list(d)) == d"""
    pairs = [("x", 1), ("y", 2), ("z", 3)]
    d = hm.from_list(pairs)
    assert d == hm.from_list(hm.to_list(d))


def test_pbt_member_from_list():
    """Property: If k in list, member(k, from_list(list)) is True"""
    pairs = [("p", 10), (None, "v"), (42, True)]
    d = hm.from_list(pairs)
    for k, v in pairs:
        assert hm.member(k, d)
    assert not hm.member("missing", d)
