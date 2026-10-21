# Reading List

Everything students are asked to read, in one place. Two categories per week: a
**textbook section** (the load-bearing conceptual reading) and one or two
**papers** (the discussion material).

Papers are open access or available through the university library. Links are to
publisher DOIs and arXiv abstract pages rather than to PDF mirrors, so they keep
working.

---

## How the reading is used

The Session A mini-lecture **assumes the textbook reading was done.** It clarifies,
contextualizes, and corrects; it does not re-present. See
[`teaching-guide.md`](teaching-guide.md) §1 for why this matters.

Papers are paired deliberately. In most weeks one paper is the **classical primary
source** — the actual 1962 DPLL paper, the actual 1968 A* paper — and one is a
**modern counterpart** attempting the same task with a language model. Reading them
back to back in one sitting is the point. Students should notice that the older
papers state their theorems and the newer ones state their benchmarks.

Load per week: roughly 25–40 pages of textbook, one or two papers. Where a paper is
long, the assigned sections are given and they are not optional-in-disguise — read
exactly those.

---

## Textbooks

**Russell, Stuart J., and Peter Norvig.** *Artificial Intelligence: A Modern
Approach.* Pearson. Cited below as **R&N**. Section numbers follow the **4th
edition** (2021); a 3rd-edition mapping is at the end of this file.

**Luger, George F.** *Artificial Intelligence: Structures and Strategies for
Complex Problem Solving.* Addison-Wesley. Cited as **Luger**; numbers follow the
5th edition (2005).

Neither book is required to be purchased new. R&N is the primary; Luger is used for
the state-space-search framing in weeks 3–4 and for the evolutionary/swarm material
in weeks 10–11, which R&N covers only briefly.

---

## Week by week

### Week 1 — Intelligence and history
- **R&N ch. 1** · **Luger ch. 1**
- Turing, A. M. (1950). *Computing Machinery and Intelligence.* **Mind** 59(236):
  433–460. [DOI:10.1093/mind/LIX.236.433](https://doi.org/10.1093/mind/LIX.236.433)
  — **read §1–§6 only.** §6 is the objections section and is where the discussion
  goes.

### Week 2 — Agents, PEAS, environments
- **R&N ch. 2**
- Yao, S., et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language
  Models.* [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) — ICLR 2023.

### Week 3 — Problem formulation and uninformed search
- **R&N §3.1–3.4** · **Luger ch. 3**
- Newell, A., and H. A. Simon (1976). *Computer Science as Empirical Inquiry:
  Symbols and Search.* **Communications of the ACM** 19(3):113–126.
  [DOI:10.1145/360018.360022](https://doi.org/10.1145/360018.360022) —
  their ACM Turing Award lecture. Read §1 and the "Heuristic Search" section.
  (The ACM Digital Library page sometimes blocks direct links; searching the title
  reaches a free copy.)

### Week 4 — Heuristics and A*
- **R&N §3.5–3.6**
- Hart, P. E., N. J. Nilsson, and B. Raphael (1968). *A Formal Basis for the
  Heuristic Determination of Minimum Cost Paths.* **IEEE Transactions on Systems
  Science and Cybernetics** 4(2):100–107.
  [DOI:10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136) — the
  A* paper. Short. Read the admissibility theorem carefully.
- Lehnert, L., et al. (2024). *Beyond A\*: Better Planning with Transformers via
  Search Dynamics Bootstrapping.*
  [arXiv:2402.14083](https://arxiv.org/abs/2402.14083) — Searchformer.

### Week 5 — Adversarial search and games
- **R&N §5.1–5.4** · **Luger ch. 4**
- Shannon, C. E. (1950). *Programming a Computer for Playing Chess.*
  **Philosophical Magazine** 41(314):256–275.
  [text copy](https://www.pi.infn.it/~carosi/chess/shannon.txt) — the origin of
  minimax-with-evaluation-function as an engineering proposal.
- Ruoss, A., et al. (2024). *Amortized Planning with Large-Scale Transformers: A
  Case Study on Chess.* [arXiv:2402.04494](https://arxiv.org/abs/2402.04494) —
  grandmaster-level play *without* search. The direct answer to Shannon.

### Week 6 — Constraint satisfaction
- **R&N §6.1–6.4**
- Mackworth, A. K. (1977). *Consistency in Networks of Relations.* **Artificial
  Intelligence** 8(1):99–118.
  [DOI:10.1016/0004-3702(77)90007-8](https://doi.org/10.1016/0004-3702(77)90007-8)
  — AC-3's origin. Read §1–3.
- Pan, L., et al. (2023). *Logic-LM: Empowering Large Language Models with Symbolic
  Solvers for Faithful Logical Reasoning.*
  [arXiv:2305.12295](https://arxiv.org/abs/2305.12295) — EMNLP 2023 Findings.
  **First appearance of the course's central architecture.**

### Week 7 — Propositional logic and SAT
- **R&N §7.1–7.6** · **Luger ch. 2**
- Davis, M., G. Logemann, and D. Loveland (1962). *A Machine Program for
  Theorem-Proving.* **Communications of the ACM** 5(7):394–397.
  [DOI:10.1145/368273.368557](https://doi.org/10.1145/368273.368557) — DPLL. Two
  and a half pages, and still the backbone of every modern SAT solver.
- Stechly, K., K. Valmeekam, and S. Kambhampati (2024). *Chain of Thoughtlessness?
  An Analysis of CoT in Planning.*
  [arXiv:2405.04776](https://arxiv.org/abs/2405.04776)

### Week 8 — First-order logic, unification, Prolog
- **R&N ch. 8, §9.1–9.4** · **Luger ch. 2**
- Robinson, J. A. (1965). *A Machine-Oriented Logic Based on the Resolution
  Principle.* **Journal of the ACM** 12(1):23–41.
  [DOI:10.1145/321250.321253](https://doi.org/10.1145/321250.321253) — read §1–2
  and the unification section. Dense; the assigned sections are enough.
- Olausson, T. X., et al. (2023). *LINC: A Neurosymbolic Approach for Logical
  Reasoning by Combining Language Models with First-Order Logic Provers.*
  [arXiv:2310.15164](https://arxiv.org/abs/2310.15164) — EMNLP 2023. The
  architecture again, second research group.

### Week 9 — Knowledge representation and planning
- **R&N §10.1–10.3, §11.1–11.2**
- Fikes, R. E., and N. J. Nilsson (1971). *STRIPS: A New Approach to the
  Application of Theorem Proving to Problem Solving.* **Artificial Intelligence**
  2(3–4):189–208.
  [DOI:10.1016/0004-3702(71)90010-5](https://doi.org/10.1016/0004-3702(71)90010-5)
- Kambhampati, S., et al. (2024). *LLMs Can't Plan, But Can Help Planning in
  LLM-Modulo Frameworks.*
  [arXiv:2402.01817](https://arxiv.org/abs/2402.01817) — ICML 2024. The
  architecture a third time, stated as a general framework.
- Valmeekam, K., et al. (2023). *PlanBench: An Extensible Benchmark for Evaluating
  Large Language Models on Planning and Reasoning about Change.*
  [arXiv:2206.10498](https://arxiv.org/abs/2206.10498) — NeurIPS 2023 Datasets &
  Benchmarks. Skim for the benchmark design; that is what students are imitating.

### Week 10 — Local search and genetic algorithms
- **R&N §4.1** · **Luger ch. 12**
- Holland, J. H. (1975/1992). *Adaptation in Natural and Artificial Systems.* MIT
  Press. Read ch. 1 and the schema-theorem section.
- Kirkpatrick, S., C. D. Gelatt, and M. P. Vecchi (1983). *Optimization by
  Simulated Annealing.* **Science** 220(4598):671–680.
  [DOI:10.1126/science.220.4598.671](https://doi.org/10.1126/science.220.4598.671)

### Week 11 — Swarm intelligence
- **Luger ch. 12** · **R&N §4.1** (review; R&N does not cover swarm methods)
- Dorigo, M., V. Maniezzo, and A. Colorni (1996). *Ant System: Optimization by a
  Colony of Cooperating Agents.* **IEEE Transactions on Systems, Man, and
  Cybernetics, Part B** 26(1):29–41.
  [DOI:10.1109/3477.484436](https://doi.org/10.1109/3477.484436)
- Romera-Paredes, B., et al. (2024). *Mathematical discoveries from program search
  with large language models.* **Nature** 625:468–475.
  [DOI:10.1038/s41586-023-06924-6](https://doi.org/10.1038/s41586-023-06924-6) —
  FunSearch. **Open access, CC BY 4.0**; a free mirror is at
  [PMC10794145](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10794145/).

### Week 12 — Probability, Bayes, Naive Bayes
- **R&N ch. 12, §20.2** · **Luger ch. 5**
- Domingos, P., and M. Pazzani (1997). *On the Optimality of the Simple Bayesian
  Classifier under Zero-One Loss.* **Machine Learning** 29:103–130.
  [DOI:10.1023/A:1007413511361](https://doi.org/10.1023/A:1007413511361) — why a
  false assumption still classifies well. The single most useful paper in the
  course for thinking about model assumptions.
- Kadavath, S., et al. (2022). *Language Models (Mostly) Know What They Know.*
  [arXiv:2207.05221](https://arxiv.org/abs/2207.05221) — read the calibration
  sections.

### Week 13 — Markov chains and hidden Markov models
- **R&N §14.1–14.3**
- Rabiner, L. R. (1989). *A Tutorial on Hidden Markov Models and Selected
  Applications in Speech Recognition.* **Proceedings of the IEEE** 77(2):257–286.
  [DOI:10.1109/5.18626](https://doi.org/10.1109/5.18626) — read §I–III. Long but
  genuinely the best exposition of the forward algorithm and Viterbi ever written.
- Vaswani, A., et al. (2017). *Attention Is All You Need.*
  [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) — read **§1–3.2 only.** The
  bridge paper: read it as an answer to the question "what would you do if you
  dropped the Markov assumption entirely?"

### Week 14 — Neural networks, ethics and safety
- **R&N §21.1–21.2, ch. 27**
- Rosenblatt, F. (1958). *The Perceptron: A Probabilistic Model for Information
  Storage and Organization in the Brain.* **Psychological Review** 65(6):386–408.
  [DOI:10.1037/h0042519](https://doi.org/10.1037/h0042519)
- Rumelhart, D. E., G. E. Hinton, and R. J. Williams (1986). *Learning
  Representations by Back-Propagating Errors.* **Nature** 323:533–536.
  [DOI:10.1038/323533a0](https://doi.org/10.1038/323533a0)
- Bender, E. M., T. Gebru, A. McMillan-Major, and S. Shmitchell (2021). *On the
  Dangers of Stochastic Parrots: Can Language Models Be Too Big?* FAccT '21,
  610–623. [DOI:10.1145/3442188.3445922](https://doi.org/10.1145/3442188.3445922)

---

## Optional further reading

Not assigned. Point individual students here when they ask "what should I read
next" — which several will, usually around week 9.

| Topic | Suggestion |
|---|---|
| Search, deeper | Korf (1985), *Depth-First Iterative-Deepening.* [DOI:10.1016/0004-3702(85)90084-0](https://doi.org/10.1016/0004-3702(85)90084-0) |
| Heuristics from first principles | Pearl (1984), *Heuristics.* Addison-Wesley. |
| Games | Campbell, Hoane & Hsu (2002), *Deep Blue.* [DOI:10.1016/S0004-3702(01)00129-1](https://doi.org/10.1016/S0004-3702(01)00129-1) |
| Games, learned | Silver et al. (2017), *Mastering Chess and Shogi by Self-Play* (AlphaZero). [arXiv:1712.01815](https://arxiv.org/abs/1712.01815) |
| SAT in practice | Marques-Silva & Sakallah (1999), *GRASP* (conflict-driven clause learning). [DOI:10.1109/12.769433](https://doi.org/10.1109/12.769433) |
| Planning heuristics | Hoffmann & Nebel (2001), *The FF Planning System.* [arXiv:1106.0675](https://arxiv.org/abs/1106.0675) |
| Planning + LLMs | Liu et al. (2023), *LLM+P.* [arXiv:2304.11477](https://arxiv.org/abs/2304.11477) |
| LLM planning, skeptical | Valmeekam et al. (2023), *On the Planning Abilities of LLMs.* [arXiv:2302.06706](https://arxiv.org/abs/2302.06706) |
| No Free Lunch | Wolpert & Macready (1997). [DOI:10.1109/4235.585893](https://doi.org/10.1109/4235.585893) |
| Calibration of modern nets | Guo et al. (2017), *On Calibration of Modern Neural Networks.* [arXiv:1706.04599](https://arxiv.org/abs/1706.04599) |
| Emergence, skeptical | Schaeffer, Miranda & Koyejo (2023), *Are Emergent Abilities of LLMs a Mirage?* [arXiv:2304.15004](https://arxiv.org/abs/2304.15004) |

---

## R&N 3rd-edition mapping

The 4th edition reorganized Parts III and IV substantially — knowledge
representation and planning swapped position, and neural networks were promoted
from a section of the learning chapter to a chapter of their own. If your students
have the 3rd edition:

| Wk | 4th ed. | 3rd ed. | Note |
|----|---------|---------|------|
| 1 | ch. 1 | ch. 1 | |
| 2 | ch. 2 | ch. 2 | |
| 3 | §3.1–3.4 | §3.1–3.4 | |
| 4 | §3.5–3.6 | §3.5–3.6 | |
| 5 | §5.1–5.4 | §5.1–5.4 | |
| 6 | §6.1–6.4 | §6.1–6.4 | |
| 7 | ch. 7 | ch. 7 | |
| 8 | ch. 8, §9.1–9.4 | ch. 8, §9.1–9.4 | |
| 9 | §10.1–10.3 (KR), §11.1–11.2 (planning) | §12.1–12.3 (KR), §10.1–10.2 (planning) | **swapped** |
| 10 | §4.1 | §4.1 | |
| 11 | — (Luger only) | — | |
| 12 | ch. 12, §20.2 | ch. 13, §20.2 | uncertainty chapter renumbered |
| 13 | §14.1–14.3 | §15.1–15.3 | |
| 14 | §21.1–21.2, ch. 27 | **§18.7**, ch. 26 | 3rd ed. has no deep-learning chapter; NNs are a section of *Learning from Examples*. Ch. 26 is *Philosophical Foundations* and is thinner on safety — supplement with the Bender paper, which carries that discussion anyway. |

Verify section numbers against the copy in hand before publishing the syllabus;
printings vary and this table is a starting point, not a guarantee.
