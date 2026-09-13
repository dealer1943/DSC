Part 1: DSC MVP Blueprint for Development Team
This section is designed to be handed to your developers. It defines the MVP scope, the core components, and the theoretical guardrails that prevent shortcuts which would create technical debt later.

1.1 MVP Objective
Build a working Dynamic State Connectome (DSC) that demonstrates three core capabilities:

State emergence: A population of undifferentiated "stem" state cells self-organizes into distinct functional types.

Evolutionary dynamics: The population undergoes selection, reproduction, and mutation over generations.

Pruning and absorption: Low-utility states are removed, and their function is absorbed by surviving neighbors.

MVP Success Criteria: The DSC can solve a simple, reproducible task (e.g., a temporal pattern-matching problem) while maintaining a compact state footprint. The system must demonstrate that pruning reduces the number of active states without catastrophic loss of task performance.

1.2 Core Architecture
The DSC is a population of State Cells operating on a Substrate Graph.

Substrate Graph (The "Hardware")
MVP Requirement: Start with a synthetic graph, not the full zebrafish connectome. Recommended initial choices: Erdős–Rényi (random), Watts–Strogatz (small-world), or Barabási–Albert (scale-free).

Rationale: This isolates the mechanism from the biology. You are testing whether the evolutionary loop works, not whether the zebrafish topology is necessary. This is faster to iterate, easier to debug, and provides a clean baseline for later comparison against biological connectomes.

Guardrail: The substrate graph must be sparse (connectivity < 10%) and directed. This reflects biological reality and is essential for the sparsity metrics in Part 2.

State Cell (The "Software")
Each state cell is an independent computational unit. Its architecture must be modular to allow type emergence.

text
StateCell {
    id: UUID
    type: ENUM { STEM, ATTRACTOR, LATENT, MODULATORY, MODULAR, METASTABLE }
    parameters: Dict[str, float]  // Type-specific weights, thresholds, time constants
    utility: float  // Exponential moving average of contribution to task objective
    age: int
    connections: List[UUID]  // Other state cells this cell communicates with
    differentiation: float  // 0.0 = fully stem (plastic), 1.0 = fully committed to type
}
Type Gene: The type field is mutable. A cell can change type during reproduction or mutation.

Stem Cells: All cells initialize as STEM. A stem cell's behavior is a learned mixture of all type behaviors, with a gating network that weights each type's contribution. This is the key to emergent type selection.

Differentiation: As a cell's utility stabilizes, differentiation increases, committing it to its current type. If utility drops, differentiation decreases, allowing the cell to revert to a stem-like state and re-differentiate.

1.3 The Evolution Loop
The loop runs every N steps (e.g., N = 100 task iterations).

Step 1: Evaluation
Compute utility for every active state cell.

text
U(cell) = w1 * task_performance + w2 * coverage_bonus + w3 * novelty_bonus - w4 * compute_cost
Task Performance: Marginal contribution of this cell to the task objective (e.g., prediction accuracy). Use counterfactual utility: measure performance drop when the cell is masked.

Coverage: Fraction of the input space where this cell is the dominant responder.

Novelty: Inverse of the maximum correlation between this cell's activation pattern and any other cell's pattern. Rewards cells that handle unique inputs.

Compute Cost: Memory footprint and active synaptic operations of this cell.

Step 2: Selection and Pruning
Prune: Remove cells with utility < threshold for M consecutive evaluation cycles (e.g., M = 3).

Absorb: For each pruned cell, redistribute its input coverage. For every input pattern the pruned cell handled, find the surviving cell with the highest response. Increase that surviving cell's coverage_bonus and widen its attractor basin (if applicable) to include the pruned cell's inputs.

Latent Retention (Guardrail): Do not delete the pruned cell's parameters. Move them to a dormant pool. This allows for reactivation if the task changes, preventing catastrophic forgetting.

Step 3: Reproduction and Mutation
Clone: The top K cells by utility are cloned.

Mutate Parameters: Each clone's parameters are perturbed by Gaussian noise.

Mutate Type: With low probability p_type, a clone changes its type gene (e.g., ATTRACTOR → LATENT).

Hybridize: With low probability p_hybrid, two high-utility cells of different types produce a child whose type is a mixture of the parents' types.

Step 4: Stability Guardrails
After each evolution cycle, run these checks. If any fail, rollback the cycle.

Reachability: Verify all remaining states are reachable from the base state.

Interference: Compute pairwise correlation of activation patterns. If any pair has correlation > 0.8, merge them or prune one.

Transition Collapse: Verify no state transition probability has collapsed to 0 or 1.

1.4 MVP Development Roadmap
Phase	Deliverable	Key Guardrail
1. Substrate	Synthetic graph generator with configurable topology.	Must support sparse, directed graphs.
2. State Cell	Stem cell with gated mixture-of-types behavior.	Type gating must be differentiable.
3. Evolution Loop	Working evaluation, selection, and reproduction.	Utility function must be computationally tractable.
4. Pruning & Absorption	Pruning with latent retention and coverage redistribution.	Rollback mechanism must be tested.
5. Task Integration	Simple temporal task (e.g., sequence prediction).	Task must have a clear, measurable objective.
1.5 Theoretical Guardrails (The "Why" for Devs)
Do not hardcode state types. The entire point is emergence. If a developer "optimizes" by pre-assigning types, they destroy the experiment.

Do not skip the substrate graph. The graph is not a detail. It shapes the dynamics. Starting with a fully connected graph will cause degenerate behavior (all states become the same).

Do not use a single utility metric. Task performance alone leads to degenerate solutions (one state does everything). Coverage and novelty bonuses are essential for diversity.

Do not delete pruned states. Latent retention is the mechanism for adaptation. Deleting them makes the system brittle.

📚 Part 2: Neural Benchmarking Theory and AI Benchmarks
This section provides the academic grounding for evaluating your DSC. It defines what "good" looks like in this field and which established benchmarks you can use as reference points.

2.1 The Theory of Neural Benchmarking
Benchmarking a connectome-based model is fundamentally different from benchmarking a standard AI model. The goal is not just task accuracy; it is biological fidelity and computational efficiency.

The Three Pillars of Neural Benchmarking
Task Correctness: Does the model solve the task? This is the baseline. Metrics: accuracy, F1, MSE, or task-specific rewards.

Computational Complexity: How expensive is the model to run? This is critical for neuromorphic and biological models. The NeuroBench framework formalizes this with metrics including Footprint (memory in bytes), Connection Sparsity (fraction of zero weights), Activation Sparsity (fraction of inactive neurons), and Synaptic Operations (effective MACs/ACs). Your DSC must report these metrics to be comparable to other spiking and neuromorphic models.

Biological Alignment: Does the model's internal representation match biological data? This is the gold standard. The Brain-Score platform is the canonical example: it evaluates models on their alignment to neural recordings and behavioral measurements in primate vision across 50+ benchmarks. For connectome models, alignment is assessed by comparing model activations to calcium imaging or electrophysiology data from the same species.

Key Academic Standards for Connectome Models
Null Models: Any claim of biological significance must be tested against a null model. For connectome-based models, this means generating rewired connectomes that preserve degree distribution but randomize topology. Your DSC's performance must be compared to its own performance on a rewired substrate.

k-Fold Cross-Validation: For any model with stochastic components, use k-fold CV to prevent overfitting. The connectome manipulation framework (BlueBrain) provides this semi-automatically. This is essential for your evolution loop, which has many hyperparameters.

Spatiotemporal Similarity: When comparing to biological data, you must evaluate both spatial similarity (which regions are active) and temporal similarity (when they are active). Metrics like Pearson's r and MAE are used, along with spatial autocorrelation-preserving null models to assess significance.

Reproducibility: Your benchmark must be reproducible. Use a fixed random seed, report all hyperparameters, and release the code. The NeuroBench framework provides a harness library for this purpose.

2.2 AI Benchmarks for Connectome-Inspired Models
There is no single benchmark called "DSC Benchmark." However, several established benchmarks are directly relevant to evaluating a model like yours.

Benchmark	What It Evaluates	Relevance to DSC
NeuroBench	Spiking/neuromorphic algorithms and systems. Metrics: Footprint, Sparsity, Synaptic Ops.	Directly applicable. Use this to report the computational cost of your DSC. It is the standard for neuromorphic models.
Brain-Score	Neural and behavioral alignment of ANNs to primate vision.	Adaptable. If you later map your DSC states to biological brain regions, you can use Brain-Score's methodology to assess alignment.
Mouse vs. AI	Neural alignment and robustness in a visually-guided foraging task.	Highly relevant. This benchmark tests models in an active, behaviorally relevant context—exactly the regime your DSC is designed for. It evaluates alignment to mouse visual cortex.
Neural Latents Benchmark (NLB)	Latent variable models of neural population activity. Metrics: co-smoothing, few-shot prediction.	Directly relevant to your state discovery layer. If your DSC discovers latent states, you can evaluate them using NLB's metrics on standard neural datasets.
ConnectomeBench2	Automated proofreading of connectomic reconstructions.	Context only. This is for evaluating the quality of the connectome data itself, not models.
BrainGB	GNNs on brain network analysis tasks.	Relevant if you use GNNs as your state cell architecture. It provides standardized pipelines and datasets.
2.3 Recommended Diagnostic Protocol for Your DSC
Task Benchmark: Choose a standard task with a clear objective (e.g., a temporal sequence prediction from the Computation-through-Dynamics Benchmark). Report accuracy.

Complexity Benchmark: Use the NeuroBench harness to report Footprint, Connection Sparsity, Activation Sparsity, and Synaptic Operations. Compare to a baseline SNN with the same number of neurons.

Ablation Study: Run your DSC with and without each core component (evolution loop, pruning, absorption, type mutation). Report the delta in task performance and footprint.

Null Model Comparison: Run your DSC on the real substrate graph and on a rewired substrate graph (degree-preserving randomization). Report the difference in all metrics.

Neural Alignment (Optional, Advanced): If you have access to neural data (e.g., from the Neural Latents Benchmark), map your DSC states to the latent variables and report co-smoothing performance.

This protocol ensures your MVP is not just "working"—it is diagnostically sound and comparable to the standards of the field.

💎 Summary
Your MVP blueprint is the mechanism. The benchmarking docket is the measurement. Build the mechanism on a synthetic substrate, measure it with NeuroBench and task-specific metrics, and validate it against null models. Once it works, you can swap in the zebrafish connectome as your validation substrate and compare it to the fly connectome. The path is clear: build, measure, validate, compare.