"""
Question Quality (QuGen) metrics — Group 4.

Đánh giá chất lượng question generation (QuGen) — thành phần cốt lõi của QUIS:
- 11a. Question Semantic Diversity        : đa dạng trong tập câu hỏi (within-system)
- 11b. Question Specificity               : độ dài (mean ± std) — câu hỏi càng cụ thể càng có giá trị
- 11c. Question-Insight Alignment         : câu hỏi có thực sự được trả lời bởi insight (cosine sim)
- 11d. Question Novelty (cross-system)    : câu hỏi của hệ A có khác hệ B không
- 11e. Reason-Insight Coherence           : reason (giải thích vì sao đáng hỏi) bám vào insight

Tất cả metric dùng SentenceTransformer all-MiniLM-L6-v2 (đồng nhất với novelty.py & diversity.py).
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

import numpy as np
from utils.model_singleton import get_embedding_model


# ───────────────────────── helpers ──────────────────────────

def _get_question(ins: Dict) -> str:
    return (ins.get('question') or ins.get('insight', {}).get('question') or '').strip()


def _get_reason(ins: Dict) -> str:
    d = ins.get('insight', {}) or {}
    return (
        ins.get('reason')
        or d.get('reason')
        or ins.get('explanation')
        or ''
    ).strip()


def _insight_string(ins: Dict) -> str:
    """Same canonical string used in novelty.py & diversity.py."""
    d = ins.get('insight', ins)
    breakdown = d.get('breakdown', '')
    measure = d.get('measure', '')
    pattern = d.get('pattern', '')
    subspace = d.get('subspace', []) or []
    if subspace:
        condition = ", ".join(f"{k}={v}" for k, v in subspace)
    else:
        condition = ''
    return f"{breakdown} | {measure} | {pattern} | {condition}"


def _embed(texts: List[str]):
    """Load model from singleton and encode."""
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False)


# ───────────────────── 11a. Question Semantic Diversity ─────────────────

def compute_question_diversity(insights: List[Dict], system_name: str = None) -> Dict[str, Any]:
    """
    D_q = 1 - mean cosine_similarity over (i,j), i != j

    Diversity câu hỏi within-system: 1.0 = tất cả câu hỏi khác hẳn nhau.
    Khác `4a Diversity — Semantic` ở chỗ chỉ dùng *question text*, không kèm
    breakdown|measure|pattern|subspace. Phơi bày trực tiếp đa dạng intent của
    QuGen, không bị "trộn" với output của IsGen.
    """
    if system_name == 'ONLYSTATS':
        return {'question_diversity': None, 'avg_similarity': None, 'num_questions': 0}
    qs = [_get_question(i) for i in insights]
    qs = [q for q in qs if q]
    n = len(qs)
    if n < 2:
        return {'question_diversity': 0.0, 'avg_similarity': 0.0, 'num_questions': n}

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        emb = _embed(qs)
        sim = cosine_similarity(emb)
        avg_sim = float((sim.sum() - sim.trace()) / (n * (n - 1)))
        return {
            'question_diversity': 1.0 - avg_sim,
            'avg_similarity': avg_sim,
            'num_questions': n,
        }
    except Exception as e:
        return {'question_diversity': 0.0, 'avg_similarity': 0.0,
                'num_questions': n, 'error': str(e)}


# ───────────────────── 11b. Question Specificity ─────────────────

def compute_question_specificity(insights: List[Dict], system_name: str = None) -> Dict[str, Any]:
    """
    Specificity_q = mean(#tokens(q_i))   (cao hơn -> câu hỏi cụ thể hơn)
    + reports stddev to capture variability across questions.

    Câu hỏi dài hơn thường mang nhiều ràng buộc semantic (column, value, time
    window, scope) -> chứng minh QuGen sinh câu hỏi chuyên biệt thay vì chung
    chung kiểu "What is the trend?".
    """
    if system_name == 'ONLYSTATS':
        return {'question_specificity_mean': None, 'question_specificity_std': None, 'num_questions': 0}
    qs = [_get_question(i) for i in insights]
    qs = [q for q in qs if q]
    if not qs:
        return {'question_specificity_mean': 0.0,
                'question_specificity_std': 0.0,
                'num_questions': 0}
    lens = [len(q.split()) for q in qs]
    return {
        'question_specificity_mean': float(np.mean(lens)),
        'question_specificity_std': float(np.std(lens)),
        'num_questions': len(qs),
    }


# ───────────────────── 11c. Question–Insight Alignment ─────────────────

def compute_question_insight_alignment(insights: List[Dict], system_name: str = None) -> Dict[str, Any]:
    """
    Align_{Q-I} = mean_i cosine( Embed(q_i), Embed(insight_string_i) )

    Đo "câu hỏi có thực sự được insight trả lời không". Đây là *faithfulness ở
    tầng ngữ nghĩa*: bù cho metric 1 vốn chỉ check số liệu. QuGen tốt -> insight
    sinh ra phải bám sát ngữ cảnh câu hỏi.
    """
    if system_name == 'ONLYSTATS':
        return {'question_insight_alignment': None, 'num_pairs': 0}
    qs, isos = [], []
    for ins in insights:
        q = _get_question(ins)
        if not q:
            continue
        qs.append(q)
        isos.append(_insight_string(ins))
    n = len(qs)
    if n == 0:
        return {'question_insight_alignment': 0.0, 'num_pairs': 0}

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        q_emb = _embed(qs)
        i_emb = _embed(isos)
        # Vectorised pairwise diag: cos(q_i, i_i)
        # cosine_similarity returns full matrix; we only need diagonal.
        # For modest n (<200) full matrix is cheap and avoids loops.
        sim = cosine_similarity(q_emb, i_emb)
        diag = np.array([sim[k, k] for k in range(n)])
        return {
            'question_insight_alignment': float(diag.mean()),
            'question_insight_alignment_std': float(diag.std()),
            'num_pairs': n,
        }
    except Exception as e:
        return {'question_insight_alignment': 0.0, 'num_pairs': n, 'error': str(e)}


# ───────────────────── 11d. Question Novelty (cross-system) ─────────────────

def compute_question_novelty(
    insights_a: List[Dict],
    insights_b: List[Dict],
    tau: float = 0.85,
    system_name: str = None,
) -> Dict[str, Any]:
    """
    Q-Novelty(A | B) = mean_i 1{ max_j cos(q_i^A, q_j^B) < tau }

    Khác metric 3 (Insight Novelty) ở chỗ chỉ so trên *question text* — tách
    "ý tưởng phân tích" khỏi kết quả phân tích. Hai hệ có thể trùng (B,M,
    pattern) nhưng đặt câu hỏi khác nhau -> vẫn novel ở góc QuGen.

    For ONLYSTATS, return None as it doesn't have proper questions.
    """
    # Skip for ONLYSTATS as it doesn't have proper questions
    if system_name == 'ONLYSTATS':
        return {'question_novelty': None, 'novel_count': 0, 'total_count': 0, 'tau': tau}
    qs_a = [_get_question(i) for i in insights_a]
    qs_a = [q for q in qs_a if q]
    qs_b = [_get_question(i) for i in insights_b]
    qs_b = [q for q in qs_b if q]
    n_a = len(qs_a)
    if n_a == 0 or len(qs_b) == 0:
        return {'question_novelty': 0.0, 'novel_count': 0,
                'total_count': n_a, 'avg_max_similarity': 0.0}

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        ea = _embed(qs_a)
        eb = _embed(qs_b)
        sim = cosine_similarity(ea, eb)
        max_sim = sim.max(axis=1)
        novel = int((max_sim < tau).sum())
        return {
            'question_novelty': novel / n_a,
            'novel_count': novel,
            'total_count': n_a,
            'avg_max_similarity': float(max_sim.mean()),
            'tau': tau,
        }
    except Exception as e:
        return {'question_novelty': 0.0, 'novel_count': 0,
                'total_count': n_a, 'avg_max_similarity': 0.0, 'error': str(e)}


# ───────────────────── 11e. Reason–Insight Coherence ─────────────────

def compute_reason_insight_coherence(insights: List[Dict], system_name: str = None) -> Dict[str, Any]:
    """
    Coh_{R-I} = mean_i cosine( Embed(reason_i), Embed(insight_string_i) )

    `reason` là output đặc trưng của QuGen (giải thích vì sao câu hỏi đáng hỏi).
    Coherence cao -> reason không chỉ là template mà thực sự liên quan tới
    insight được trả về. Đo *grounding* của reason — khía cạnh QuGen mà các bộ
    metric trước hoàn toàn bỏ qua.

    For ONLYSTATS, reason field is not available, so skip this metric.
    """
    # Skip for ONLYSTATS as it doesn't have reason field
    if system_name == 'ONLYSTATS':
        return {'reason_insight_coherence': None, 'num_pairs': 0}

    rs, isos = [], []
    for ins in insights:
        r = _get_reason(ins)
        if not r:
            continue
        rs.append(r)
        isos.append(_insight_string(ins))
    n = len(rs)
    if n == 0:
        return {'reason_insight_coherence': 0.0, 'num_pairs': 0}

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        r_emb = _embed(rs)
        i_emb = _embed(isos)
        sim = cosine_similarity(r_emb, i_emb)
        diag = np.array([sim[k, k] for k in range(n)])
        return {
            'reason_insight_coherence': float(diag.mean()),
            'reason_insight_coherence_std': float(diag.std()),
            'num_pairs': n,
        }
    except Exception as e:
        return {'reason_insight_coherence': 0.0, 'num_pairs': n, 'error': str(e)}


# ───────────────────── public single-call wrapper ─────────────────

def compute_question_quality(insights: List[Dict], system_name: str = None) -> Dict[str, Any]:
    """
    Run all *single-system* QuGen metrics. Cross-system metric (Question
    Novelty) is computed separately in run_evaluation.py because it needs both
    systems' insights.
    """
    return {
        'question_diversity': compute_question_diversity(insights, system_name),
        'question_specificity': compute_question_specificity(insights, system_name),
        'question_insight_alignment': compute_question_insight_alignment(insights, system_name),
        'reason_insight_coherence': compute_reason_insight_coherence(insights, system_name),
    }
