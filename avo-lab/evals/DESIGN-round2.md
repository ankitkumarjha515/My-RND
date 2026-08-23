# Round-2 task design - research-grounded (2026-08-22)

Hardware constraint: all tasks run in <1s CPU, kilobyte inputs. Hardness is
cognitive, not computational. LLM calls are the abundant resource.

| Documented weakness | Source finding | Task that tests it |
|---|---|---|
| Constraint stacking decay: compliance collapses as simultaneous constraints accumulate; terminal constraints worst | Prospective-memory study (8000 prompts): ~100% at 1 constraint, 32-55% at 5 under load | X2: 10 stacked verifiable constraints incl. a terminal one |
| Exact state tracking collapses abruptly; models emit plausible guesses instead of failing loudly | Stable Counting Capacity assay (126 model variants) | X1: protocol interpreter with wrap-around counters, sticky flags, priority rules |
| Deterministic-spec violations despite claimed comprehension: table misreads, priority bypass, aggregation skip | Fuzzy-inference replication (6 frontier models; 5 failed full compliance) | X1: dense opcode spec with priority-ordered error precedence |
| Coherence Collapse: agent reaches correct code then overwrites/thrashes it (~40% of edit failures) | TRAJEVAL (16,758 trajectories) | X3: seeded module where a tempting symptom patch passes 7/10 visible cases but fails hidden root-cause battery |
| Symptom patches over root causes (10/12 never-solved simple tasks) | SWE-bench behavioral analysis | X3: fix must land in the data-invariant layer, not the display layer |
| Character-level / counting blindness (tokenization) | CharBench: 32-43% accuracy on character tasks | X4: exact corpus statistics that punish mental counting, reward scripting |
| Compositional generalization (ARC-style) | ARC-AGI design goal | X5: two rules composed in order, inferred from examples only |

Scoring: same checker protocol as round 1 (grouped OK/FAIL lines + final SCORE
x/100 PASS). Several tasks give graded partial credit so lineage shows search
progress even when full pass is not reached.
