# GROUP-7 - lab 2 - variant 7

This project implements an immutable Dictionary based on a Hash-map
using Separate Chaining. It is built strictly adhering to functional
programming principles, utilizing recursion instead of loops, and
ensuring no in-place mutations occur.

## Project structure

- `hash_dict.py` -- implementation of `HashMap` and `Node` classes
  with immutable separate chaining logic and a function-style API.
- `hash_dict_test.py` -- unit, PBT, monoid, and immutability tests
  for `HashMap`.

## Features

- Immutable Dictionary based on Hash-map with Separate Chaining.
- Function-style API (`cons`, `remove`, `member`, `length`, etc.).
- Monoid properties: associativity and identity (`empty`, `concat`).
- PBT: `test_pbt_conversion`, `test_pbt_member_from_list`.
- Immutability guarantees with structural sharing.

## Contribution

- ZHENG Rongzhen(1661342449@qq.com) -- all work.

## Changelog

- 13.05.2026 - 2
  Add PBT tests.
- 10.05.2026 - 2
  Add unit, monoid, and immutability tests.
- 8.05.2026 - 1
  Add hash_dict.py and hash_dict_test.py.
- 6.05.2026 - 0
  Initial project structure.

## Design notes

- **Immutability via Tuples:** Buckets are stored as a `Tuple` instead
  of a `list` to guarantee physical immutability at the language level.
- **Recursive Implementation:** All traversals (buckets and chains) use
  recursive helper functions instead of `for`/`while` loops.
- **Generic Invariance Bypass:** Python's type system is invariant.
  Inserting a new key type (e.g., `None` into `str`) requires type
  widening (`K | K2`). To prevent Pylance/mypy errors, internal chain
  helpers (`_cons_chain`) use `object` types. This isolates the type
  compromise while keeping the public API strictly typed.
- **Structural Sharing:** `remove` and `cons` reuse unchanged nodes and
  bucket references to minimize memory overhead.
- **PEP 8 Compliance:** All lines strictly adhere to the 79-character
  limit.

## Mutable vs. Immutable Comparison

- **State Mutation**: Immutable types return a new instance upon
  modification (no side effects), whereas mutable types alter the
  existing data in-place.
- **Underlying Storage**: Immutability is enforced at the language
  level by using `Tuple` for buckets and linked lists for chains.
  Mutable types use nested `List`s for efficient in-place updates.
- **Memory**: Immutable types rely on structural sharing to reuse
  unchanged data, avoiding full deep copies. Mutable types modify
  existing memory directly, which is faster for single operations.
- **Concurrency**: Immutable instances are inherently thread-safe
  without requiring locks. Mutable instances require external
  synchronization in concurrent environments.
- **Paradigm**: Immutable logic strictly uses recursion (functional),
  while mutable logic relies on loops (imperative).
  