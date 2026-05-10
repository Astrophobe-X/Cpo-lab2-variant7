"""
Purely Functional, Immutable Hash Map using Separate Chaining.
Complies with PEP 8 (79 characters max per line) and uses Covariant Types.
"""

from __future__ import annotations
from typing import (
    TypeVar, Generic, Callable, Optional,
    Tuple, List, Iterator, Union, Any, Sequence
)

# Covariant Type Variables for immutable structures
K_co = TypeVar('K_co', covariant=True)
V_co = TypeVar('V_co', covariant=True)

# Standard Type Variables for input mapping
K2 = TypeVar('K2')
V2 = TypeVar('V2')
T = TypeVar('T')


class Node(Generic[K_co, V_co]):
    """Immutable Node for the separate chaining linked list."""
    __slots__ = ['key', 'value', 'nxt']

    def __init__(
        self,
        key: K_co,
        value: V_co,
        nxt: Optional[Node[K_co, V_co]] = None
    ) -> None:
        self.key = key
        self.value = value
        self.nxt = nxt


class HashMap(Generic[K_co, V_co]):
    """Immutable Dictionary based on a Hash-map."""
    def __init__(
        self,
        buckets: Optional[Tuple[Optional[Node[K_co, V_co]], ...]] = None,
        capacity: int = 16
    ) -> None:
        self.capacity = capacity
        if buckets is None:
            self.buckets: Tuple[Optional[Node[K_co, V_co]], ...] = (
                tuple([None] * capacity)
            )
        else:
            self.buckets = buckets

    def __iter__(self) -> Iterator[K_co]:
        def _iter_chain(node: Optional[Node[K_co, V_co]]) -> List[K_co]:
            if node is None:
                return []
            return [node.key] + _iter_chain(node.nxt)

        def _iter_buckets(idx: int = 0) -> List[K_co]:
            if idx >= len(self.buckets):
                return []
            return _iter_chain(self.buckets[idx]) + _iter_buckets(idx + 1)

        return iter(_iter_buckets(0))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashMap):
            return False
        if length(self) != length(other):
            return False

        def _check_chain(node: Optional[Node[K_co, V_co]]) -> bool:
            if node is None:
                return True
            target_idx = _hash_key(node.key, other.capacity)
            o_node = _get_node(other.buckets[target_idx], node.key)
            if o_node is None or o_node.value != node.value:
                return False
            return _check_chain(node.nxt)

        def _check_buckets(idx: int = 0) -> bool:
            if idx >= len(self.buckets):
                return True
            return (
                _check_chain(self.buckets[idx]) and
                _check_buckets(idx + 1)
            )

        return _check_buckets()

    def __str__(self) -> str:
        def _chain_str(node: Optional[Node[K_co, V_co]]) -> List[str]:
            if node is None:
                return []
            cur_str = f"{repr(node.key)}: {repr(node.value)}"
            return [cur_str] + _chain_str(node.nxt)

        def _buckets_str(idx: int = 0) -> List[str]:
            if idx >= len(self.buckets):
                return []
            return _chain_str(self.buckets[idx]) + _buckets_str(idx + 1)

        items = _buckets_str()
        return "{" + ", ".join(items) + "}"


# ==========================================
# Internal Recursive Helper Functions
# ==========================================

def _hash_key(key: Any, capacity: int) -> int:
    """Computes the bucket index for a given key."""
    return hash(key) % capacity


def _get_node(
    node: Optional[Node[K_co, V_co]], key: Any
) -> Optional[Node[K_co, V_co]]:
    """Recursively searches for a node by key."""
    if node is None:
        return None
    if node.key == key:
        return node
    return _get_node(node.nxt, key)


def _cons_chain(
    key: K2, value: V2, node: Optional[Node[K_co, V_co]]
) -> Node[Union[K_co, K2], Union[V_co, V2]]:
    """Recursively constructs a new chain, safely widening types."""
    if node is None:
        return Node(key, value, None)
    if node.key == key:
        return Node(key, value, node.nxt)
    return Node(node.key, node.value, _cons_chain(key, value, node.nxt))


def _remove_chain(
    key: Any, node: Optional[Node[K_co, V_co]]
) -> Optional[Node[K_co, V_co]]:
    """Recursively removes a node by key, returning a new chain."""
    if node is None:
        return None
    if node.key == key:
        return node.nxt
    return Node(node.key, node.value, _remove_chain(key, node.nxt))


def _member_chain(key: Any, node: Optional[Node[K_co, V_co]]) -> bool:
    """Recursively checks if a key exists in a given chain."""
    if node is None:
        return False
    if node.key == key:
        return True
    return _member_chain(key, node.nxt)


# ==========================================
# Function-style Public API
# ==========================================

def empty() -> HashMap[Any, Any]:
    """Creates and returns an empty HashMap."""
    return HashMap()


def cons(
    key: K2, value: V2, d: HashMap[K_co, V_co]
) -> HashMap[Union[K_co, K2], Union[V_co, V2]]:
    """Inserts a key-value pair, returning a new instance."""
    idx = _hash_key(key, d.capacity)
    new_chain = _cons_chain(key, value, d.buckets[idx])

    new_buckets = d.buckets[:idx] + (new_chain,) + d.buckets[idx + 1:]
    return HashMap(new_buckets, d.capacity)


def remove(d: HashMap[K_co, V_co], key: Any) -> HashMap[K_co, V_co]:
    """Removes a key, returning a new instance via structural sharing."""
    idx = _hash_key(key, d.capacity)
    if not _member_chain(key, d.buckets[idx]):
        return d

    new_chain = _remove_chain(key, d.buckets[idx])
    new_buckets = d.buckets[:idx] + (new_chain,) + d.buckets[idx + 1:]
    return HashMap(new_buckets, d.capacity)


def length(d: HashMap[K_co, V_co]) -> int:
    """Calculates the total number of key-value pairs."""
    def _len_chain(node: Optional[Node[K_co, V_co]]) -> int:
        return 0 if node is None else 1 + _len_chain(node.nxt)

    def _len_buckets(
        buckets: Tuple[Optional[Node[K_co, V_co]], ...], idx: int = 0
    ) -> int:
        if idx >= len(buckets):
            return 0
        return _len_chain(buckets[idx]) + _len_buckets(buckets, idx + 1)

    return _len_buckets(d.buckets)


def member(key: Any, d: HashMap[K_co, V_co]) -> bool:
    """Checks if a key exists in the HashMap."""
    idx = _hash_key(key, d.capacity)
    return _member_chain(key, d.buckets[idx])


def to_list(d: HashMap[K_co, V_co]) -> List[Tuple[K_co, V_co]]:
    """Converts the HashMap into a list of key-value tuples."""
    def _chain_to_list(
        node: Optional[Node[K_co, V_co]]
    ) -> List[Tuple[K_co, V_co]]:
        if node is None:
            return []
        return [(node.key, node.value)] + _chain_to_list(node.nxt)

    def _buckets_to_list(
        buckets: Tuple[Optional[Node[K_co, V_co]], ...], idx: int = 0
    ) -> List[Tuple[K_co, V_co]]:
        if idx >= len(buckets):
            return []
        return (
            _chain_to_list(buckets[idx]) +
            _buckets_to_list(buckets, idx + 1)
        )

    return _buckets_to_list(d.buckets)


def from_list(lst: Sequence[Tuple[K2, V2]]) -> HashMap[K2, V2]:
    """Constructs a HashMap from a sequence (e.g., list) of tuples."""
    def _from_list_rec(
        idx: int, current_map: HashMap[Any, Any]
    ) -> HashMap[Any, Any]:
        if idx >= len(lst):
            return current_map
        k, v = lst[idx]
        return _from_list_rec(idx + 1, cons(k, v, current_map))

    return _from_list_rec(0, empty())


def find(
    d: HashMap[K_co, V_co],
    predicate: Callable[[Tuple[K_co, V_co]], bool]
) -> Optional[Tuple[K_co, V_co]]:
    """Finds the first key-value pair that satisfies the predicate."""
    def _find_chain(
        node: Optional[Node[K_co, V_co]]
    ) -> Optional[Tuple[K_co, V_co]]:
        if node is None:
            return None
        if predicate((node.key, node.value)):
            return (node.key, node.value)
        return _find_chain(node.nxt)

    def _find_buckets(
        buckets: Tuple[Optional[Node[K_co, V_co]], ...], idx: int = 0
    ) -> Optional[Tuple[K_co, V_co]]:
        if idx >= len(buckets):
            return None
        res = _find_chain(buckets[idx])
        if res is not None:
            return res
        return _find_buckets(buckets, idx + 1)

    return _find_buckets(d.buckets)


def filter(
    d: HashMap[K_co, V_co],
    predicate: Callable[[Tuple[K_co, V_co]], bool]
) -> HashMap[K_co, V_co]:
    """Returns a new HashMap with pairs satisfying the predicate."""
    def _filter_chain(
        node: Optional[Node[K_co, V_co]]
    ) -> List[Tuple[K_co, V_co]]:
        if node is None:
            return []
        if predicate((node.key, node.value)):
            return [(node.key, node.value)] + _filter_chain(node.nxt)
        return _filter_chain(node.nxt)

    def _filter_buckets(
        buckets: Tuple[Optional[Node[K_co, V_co]], ...], idx: int = 0
    ) -> List[Tuple[K_co, V_co]]:
        if idx >= len(buckets):
            return []
        return (
            _filter_chain(buckets[idx]) +
            _filter_buckets(buckets, idx + 1)
        )

    return from_list(_filter_buckets(d.buckets))


def map_dict(
    d: HashMap[K_co, V_co],
    func: Callable[[Tuple[K_co, V_co]], Tuple[K2, V2]]
) -> HashMap[K2, V2]:
    """Applies a function to all pairs, returning a new HashMap."""
    def _map_chain(
        node: Optional[Node[K_co, V_co]]
    ) -> List[Tuple[K2, V2]]:
        if node is None:
            return []
        return [func((node.key, node.value))] + _map_chain(node.nxt)

    def _map_buckets(
        buckets: Tuple[Optional[Node[K_co, V_co]], ...], idx: int = 0
    ) -> List[Tuple[K2, V2]]:
        if idx >= len(buckets):
            return []
        return _map_chain(buckets[idx]) + _map_buckets(buckets, idx + 1)

    return from_list(_map_buckets(d.buckets))


def reduce(
    d: HashMap[K_co, V_co],
    func: Callable[[T, Tuple[K_co, V_co]], T],
    init: T
) -> T:
    """Reduces the HashMap to a single value using an accumulator."""
    lst = to_list(d)

    def _reduce_rec(idx: int, acc: T) -> T:
        if idx >= len(lst):
            return acc
        return _reduce_rec(idx + 1, func(acc, lst[idx]))

    return _reduce_rec(0, init)


def concat(
    d1: HashMap[K_co, V_co], d2: HashMap[K2, V2]
) -> HashMap[Union[K_co, K2], Union[V_co, V2]]:
    """Concatenates two HashMaps safely using Sequence input."""
    # The union of types is safely passed into the Sequence protocol
    merged_list: Sequence[Tuple[Union[K_co, K2], Union[V_co, V2]]] = (
        to_list(d1) + to_list(d2)
    )
    return from_list(merged_list)


def iterator(d: HashMap[K_co, V_co]) -> Iterator[K_co]:
    """Returns an iterator over the keys."""
    return iter(d)
