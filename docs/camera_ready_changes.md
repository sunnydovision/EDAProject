# Camera-Ready Response Plan

This note summarizes the reviewer comments, our author response, and the concrete edits made or planned for `docs/conference_IEEE.tex`.

## Reviewer #1

### R1.1 — Fairness of the agentic baseline

**Reviewer comment.** The free-form agentic baseline is converted into `(B, M, S, P)` tuples after generation, although it was not designed to emit that representation. This may artificially lower its SVR by mixing format mismatch with reasoning errors.

**Author response.** We agree partially. The baseline does not require fragile free-text parsing; it emits structured JSON. However, the reviewer is right that its native schema is different from the tuple interface used by the structured systems. Therefore, SVR for this baseline should be interpreted as validity under the shared evaluation contract, not as a pure measure of internal reasoning quality.

**Revision.**
- Revised §III.C to state that the agentic baseline has no native tuple interface.
- Replaced "parse outputs" with "normalize its structured JSON outputs into `(B, M, S, P)`".
- Revised §VII Limitations to say that, with schema-normalized agentic outputs, metric differences should be read as observations under the shared evaluation contract.
- We did not add a prompted structured-output agent because that would require a new experiment and is outside the camera-ready scope.

### R1.2 — Q-I Alignment and R-I Coherence

**Reviewer comment.** Q-I Alignment and R-I Coherence add limited discriminative value. Since the paper labeled them as control metrics, their role in the core framework was unclear.

**Author response.** We agree. These metrics should not be framed as causal controls, and they do not prove that retrieval or search bias is absent. They are better interpreted as auxiliary text-alignment diagnostics: they check whether the question or rationale text remains semantically close to the evaluated structured insight representation.

**Revision.**
- Reframed Group 5 as auxiliary text-alignment diagnostics.
- Changed `$T_i$` from "insight text" to "structured insight representation" in the Q-I formula description.
- Renamed the Cross-Dataset Analysis subsection from `Control Metrics` to `Text-Alignment Diagnostics`.
- Removed claims about retrieval bias and shared search implementation.
- Kept the metrics in the framework as descriptive checks, not primary discriminators or causal controls.

## Reviewer #5

### R5.1 — Limited novelty

**Reviewer comment.** The novelty is somewhat limited because most metrics are adapted from existing statistical tests, subgroup-discovery measures, or embedding-similarity metrics.

**Author response.** We agree with the characterization that the individual metric components are adapted rather than entirely new. Our intended contribution is the integration of these components into one reproducible diagnostic protocol for AutoEDA, together with a controlled case study comparing structured question guidance, statistical ablation, and free-form agentic analysis.

**Revision plan.**
We will address this by sharpening the framing in the Introduction: the contribution is the integrated diagnostic protocol and the controlled comparison, not a claim that each individual metric is novel. We do not plan to introduce an additional metric, because that would change the scope rather than clarify the contribution.

### R5.2 — No validation against human judgments

**Reviewer comment.** The paper argues for automatic diagnostics but does not validate the metrics against human judgments, so it is unclear whether higher scores correspond to better user-perceived insight quality.

**Author response.** We agree. The framework is intended as a diagnostic layer for structural and statistical failures, not as a full replacement for human evaluation. Human validation would require a separate user study or expert-rating study.

**Revision plan.**
We will add this as a limitation rather than overclaiming the automatic metrics. The intended wording should say that the diagnostics are complementary to human evaluation and that future work should correlate them with expert ratings or user-study outcomes. We will not add a new human study in camera-ready, since that would require new data collection.

### R5.3 — Why these nine metrics and whether they are independent

**Reviewer comment.** More discussion is needed on why these nine metrics were selected and whether they are independent.

**Author response.** We agree. The nine metrics were selected from a larger candidate pool to keep the evaluation focused on failures that matter for AutoEDA insight quality: grounded numeric correctness, structural validity, statistical strength, pattern/subspace exploration, and auxiliary text alignment. We deliberately did not foreground some available metrics, such as runtime, token cost, or several breakdown-measure association scores, because they either measure efficiency rather than insight quality or can distract from the paper's main diagnostic claims. The retained metrics are also not fully independent; for example, SVR affects which insights can be meaningfully tested, and Subspace Rate conditions uplift and SPR.

**Revision plan.**
We will add only a compact explanation in §IV. The paragraph should say that the nine metrics were chosen from the broader metric inventory as a minimal diagnostic set, while acknowledging the main dependencies among them. This should be kept short because the paper is already at the page limit.

### R5.4 — Typographical and formatting issues

**Reviewer comment.** The notation `(p ¡ 0.05)` should be corrected to `(p < 0.05)`, and Section IV should be titled "Evaluation Metrics".

**Author response.** We agree.

**Revision.**
We corrected the malformed `p < 0.05` notation by writing the threshold in math mode wherever it appears in the metric definitions, and renamed `\section{Evaluation Framework}` to `\section{Evaluation Metrics}`.

### R5.5 — Paper organization

**Reviewer comment.** Section IV contains only one subsection, and Section V is very short. Section V could be merged into Section VI to improve flow.

**Author response.** We agree. The experimental setup is short and reads more naturally as the first subsection of Results.

**Revision.**
We removed the standalone `\section{Experimental Setup}` and moved the same content into Results as `\subsection{Experimental Setup}`, before the overview subsection. No experimental content was removed; the change only reduces the number of top-level sections and makes the paper flow more naturally.

### R5.6 — Related work on automatic AutoEDA evaluation

**Reviewer comment.** The related work section should better cover previous studies that use automatic evaluation metrics for AutoEDA.

**Author response.** We agree in principle, but this change was skipped for the current camera-ready pass due to page constraints and project instruction to avoid expanding related work.

**Revision plan.**
We will leave this unchanged unless page budget becomes available. Expanding related work would be valuable, but in the current camera-ready version it competes directly with higher-priority reviewer fixes on agentic fairness, metric framing, and limitations.
