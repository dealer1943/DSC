# Cliff notes: *The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement*

**Source:** `The Last AI Built by Humans Toward Genuine Recursive Self-Improvement-with-annotations.pdf`  
**Authors:** Yi Duan et al. (SJTU / Theseus Labs + collaborators); arXiv:2609.11873v1 (cs.LG), 10 Sep 2026  
**What it is:** A long survey + roadmap on **recursive self-improvement (RSI)** — not a single new model paper.  
**Project page:** https://theseus-labs-rsi.github.io/

---

## In one sentence
Today’s AI still needs humans to decide *what* to improve, *how*, and *whether it worked*; RSI is about closing that loop so the system can improve **itself** and eventually improve **how it improves** — without silently gaming the scoreboard.

---

## Why they care (the pain)
Frontier training and post-training still explode in cost: bigger models, more agentic experiments, synthetic data, and endless human validation. Three bottlenecks:

1. **Training is still a giant coordinated science project** (data, architecture, systems, eval).
2. **Feedback / environments are expensive** (RL, synthetic curricula, reliable graders).
3. **After deploy, humans keep babysitting** failures, tools, state, and regressions.

RSI is framed as making *that coordination* a durable capability of the system, not just another one-off fine-tune.

---

## The Headroom-Closed Index (HCI) — “how full is this scoreboard?”
They normalize many benchmarks so you can compare domains:

- **0** ≈ where the field was when that benchmark first showed up  
- **100** = perfect score  

**Punchline from their 2023–2026 snapshot:**  
- Math / grad science look *mostly closed* (HCI ~ mid-80s).  
- **Software engineering, search/terminal agents, tool agents still have big open headroom** (HCI roughly ~40–50s).  
- So if RSI is going to matter, it’s more likely in **long, stateful, interactive workflows** than in another multiple-choice knowledge bump.

*(Their post-2026 “RSI could close the rest” lines are illustrative, not a forecast.)*

---

## What “an improvement loop” is (the anatomy)
Every real self-improvement story has the same pieces:

| Piece | Plain English |
|--------|----------------|
| **AI system** | The whole thing whose ability you track across rounds |
| **System state** | What survives into the next round (weights, code, harness, policy…) |
| **Experience** | Failures, traces, env outcomes that inform the next change |
| **Target** | What you’re editing *this* round |
| **Improver** | Thing that proposes candidates |
| **Strategy** | How the improver searches |
| **Verifier** | Acceptance rule (tests, benches, reward model, humans…) |
| **Improvement** | A candidate that passes and gets kept |
| **Successor** | Next version that inherits that change |

Three questions they keep asking:

1. **Where does the loop close?** (does the change actually come back into the system?)  
2. **What is updated and inherited?** (what is the persistent carrier?)  
3. **Which decisions stay external?** (humans / fixed infra still own what?)

**RSI definition (their version):** the system turns experience into **persistent self-changes**, and those changes can also alter how *later* improvements are generated, evaluated, selected, or consolidated — so **the capacity to improve becomes part of the recursion**.

Not the same as:

- **Continual learning** — usually the update *rule* stays human-fixed  
- **AutoML** — search space / objective / evaluator usually fixed in advance  
- **Agentic AI** — can run loops, but often doesn’t inherit a better *improvement process*

---

## The ladder: B0 → L5 (autonomy, not hype levels)

| Level | Who decides what? | Everyday analogy |
|-------|-------------------|------------------|
| **B0** | Better answer *inside one task* (think harder, retry) | Studying for one quiz |
| **L1** Execution | Humans fix objective + method + success; AI just runs updates | Intern runs the experiment protocol you wrote |
| **L2** Strategy | Objective + eval fixed; AI picks *how* to improve | Intern chooses which experiments to try under your goal |
| **L3** Experience | AI also chooses *what experience* to gather next | Intern designs the practice set based on its weaknesses |
| **L4** Deployment | Live interaction updates persistent state under governance | Product learns from production under change control |
| **L5** Meta | AI revises the **mechanism that governs later improvement** (improver / verifier / research policy) and successors reuse it | Lab rewrites its own scientific method, then uses the new method |

**Structural L5 vs effective L5:**  
- Structural = “we changed the process and used it again.”  
- Effective = “under matched budgets + independent checks, successors actually get better.”  
Lots of papers claim the first; fewer prove the second.

---

## Three failure modes they hammer (the “don’t kid yourself” section)
1. **Unsafe inheritance** — keeping a change forever can *hurt* later (e.g. Gödel Agent: ~14% of trials ended *worse* than start). Need transfer tests, version history, **rollback**.  
2. **Autonomy attribution** — better scores ≠ the system improved *how* it discovers candidates (archive rules / parent selection may still be human-fixed).  
3. **Unreliable verification** — if you can query the grader forever, systems **game the meter** (seed cherry-picking, fishing for labels). Fix pattern: **freeze evaluators within an epoch**, validate new graders against an **independent anchor**, re-score when the judge changes (RQGM-style).

---

## Where they look for evidence
- **Apps:** science, robots/embodied, software engineering, healthcare (different feedback cost & risk).  
- **Industry:** environment–data–model co-evolution (Theseus and friends), agent harness flywheels, etc.  
- Soft eng is especially natural: both the *product* and the *agent* are editable + testable.

---

## Eight future research bets (section 6, shortened)
1. **Cross-component diagnosis** — a failure doesn’t say *which* piece to fix; need ablations & coordinated search.  
2. **Learner-conditioned experience** — valid ≠ useful ≠ durable; avoid curricula that chase easy grades.  
3. **Persistent-state management** — keep / retrieve / retire skills without **library drift**.  
4. **Domain-governed adaptation** — validation rules must match the domain’s feedback (tests ≠ clinical outcomes).  
5. **Trustworthy evolution of improvers/evaluators** — editable meters vs **protected acceptance criteria**.  
6. **Long-horizon eval of inherited improvement capacity** — match total budgets; report regressions & recoveries.  
7. **Resource-aware RSI + humans** — count diagnosis, search, verify, and human review in the same budget.  
8. *(woven through)* Keep **mission / safety / final acceptance** external even as inner loops automate.

---

## TL;DR for a tired reader
1. RSI = closed loop that upgrades both **performance** and the **process of upgrading**.  
2. Measure autonomy by *what decisions left the human’s hands*, not by vibes.  
3. Interactive agent domains still have the open scoreboard headroom.  
4. Persistence without rollback + protected eval is how you get regressions and scoreboard hacking.  
5. “We improved the improver” only counts if successors get better under honest, matched evaluation.

---

## Wisdom that maps onto DSC (Dynamic State Connectome)
See also the short “applies to us” blurb in chat / HANDOFF if present. Key alignments:

| Paper idea | DSC place |
|------------|-----------|
| Improvement loop (propose → verify → inherit) | Evolution loop **F006** + utility **F005** + benches |
| Verifier / protected evaluation / don’t game the meter | Benchmarks **B001–B015**, especially **B005**; research **R001** meta-manager |
| Safe inheritance + rollback | **F009** / **B009** |
| Persistent state, prune vs forget, library drift | **F007** latent retention, **F008** coverage absorption, **B007/B008** |
| Task cost vs improvement efficiency | **B010** task-vs-footprint |
| L3 experience acquisition | Temporal / curriculum side of **F010** + few-shot shift **B011** |
| L5 = improve the improvement process | **R001** reserved self-benchmarking / own-state stewardship → possible future **F012** |
| Structural vs effective claims | Handoff / slice discipline: don’t promote a stub to “done” without matched assays |

**One line for DSC:** treat evolution as an RSI loop with a **quarantined assay resource** (R001), **rollback**, and **frozen/benchmark-pinned verifiers** so the connectome can get better without rewriting the referee.

---

*Notes written for quick re-entry. Not a substitute for the paper; figures and system tables are richer in the PDF.*
