# Current research baseline: v28

Two completed changes are already in the main version lineage:

- **KING_ESCAPE_TAIL_FIX=1**, shipped in v25: prevents a sprint from treating
  the current tail as already vacated. See `../notes/robustness.md`.
- **PEARL_ROUTE=2**, shipped in v26: route-based food value on unknown maps
  only. The all-map mode regressed several tuned ranked maps. The main journal
  records 68.1% on holdout and blind real-opponent performance improving from
  0/20 to 6/20. See `../notes/pearl-route.md`.

The current sandbox is an immutable-v28 copy with one **unvalidated,
default-off** experiment:

```text
-DUNK_BLOCKED_FOOD=1
```

It permits the existing clean-probe exploration when a nearby visible pearl
requires a long portal-free detour around observed walls. It does not change
known maps, portal destinations, probe safety, or the live bot. Do not enable
it for submission until its confirmation/regression tests pass.

The former v24 route experiment is preserved in
`../archive/pearl-route-v24-20260929/`; the v15 and symmetry experiments are
also archived. All new work stays inside `codex-battlecode/`.
