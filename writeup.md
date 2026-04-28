## Why these questions

The system is designed around three behavioral axes:

- Locus of Control → internal vs external agency  
- Contribution vs Entitlement → giving vs expecting  
- Radius of Concern → self vs others  

These dimensions were chosen to progressively move the user from
self-awareness to behavioral insight and meaning.

---

## Branching logic

The system does not rely on simple if-else branching.

Instead, it uses signal-based reasoning:

- Each answer emits a signal (e.g., axis1:internal)
- Signals accumulate across questions
- A dominant pattern is computed per axis
- Decisions are made based on this dominant behavior

This allows the system to model patterns rather than single responses.

Additionally:
- Early decisions split based on context (e.g., productive vs frustrating)
- Later decisions adapt reflections based on aggregated signals
- The flow progressively widens perspective: self → team → others

---

## Hallucination Guardrails

The system eliminates hallucination risk entirely by design:

- No LLM calls at runtime
- All outputs are predefined in a structured JSON tree
- User input is constrained to fixed options
- Decisions are deterministic and fully traceable

This ensures:
- zero hallucination
- consistent outputs
- explainable behavior

---

## Trade-offs

- Fixed options reduce nuance but ensure determinism
- Predefined reflections limit flexibility but improve reliability
- Designing the tree requires upfront effort but simplifies execution

---

## Improvements

- More granular signal weighting (not just counts)
- Dynamic summaries based on dominant axes
- Additional branching for edge behavioral patterns
- Optional hybrid mode with LLM refinement (with guardrails)