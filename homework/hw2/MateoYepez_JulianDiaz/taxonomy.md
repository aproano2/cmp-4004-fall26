# Error taxonomy

| Category | Count | Share of B flagged cases | Production detectability |
| --- | --- | --- | --- |
| Malformed syntax | 0 | 0.0% | Yes |
| Valid syntax, over-constrained | 1 | 5.0% | No: reference comparison required |
| Valid syntax, under-constrained | 11 | 55.0% | No: reference comparison required |
| Valid model of the wrong problem | 8 | 40.0% | No: reference comparison required |
| Quantifier scope / arity errors | 0 | 0.0% | Not applicable |
| Solver timeout | 0 | 0.0% | Yes |

Each case is one instance/repetition. The table includes all status failures and semantic model mismatches even when SAT/UNSAT is correct. `results/errors.csv` contains every flagged attempt in B and B′ with raw output and exhaustive evidence. `results/attempts.csv` contains all model attempts. Infrastructure failures are separate from reasoning failures.

Over-constrained means the generated solution set is a strict subset of the reference set; under-constrained means a strict superset. Incomparable sets identify a different problem. The analysis enumerates all assignments and saves lost/added counterexamples. Missing/extra clauses are supporting evidence only, because redundant clauses need not change semantics. Linguistic causes (reversed implication, dropped premise, incorrect negation) require manual review of the original prompt and are not inferred from a status mismatch. No quantifiers or predicate arities exist in this propositional output language; that category is not applicable. Invalid variable IDs are schema errors.

A legitimate UNSAT answer does not establish over-constraint or an error. Contrary to a literal reading of the assignment's generic table, UNSAT is observable but its incorrectness is not. Neither solution multiplicity nor a generated SAT witness establishes faithfulness to the Spanish prompt.

## B versus C detectability

| Arm | Failed attempts | Observable failures | Detection rate |
| --- | --- | --- | --- |
| B | 11 | 0 | 0 |
| C | 5 | 0 | 0 |

Detection rate uses incorrect plus no-answer attempts as its denominator; N/A means no failures or no observations. C detects malformed or absent responses but does not claim to verify free-text reasoning contradictions. Well-formed incorrect SAT/UNSAT answers are silent. B additionally checks variable references, solver errors, deadlines and generated-model witnesses. Semantic comparisons are privileged post-hoc analysis, never production detectors.

## Refinement

Only parse/schema/solver errors and solver timeouts trigger up to three repairs. API failures and LLM timeouts stop as infrastructure failures. A valid SAT or UNSAT result stops immediately. Therefore an equivalent UNSAT model is not pressured toward SAT, while semantic errors may survive silently. Observable convergence and ground-truth correctness are stored separately.

Paired improvement (percentage points): 0.

| Outcome | Count |
| --- | --- |
| initial_success | 9 |
| silent_incorrect | 11 |

## Verbatim examples

There are 20 flagged B cases. 5 real output examples are available below. No outputs are synthesized to meet the requested five-example target.

### Example 1: flagged B case

Problem ID: sat_01  
Difficulty: easy  
Arm: B  
Iteration: 0  

Original LLM output:

    {
    "clauses": [
        [1, 2],
        [-3, -4],
        [-1, -3],
        [3, -4]
    ]
    }

Solver result: SAT  
Ground truth: SAT  
Error category: Valid model of the wrong problem  
Detectable without ground truth: False  
Explanation: Assistant post-hoc clause review: the premise Arte → Robótica requires [-1,3], but the output contains [-1,-3], reversing the consequent polarity. The mandatory Danza clause [4] is absent. Clause [3,-4] adds Danza → Robótica, which is not a supplied premise. These are explicit incorrect-negation, dropped-premise and hallucinated-constraint findings, supported by the original Spanish text.  
Refinement result: initial_success

### Example 2: flagged B case

Problem ID: sat_02  
Difficulty: easy  
Arm: B  
Iteration: 0  

Original LLM output:

    {
    "clauses":[
        [-1,-2],
        [1,3],
        [-1,2],
        [-2,3],
        [-3,4],
        [3,-4]
    ]}

Solver result: SAT  
Ground truth: UNSAT  
Error category: Valid syntax, under-constrained  
Detectable without ground truth: False  
Explanation: Assistant post-hoc clause review: at least one of cámara/trípode requires [1,2], whereas [-1,-2] expresses at most one. The required exclusion of micrófono and lámpara is [-3,-4], not generated [3,-4]. Exhaustive analysis finds two generated solutions and no reference solution. The category under-constrained follows from solution sets, not merely the wrong SAT answer.  
Refinement result: silent_incorrect

### Example 3: flagged B case

Problem ID: sat_03  
Difficulty: easy  
Arm: B  
Iteration: 0  

Original LLM output:

    {
    "clauses": [
    [-1],
    [1, -2],
    [-1, 2, 3],
    [-1, 2, -3],
    [-1, -2, -3],
    [-1, -2, -4],
    [1]
    ] 
    }

Solver result: UNSAT  
Ground truth: SAT  
Error category: Valid syntax, over-constrained  
Detectable without ground truth: False  
Explanation: Assistant post-hoc clause review: the output contains both [-1] and [1], directly forcing carteles false and true. The text requires carteles, corresponding to [1], and does not authorize [-1]. This explicit contradictory, hallucinated negative unit clause explains why the generated model is UNSAT despite a satisfiable reference.  
Refinement result: silent_incorrect

### Example 4: flagged B case

Problem ID: sat_04  
Difficulty: easy  
Arm: B  
Iteration: 0  

Original LLM output:

    {
    "clauses":[
        [-1],
        [1, 2],
        [-2, 3],
        [-3, -4],
        [-4]
    ]}

Solver result: SAT  
Ground truth: UNSAT  
Error category: Valid syntax, under-constrained  
Detectable without ground truth: False  
Explanation: Assistant post-hoc clause review: the text requires carteles ([1]), but the output starts with [-1]. The exclusion of maquetas and folletos requires [-2,-3], while generated [-2,3] requires folletos when maquetas is chosen. These are identifiable polarity errors; the solution-set test establishes the resulting semantic category.  
Refinement result: silent_incorrect

### Example 5: flagged B case

Problem ID: sat_05  
Difficulty: easy  
Arm: B  
Iteration: 0  

Original LLM output:

    {
    "clauses":[
        [-1, -3],
        [1],
        [1, -2],
        [-2, -4]
    ]}

Solver result: SAT  
Ground truth: SAT  
Error category: Valid syntax, under-constrained  
Detectable without ground truth: False  
Explanation: Assistant post-hoc clause review: the premise mapa → brújula requires [-1,2], whereas [1,-2] encodes brújula → mapa, a reversed implication. The generated model allows mapa=true and brújula=false, which violates the original premise. Both formulas are SAT, so status accuracy hides this under-constrained translation.  
Refinement result: initial_success

