# Camera-Ready Changes — `conference_IEEE.tex`

## #1 — Fix `p < 0.05` notation (Reviewer #5 typo)
- Converted three in-text occurrences from plain text to math mode (equations already used `<` correctly).
- **§IV, Statistical Significance (line 137):** `at p < 0.05.` → `at $p < 0.05$.`
- **§IV, SPR definition (line 169):** `statistically significant (p < 0.05).` → `statistically significant ($p < 0.05$).`
- **§IV, SPR formula description (line 176):** `requires p < 0.05 for both` → `requires $p < 0.05$ for both`

## #2 — Rename §IV (Reviewer #5)
- **Section IV heading (line 98):** `\section{Evaluation Framework}` → `\section{Evaluation Metrics}`

## #3 — Merge §V into §VI (Reviewer #5)
- Deleted standalone `\section{Experimental Setup}`.
- Moved its text verbatim into Results as `\subsection{Experimental Setup}`, placed before `\subsection{Overview}`.
- Added `\label{sec:results}` to the Results section.
- No content lost; no in-text "Section V" references needed updating.
- Net effect: paper drops from 8 to 7 numbered sections; Results is now §V, with Experimental Setup as its first subsection.

---

# All Reviewer Comments — Plan & Status

Items #1–#3 above are applied (**DONE**); the rest are planned.

## Reviewer #1

| # | Comment | Our plan | Status |
|---|---|---|---|
| R1.1 | Potentially unfair agentic baseline — free-form outputs parsed post-hoc into `(B,M,S,P)`, likely penalizing SVR for format (not reasoning) | Add short text in **§III.C** + **§VII Limitations**: parsing is needed for a common protocol; some SVR loss is format mismatch; comparison still fair since all systems share the `(B,M,S,P)` contract. No new baseline experiment. | Planned |
| R1.2 | Q-I Alignment & R-I Coherence add limited value; why in the core 9? | Reframe (don't remove): add a paragraph at start of **§IV** — Groups 1–4 = diagnostic, Group 5 = control metrics ruling out retrieval bias when ISGEN is shared. | Planned |

## Reviewer #5

| # | Comment | Our plan | Status |
|---|---|---|---|
| R5.1 | Limited novelty — mostly adapted metrics | Reframe contribution in **Introduction**: novelty = integrated reproducible protocol (composition + controlled case study), components adapted by design. No new metrics. | Planned |
| R5.2 | No validation against human judgments | Expand **§VII Limitations**: no human-rater validation; metrics target structural/statistical failures humans miss; future work = correlate with expert/user ratings. No new user study. | Planned |
| R5.3 | Why these 9 metrics; are they independent? | Add "Metric selection" paragraph at start of **§IV**: selection criteria per group + note non-independence (SVR gates significance; Subspace Rate conditions SPR/Uplift). | Planned |
| R5.4a | Typo `(p ¡ 0.05)` → `(p < 0.05)` | Convert 3 in-text occurrences to math mode `$p < 0.05$` (§IV). | **DONE (#1)** |
| R5.4b | Rename §IV to "Evaluation Metrics" | `\section{Evaluation Framework}` → `\section{Evaluation Metrics}`. | **DONE (#2)** |
| R5.5 | §IV has one subsection; §V very short — merge §V into §VI | Move Experimental Setup into Results as first subsection. | **DONE (#3)** |
| R5.6 | Strengthen related work on automatic AutoEDA evaluation | **Skipped** per instruction ("ignore adding related work"). | Won't do |
