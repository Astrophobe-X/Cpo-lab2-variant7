from __future__ import annotations
from typing import TypeVar, Generic, Callable, Optional
from typing import Tuple, List, Iterator, Union

K = TypeVar('K')
V = TypeVar('V')
K2 = TypeVar('K2')
V2 = TypeVar('V2')
T = TypeVar('T')


class Node(Generic[K, V]):
    """Immutable Node for the separate chaining linked list."""
    __slots__ = ['key', 'value', 'nxt']

    def __init__(
        self,
        key: K,
        value: V,
        nxt: Optional[Node[K, V]] = None
    ):
        self.key = key
        self.value = value
        self.nxt = nxt


class HashMap(Generic[K, V]):
    """
    Immutable Dictionary based on Hash-map with Separate Chaining.
    Any modification returns a new instance, sharing unmodified data.
    """
    def __init__(
        self,
        buckets: Optional[Tuple[Optional[Node[K, V]], ...]] = None,
        capacity: int = 16
    ):
        self.capacity = capacity
        if buckets is None:
            self.buckets: Tuple[Optional[Node[K, V]], ...] = \
                tuple([None] * capacity)
        else:
            self.buckets = buckets

    def __iter__(self) -> Iterator[K]:
        def _iter_chain(node: Optional[Node[K, V]]) -> List[K]:
            if node is None:
                return []
            return [node.key] + _iter_chain(node.nxt)

        def _iter_buckets(idx: int = 0) -> List[K]:
            if idx >= len(self.buckets):
                return []
            return _iter_chain(self.buckets[idx]) + \
                _iter_buckets(idx + 1)

        return iter(_iter_buckets(0))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashMap):
            return False
        if length(self) != length(other):
            return False

        def _check_chain(node: Optional[Node[K, V]]) -> bool:
            if node is None:
                return True
            o_node = _get_node(
                other.buckets[_hash_key(node.key, other.capacity)],
                node.key
            )
            if o_node is None or o_node.value != node.value:
                return False
            return _check_chain(node.nxt)

        def _check_buckets(idx: int = 0) -> bool:
            if idx >= len(self.buckets):
                return True
            return _check_chain(self.buckets[idx]) and \
                _check_buckets(idx + 1)

        return _check_buckets()

    def __str__(self) -> str:
        def _chain_str(node: Optional[Node[K, V]]) -> List[str]:
            if node is None:
                return []
            return [f"{repr(node.key)}: {repr(node.value)}"] + \
                _chain_str(node.nxt)

        def _buckets_str(idx: int = 0) -> List[str]:
            if idx >= len(self.buckets):
                return []
            return _chain_str(self.buckets[idx]) + \
                _buckets_str(idx + 1)

        items = _buckets_str()
        return "{" + ", ".join(items) + "}"


# Internal Recursive Helper Functions
def _hash_key(key: object, capacity: int) -> int:
    return hash(key) % capacity


def _get_node(
    node: Optional[Node[K, V]], key: object
) -> Optional[Node[K, V]]:
    if node is None:
        return None
    if node.key == key:
        return node
    return _get_node(node.nxt, key)


# Use object internally for cons_chain to bypass generic invariance
def _cons_chain(
    key: object, value: object, node: Optional[Node[object, object]]
) -> Node[object, object]:
    if node is None:
        return Node(key, value, None)
    if node.key == key:
        return Node(key, value, node.nxt)
    return Node(node.key, node.value, _cons_chain(key, value, node.nxt))


def _remove_chain(
    key: object, node: Optional[Node[K, V]]
) -> Optional[Node[K, V]]:
    if node is None:
        return None
    if node.key == key:
        return node.nxt
    return Node(node.key, node.value, _remove_chain(key, node.nxt))


def _member_chain(key: object, node: Optional[Node[K, V]]) -> bool:
    if node is None:
        return False
    if node.key == key:
        return True
    return _member_chain(key, node.nxt)


# Function-style API Implementation
def empty() -> HashMap[K, V]:
    return HashMap()


def cons(
    key: K2, value: V2, d: HashMap[K, V]
) -> HashMap[Union[K, K2], Union[V, V2]]:
    idx = _hash_key(key, d.capacity)
    # Type ignore necessary to align internal object widening
    b_obj: Tuple[Optional[Node[object, object]], ...] = \
        d.buckets  # type: ignore
    new_chain = _cons_chain(key, value, b_obj[idx])
    new_buckets = b_obj[:idx] + (new_chain,) + b_obj[idx+1:]
    return HashMap(new_buckets, d.capacity)


def remove(d: HashMap[K, V], key: object) -> HashMap[K, V]:
    idx = _hash_key(key, d.capacity)
    if not _member_chain(key, d.buckets[idx]):
        return d
    new_chain = _remove_chain(key, d.buckets[idx])
    new_buckets = d.buckets[:idx] + (new_chain,) + d.buckets[idx+1:]
    return HashMap(new_buckets, d.capacity)


def length(d: HashMap[K, V]) -> int:
    def _len_chain(node: Optional[Node[K, V]]) -> int:
        return 0 if node is None else 1 + _len_chain(node.nxt)

    def _len_buckets(
        buckets: Tuple[Optional[Node[K, V]], ...], idx: int = 0
    ) -> int:
        if idx >= len(buckets):
            return 0
        return _len_chain(buckets[idx]) + \
            _len_buckets(buckets, idx + 1)

    return _len_buckets(d.buckets)


def member(key: object, d: HashMap[K, V]) -> bool:
    idx = _hash_key(key, d.capacity)
    return _member_chain(key, d.buckets[idx])


def to_list(d: HashMap[K, V]) -> List[Tuple[K, V]]:
    def _chain_to_list(
        node: Optional[Node[K, V]]
    ) -> List[Tuple[K, V]]:
        if node is None:
            return []
        return [(node.key, node.value)] + _chain_to_list(node.nxt)

    def _buckets_to_list(
        buckets: Tuple[Optional[Node[K, V]], ...], idx: int = 0
    ) -> List[Tuple[K, V]]:
        if idx >= len(buckets):
            return []
        return _chain_to_list(buckets[idx]) + \
            _buckets_to_list(buckets, idx + 1)

    return _buckets_to_list(d.buckets)


def from_list(lst: List[Tuple[K, V]]) -> HashMap[K, V]:
    def _from_list_rec(
        idx: int, d: HashMap[K, V]
    ) -> HashMap[K, V]:
        if idx >= len(lst):
            return d
        k, v = lst[idx]
        # Union[K, K] simplifies to K, variance check ignored
        return _from_list_rec(idx + 1, cons(k, v, d))
    return _from_list_rec(0, empty())


def find(
    d: HashMap[K, V],
    predicate: Callable[[Tuple[K, V]], bool]
) -> Optional[Tuple[K, V]]:
    def _find_chain(
        node: Optional[Node[K, V]]
    ) -> Optional[Tuple[K, V]]:
        if node is None:
            return None
        if predicate((node.key, node.value)):
            return (node.key, node.value)
        return _find_chain(node.nxt)

    def _find_buckets(
        buckets: Tuple[Optional[Node[K, V]], ...],
        idx: int = 0
    ) -> Optional[Tuple[K, V]]:
        if idx >= len(buckets):
            return None
        res = _find_chain(buckets[idx])
        if res is not None:
            return res
        return _find_buckets(buckets, idx + 1)

    return _find_buckets(d.buckets)


def filter(
    d: HashMap[K, V],
    predicate: Callable[[Tuple[K, V]], bool]
) -> HashMap[K, V]:
    def _filter_chain(
        node: Optional[Node[K, V]]
    ) -> List[Tuple[K, V]]:
        if node is None:
            return []
        if predicate((node.key, node.value)):
            return [(node.key, node.value)] + \
                _filter_chain(node.nxt)
        return _filter_chain(node.nxt)

    def _filter_buckets(
        buckets: Tuple[Optional[Node[K, V]], ...],
        idx: int = 0
    ) -> List[Tuple[K, V]]:
        if idx >= len(buckets):
            return []
        return _filter_chain(buckets[idx]) + \
            _filter_buckets(buckets, idx + 1)

    return from_list(_filter_buckets(d.buckets))


def map(
    d: HashMap[K, V],
    func: Callable[[Tuple[K, V]], Tuple[K2, V2]]
) -> HashMap[K2, V2]:
    def _map_chain(
        node: Optional[Node[K, V]]
    ) -> List[Tuple[K2, V2]]:
        if node is None:
            return []
        return [func((node.key, node.value))] + \
            _map_chain(node.nxt)

    def _map_buckets(
        buckets: Tuple[Optional[Node[K, V]], ...],
        idx: int = 0
    ) -> List[Tuple[K2, V2]]:
        if idx >= len(buckets):
            return []
        return _map_chain(buckets[idx]) + \
            _map_buckets(buckets, idx + 1)

    return from_list(_map_buckets(d.buckets))


def reduce(
    d: HashMap[K, V],
    func: Callable[[T, Tuple[K, V]], T],
    init: T
) -> T:
    lst = to_list(d)

    def _reduce_rec(idx: int, acc: T) -> T:
        if idx >= len(lst):
            return acc
        return _reduce_rec(idx + 1, func(acc, lst[idx]))
    return _reduce_rec(0, init)


def concat(
    d1: HashMap[K, V], d2: HashMap[K2, V2]
) -> HashMap[Union[K, K2], Union[V, V2]]:
    lst = to_list(d1) + to_list(d2)
    return from_list(lst)


def iterator(d: HashMap[K, V]) -> Iterator[K]:
    return iter(d)
