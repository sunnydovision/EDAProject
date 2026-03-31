import html
import os
import re
from typing import List

import pandas as pd
import plotly.colors as pc
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from quis.qugen.models import schema_from_dataframe, InsightCard
from quis.qugen.pipeline import QUGENPipeline, QUGENConfig
from quis.qugen.llm_client import get_default_llm_client, BaseLLMClient
from quis.isgen.pipeline import ISGENPipeline, ISGENConfig


st.set_page_config(
    page_title="EDA Insight Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊",
)

# Load environment variables from .env if present (e.g., OPENAI_API_KEY)
load_dotenv()


def _init_llm_client() -> BaseLLMClient:
    """
    Initialize LLM client.

    If OPENAI_API_KEY is set, use real OpenAI-compatible client.
    Otherwise fall back to mock client so the UI still works.
    """
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    use_mock_default = not has_key
    use_mock = st.sidebar.toggle(
        "Use mock LLM (no API key required)",
        value=use_mock_default,
        help="If enabled, uses a built-in mock model instead of calling OpenAI-compatible APIs.",
    )
    if not use_mock and not has_key:
        st.sidebar.warning(
            "OPENAI_API_KEY chưa được cấu hình. Đang tự chuyển sang mock LLM để tránh lỗi."
        )
        use_mock = True
    return get_default_llm_client(use_mock=use_mock)


def _sidebar_brand():
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <p class="sidebar-brand-title">Workspace</p>
            <p class="sidebar-brand-name">EDA Insight Explorer</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _style_app():
    """Inject dashboard-style styling: header, accents, borders, sidebar."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap');

        :root {
            --c-indigo: #4C6FFF;
            --c-indigo-soft: #EEF2FF;
            --c-teal: #0D9488;
            --c-teal-soft: #ECFEFF;
            --c-violet: #7C3AED;
            --c-violet-soft: #F5F3FF;
            --c-amber: #D97706;
            --c-amber-soft: #FFFBEB;
            --c-slate-900: #0F172A;
            --c-slate-600: #475569;
            --c-border: #E2E8F0;
        }

        html, body, [class*="css"] {
            font-family: "DM Sans", "Inter", system-ui, -apple-system, sans-serif;
        }

        .stApp {
            background: linear-gradient(165deg, #DCE7F5 0%, #E8EDF5 12%, #F0F3F8 40%, #F4F6FA 100%);
        }

        /* Main canvas: card-like */
        section[data-testid="stMain"] .block-container,
        .stMain .block-container,
        [data-testid="stMain"] .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            max-width: 1200px;
            background: #FFFFFF;
            border: 1px solid var(--c-border);
            border-radius: 20px;
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            box-shadow: 0 4px 40px rgba(15, 23, 42, 0.07);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
            border-right: 2px solid var(--c-border);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
        }

        /* App top bar */
        .app-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 45%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 1rem 1.35rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 12px 40px rgba(15, 23, 42, 0.28);
        }
        .app-topbar-left {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }
        .app-logo {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--c-indigo), #6366F1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.03em;
            box-shadow: 0 4px 14px rgba(76, 111, 255, 0.45);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .app-topbar-title {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.02em;
        }
        .app-topbar-sub {
            margin: 0.15rem 0 0 0;
            font-size: 0.8rem;
            color: #94A3B8;
            font-weight: 500;
        }
        .app-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .app-pill {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.35rem 0.65rem;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.12);
        }
        .app-pill--i { background: rgba(76, 111, 255, 0.25); color: #C7D2FE; }
        .app-pill--t { background: rgba(13, 148, 136, 0.25); color: #99F6E4; }
        .app-pill--v { background: rgba(124, 58, 237, 0.25); color: #DDD6FE; }

        /* Hero */
        .hero-wrap {
            display: grid;
            grid-template-columns: 1fr minmax(200px, 280px);
            gap: 1.25rem;
            align-items: stretch;
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 40%, #F0F9FF 100%);
            border: 1px solid var(--c-border);
            border-radius: 16px;
            padding: 1.5rem 1.5rem 1.35rem;
            margin-bottom: 1.35rem;
            box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
        }
        @media (max-width: 900px) {
            .hero-wrap { grid-template-columns: 1fr; }
        }
        .hero-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--c-indigo);
            background: var(--c-indigo-soft);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(76, 111, 255, 0.2);
            margin-bottom: 0.65rem;
        }
        .hero-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--c-slate-900);
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin: 0 0 0.45rem 0;
        }
        .hero-sub {
            font-size: 0.95rem;
            color: var(--c-slate-600);
            line-height: 1.55;
            margin: 0 0 1rem 0;
            max-width: 50ch;
        }
        .hero-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }
        .chip {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.35rem 0.7rem;
            border-radius: 8px;
            border: 1px solid transparent;
        }
        .chip--indigo { background: var(--c-indigo-soft); color: #4338CA; border-color: #C7D2FE; }
        .chip--teal { background: var(--c-teal-soft); color: #0F766E; border-color: #99F6E4; }
        .chip--violet { background: var(--c-violet-soft); color: #6D28D9; border-color: #DDD6FE; }
        .chip--amber { background: var(--c-amber-soft); color: #B45309; border-color: #FDE68A; }

        .hero-aside {
            border-radius: 14px;
            border: 1px solid var(--c-border);
            background: linear-gradient(160deg, var(--c-indigo-soft) 0%, #FFFFFF 55%, var(--c-teal-soft) 100%);
            padding: 1rem 1.1rem;
            position: relative;
            overflow: hidden;
        }
        .hero-aside::before {
            content: "";
            position: absolute;
            top: 0; right: 0;
            width: 120px; height: 120px;
            background: radial-gradient(circle, rgba(76,111,255,0.15) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-aside-title {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748B;
            margin: 0 0 0.5rem 0;
        }
        .hero-aside ul {
            margin: 0;
            padding-left: 1.1rem;
            color: #475569;
            font-size: 0.86rem;
            line-height: 1.55;
        }

        /* Section headers — colored left border */
        .section-wrap {
            margin: 2rem 0 1rem;
            padding: 0.85rem 1rem 0.85rem 1rem;
            border-radius: 12px;
            border: 1px solid var(--c-border);
            background: #FAFBFC;
            border-left: 4px solid var(--c-indigo);
        }
        .section-wrap--indigo { border-left-color: var(--c-indigo); background: linear-gradient(90deg, var(--c-indigo-soft) 0%, #FAFBFC 28%); }
        .section-wrap--teal { border-left-color: var(--c-teal); background: linear-gradient(90deg, var(--c-teal-soft) 0%, #FAFBFC 28%); }
        .section-wrap--violet { border-left-color: var(--c-violet); background: linear-gradient(90deg, var(--c-violet-soft) 0%, #FAFBFC 28%); }
        .section-wrap--amber { border-left-color: var(--c-amber); background: linear-gradient(90deg, var(--c-amber-soft) 0%, #FAFBFC 28%); }

        .section-head-row {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        .section-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: var(--c-slate-900);
            margin: 0;
            letter-spacing: -0.01em;
        }
        .section-accent {
            width: 48px;
            height: 3px;
            border-radius: 2px;
            background: linear-gradient(90deg, var(--c-indigo), #93C5FD);
            margin-top: 0.45rem;
        }
        .section-wrap--teal .section-accent { background: linear-gradient(90deg, var(--c-teal), #5EEAD4); }
        .section-wrap--violet .section-accent { background: linear-gradient(90deg, var(--c-violet), #C4B5FD); }
        .section-wrap--amber .section-accent { background: linear-gradient(90deg, var(--c-amber), #FCD34D); }
        .section-desc {
            font-size: 0.86rem;
            color: #64748B;
            margin: 0.4rem 0 0 0;
            max-width: 65ch;
        }

        /* Sidebar brand */
        .sidebar-brand {
            padding: 0.85rem 0.75rem;
            margin-bottom: 0.75rem;
            border-radius: 12px;
            border: 1px solid var(--c-border);
            background: linear-gradient(135deg, #FFFFFF, #F8FAFC);
        }
        .sidebar-brand-title {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #64748B;
            margin: 0 0 0.2rem 0;
        }
        .sidebar-brand-name {
            font-size: 1rem;
            font-weight: 700;
            color: var(--c-slate-900);
            margin: 0;
        }

        /* Metric strip */
        .metric-card {
            background: #FFFFFF;
            border: 1px solid var(--c-border);
            border-radius: 12px;
            padding: 1rem 1.15rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
            border-left: 4px solid #CBD5E1;
        }
        .metric-card--indigo { border-left-color: var(--c-indigo); background: linear-gradient(135deg, #FFFFFF, var(--c-indigo-soft)); }
        .metric-card--teal { border-left-color: var(--c-teal); background: linear-gradient(135deg, #FFFFFF, var(--c-teal-soft)); }
        .metric-card--violet { border-left-color: var(--c-violet); background: linear-gradient(135deg, #FFFFFF, var(--c-violet-soft)); }
        .metric-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #94A3B8;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            font-size: 1.32rem;
            font-weight: 700;
            color: var(--c-slate-900);
        }

        /* Data preview frame */
        .preview-frame {
            border: 1px solid var(--c-border);
            border-radius: 12px;
            overflow: hidden;
            background: #FFFFFF;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
        }

        .panel-subtitle {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748B;
            margin: 0 0 0.5rem 0;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border: 1px solid var(--c-border) !important;
            border-radius: 12px !important;
            background: #FAFBFC !important;
            margin-bottom: 0.5rem !important;
            overflow: hidden;
        }
        [data-testid="stExpander"] summary {
            font-weight: 600 !important;
            color: var(--c-slate-900) !important;
        }

        /* Insight recommendation box */
        .insight-reco {
            font-size: 0.92rem;
            color: #334155;
            line-height: 1.6;
            padding: 0.85rem 1rem;
            background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
            border: 1px solid var(--c-border);
            border-left: 4px solid var(--c-indigo);
            border-radius: 0 10px 10px 0;
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 2.5rem 1.5rem;
            background: linear-gradient(180deg, #FFFFFF, #F8FAFC);
            border: 2px dashed #CBD5E1;
            border-radius: 16px;
            color: #64748B;
        }
        .empty-state strong { color: #334155; }

        /* Insight card top accent (inside bordered container) */
        .insight-accent-bar {
            height: 4px;
            border-radius: 4px;
            margin: 0 0 0.75rem 0;
        }
        .insight-accent-bar--indigo { background: linear-gradient(90deg, #4C6FFF, #818CF8); }
        .insight-accent-bar--teal { background: linear-gradient(90deg, #0D9488, #2DD4BF); }
        .insight-accent-bar--violet { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
        .insight-accent-bar--amber { background: linear-gradient(90deg, #D97706, #FBBF24); }

        footer { visibility: hidden; height: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _app_header():
    st.markdown(
        """
        <div class="app-topbar">
            <div class="app-topbar-left">
                <div class="app-logo" aria-hidden="true">EI</div>
                <div>
                    <p class="app-topbar-title">EDA Insight Explorer</p>
                    <p class="app-topbar-sub">Automated exploration · LLM narratives · Actionable next steps</p>
                </div>
            </div>
            <div class="app-pills">
                <span class="app-pill app-pill--i">Data</span>
                <span class="app-pill app-pill--t">Questions</span>
                <span class="app-pill app-pill--v">Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _hero():
    st.markdown(
        """
        <div class="hero-wrap">
            <div>
                <div class="hero-badge">Exploratory analytics</div>
                <h1 class="hero-title">Turn your CSV into clear insights</h1>
                <p class="hero-sub">
                    Upload a dataset to preview structure, generate analyst-style questions,
                    and surface charts with summaries and recommendations—styled for readability.
                </p>
                <div class="hero-chips">
                    <span class="chip chip--indigo">CSV &amp; schema</span>
                    <span class="chip chip--teal">LLM questions</span>
                    <span class="chip chip--violet">Charts</span>
                    <span class="chip chip--amber">Recommendations</span>
                </div>
            </div>
            <aside class="hero-aside">
                <p class="hero-aside-title">Workflow</p>
                <ul>
                    <li><strong>Upload</strong> — detect delimiter &amp; dtypes</li>
                    <li><strong>Generate</strong> — insight cards via LLM</li>
                    <li><strong>Review</strong> — ranked plots &amp; narrative</li>
                </ul>
            </aside>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section(title: str, description: str = "", accent: str = "indigo"):
    """Section block with colored accent: indigo | teal | violet | amber."""
    cls = f"section-wrap section-wrap--{accent}"
    desc_html = f'<p class="section-desc">{description}</p>' if description else ""
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="section-head-row">
                <h2 class="section-title">{title}</h2>
            </div>
            <div class="section-accent"></div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _generate_llm_description(
    llm: BaseLLMClient,
    insight: dict,
    base_explanation: str,
) -> str:
    """Use LLM to turn template explanation into a richer, user-friendly description."""
    breakdown = insight.get("breakdown", "")
    measure = insight.get("measure", "")
    pattern = insight.get("pattern", "")
    subspace = insight.get("subspace") or []
    filters_desc = ", ".join(f"{c}={v}" for c, v in subspace) if subspace else "overall data"

    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []

    # Keep payload small: summarize a few points only
    preview_rows = []
    for i in range(min(5, len(labels))):
        preview_rows.append(f"- {breakdown} = {labels[i]} → {measure} = {values[i]}")
    preview_text = "\n".join(preview_rows)

    prompt = f"""
Bạn là chuyên gia phân tích dữ liệu, giải thích insight cho người dùng business không chuyên kỹ thuật.

Insight đầu vào:
- Loại pattern: {pattern}
- Breakdown column: {breakdown}
- Measure: {measure}
- Segment / filters: {filters_desc}

Tóm tắt số liệu (mẫu):
{preview_text or "No numeric sample available."}

Mô tả cơ bản:
\"\"\"{base_explanation}\"\"\"

Hãy viết lại bằng tiếng Việt tự nhiên, rõ ràng, tối đa 4 bullet.
- Tập trung vào ý chính và ý nghĩa kinh doanh.
- Tránh thuật ngữ khó hiểu.
- Có thể nêu 1-2 điểm nổi bật (nhóm cao nhất/thấp nhất/xu hướng).
    """.strip()

    try:
        text = llm.complete(prompt, temperature=0.6, max_tokens=512)
        if not text:
            return base_explanation
        # Guard rail: mock output or malformed output should not be shown as explanation.
        lowered = text.lower()
        if "[insight]" in lowered or "reason:" in lowered or "question:" in lowered:
            return base_explanation
        return text
    except Exception:
        return base_explanation


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _deduplicate_cards(cards: List[InsightCard]) -> List[InsightCard]:
    """
    Rule-based dedup in app layer to avoid repeated reason/question blocks,
    especially when embedding model is unavailable.
    """
    out: List[InsightCard] = []
    seen = set()
    for c in cards:
        q_norm = _normalize_text(c.question)
        r_norm = _normalize_text(c.reason)
        key = (_normalize_text(c.breakdown), _normalize_text(c.measure), q_norm)
        loose_key = (_normalize_text(c.breakdown), _normalize_text(c.measure), r_norm[:80])
        if key in seen or loose_key in seen:
            continue
        seen.add(key)
        seen.add(loose_key)
        out.append(c)
    return out


def _build_recommendation(insight: dict) -> str:
    """Generate practical next-step recommendation from insight metadata."""
    pattern = (insight.get("pattern") or "").lower()
    breakdown = insight.get("breakdown", "nhóm")
    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []
    if not labels or not values:
        return "Tiếp tục theo dõi thêm dữ liệu để xác nhận insight và ưu tiên nhóm có ảnh hưởng lớn nhất."

    pairs = list(zip(labels, values))
    top_label, top_value = max(pairs, key=lambda x: x[1])
    low_label, low_value = min(pairs, key=lambda x: x[1])

    if "trend" in pattern:
        return (
            f"Thiết lập cảnh báo theo thời gian cho `{breakdown}`; nếu xu hướng giảm, ưu tiên kiểm tra nguyên nhân "
            f"ở giai đoạn gần nhất và triển khai thử nghiệm cải thiện trong 1-2 chu kỳ."
        )
    if "attribution" in pattern:
        return (
            f"Nhóm `{top_label}` đang đóng góp cao nhất ({top_value:.2f}). Nên bảo vệ nhóm này (giữ khách, tối ưu tồn kho), "
            f"đồng thời xây kế hoạch tăng trưởng cho các nhóm còn lại."
        )
    if "outstanding" in pattern:
        return (
            f"Nhóm `{top_label}` nổi bật hơn phần còn lại. Cần kiểm tra đây là cơ hội (best practice) hay rủi ro phụ thuộc; "
            f"đồng thời phân tích vì sao `{low_label}` đang thấp ({low_value:.2f})."
        )
    return (
        f"Ưu tiên hành động trên nhóm `{top_label}` (giá trị cao nhất), sau đó lập kế hoạch cải thiện nhóm "
        f"`{low_label}` để cân bằng hiệu quả giữa các `{breakdown}`."
    )


def _make_chart(insight: dict):
    """Build a Plotly chart from ISGEN insight dict."""
    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []
    breakdown = insight.get("breakdown", "")
    measure = insight.get("measure", "")
    pattern = (insight.get("pattern") or "").lower()

    if not labels or not values or len(labels) != len(values):
        return None

    df_chart = pd.DataFrame(
        {
            breakdown or "Category": labels,
            measure or "Value": values,
        }
    )

    if "trend" in pattern:
        fig = px.line(
            df_chart,
            x=breakdown or "Category",
            y=measure or "Value",
            markers=True,
            template="simple_white",
        )
    else:
        fig = px.bar(
            df_chart,
            x=breakdown or "Category",
            y=measure or "Value",
            template="simple_white",
        )

    fig.update_layout(
        height=380,
        margin=dict(l=16, r=16, t=44, b=16),
        plot_bgcolor="#FAFBFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="DM Sans, Inter, system-ui, sans-serif", size=12, color="#475569"),
        xaxis=dict(
            title=dict(text=breakdown or "", font=dict(size=11, color="#64748B")),
            gridcolor="#EEF2FF",
            linecolor="#E2E8F0",
            tickangle=-35,
        ),
        yaxis=dict(
            title=dict(text=measure or "", font=dict(size=11, color="#64748B")),
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            zerolinecolor="#E2E8F0",
        ),
        title=dict(
            text=f"{pattern.title() if pattern else 'View'}",
            font=dict(size=13, color="#0F172A"),
            x=0.02,
            xanchor="left",
        ),
        dragmode=False,
        showlegend=False,
    )
    if "trend" in pattern:
        fig.update_traces(
            line=dict(color="#4C6FFF", width=2.5),
            marker=dict(size=8, color="#4C6FFF", line=dict(width=0)),
        )
    else:
        n = len(labels)
        abs_vals = [abs(v) for v in values]
        sorted_idx = sorted(range(n), key=lambda i: -abs_vals[i])
        _ACCENT_PALETTE = [
            "#4C6FFF", "#6366F1", "#818CF8", "#7C3AED", "#0D9488",
            "#0EA5E9", "#F59E0B", "#EF4444", "#10B981", "#F97316",
            "#EC4899", "#8B5CF6", "#14B8A6", "#F43F5E", "#3B82F6",
            "#22D3EE", "#A855F7", "#84CC16", "#FB923C", "#06B6D4",
        ]
        bar_colors = [_ACCENT_PALETTE[i % len(_ACCENT_PALETTE)] for i in range(n)]
        if n >= 2:
            bar_colors[sorted_idx[0]] = "#EF4444"
            bar_colors[sorted_idx[1]] = "#10B981"
    
        fig.update_traces(
            marker_color=bar_colors,
            marker_line=dict(color="#FFFFFF", width=1),
        )
    return fig


def run_app():
    _style_app()
    _app_header()
    _hero()

    _sidebar_brand()
    llm_client = _init_llm_client()

    st.sidebar.markdown("### Settings")
    st.sidebar.caption("Tune question generation and insight thresholds.")
    max_cards_per_iteration = st.sidebar.slider(
        "Questions per LLM call",
        min_value=4,
        max_value=12,
        value=8,
        step=2,
    )
    num_iterations = st.sidebar.slider(
        "LLM iterations",
        min_value=1,
        max_value=5,
        value=2,
    )
    threshold_scale = st.sidebar.slider(
        "Insight strictness",
        min_value=0.3,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower = more insights kept (relaxed thresholds).",
    )
    use_llm_explanations = st.sidebar.checkbox(
        "Rich LLM explanations",
        value=True,
        help="If off, show template explanations only.",
    )

    _section("Data", "Upload a CSV. Semicolon-delimited files are supported.", accent="indigo")
    uploaded = st.file_uploader(
        "Drop a file or browse",
        type=["csv"],
        help="Excel-exported CSV often uses `;` as separator—we detect it automatically.",
    )

    if uploaded is None:
        st.markdown(
            """
            <div class="empty-state">
                <strong>No file yet.</strong><br/>
                Choose a CSV above to preview your data and generate insights.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Robust CSV loading: handle semicolon separators and locale-style decimals.
    try:
        df = pd.read_csv(uploaded)
    except Exception:
        uploaded.seek(0)
        try:
            # Try automatic delimiter detection (handles ';', '\t', etc.)
            df = pd.read_csv(uploaded, sep=None, engine="python")
        except Exception:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, sep=";", engine="python")

    if df.empty:
        st.warning("The uploaded CSV appears to be empty.")
        return

    _section("Dataset overview", "First rows, shape, and column types.", accent="teal")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="metric-card metric-card--indigo"><div class="metric-label">Rows</div><div class="metric-value">{len(df):,}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card metric-card--teal"><div class="metric-label">Columns</div><div class="metric-value">{len(df.columns):,}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        fname = uploaded.name or "dataset.csv"
        st.markdown(
            f'<div class="metric-card metric-card--violet"><div class="metric-label">File</div><div class="metric-value" style="font-size:1rem;word-break:break-all;">{html.escape(fname)}</div></div>',
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([1.55, 1])
    with c1:
        st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
        try:
            st.dataframe(df.head(50), width="stretch", hide_index=True)
        except TypeError:
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<p class="panel-subtitle">Column types</p>', unsafe_allow_html=True)
        try:
            st.dataframe(
                pd.DataFrame({"Column": df.columns, "Dtype": df.dtypes.astype(str)}),
                width="stretch",
                hide_index=True,
            )
        except TypeError:
            st.dataframe(
                pd.DataFrame({"Column": df.columns, "Dtype": df.dtypes.astype(str)}),
                use_container_width=True,
                hide_index=True,
            )

    table_schema = schema_from_dataframe(df, table_name=os.path.splitext(uploaded.name)[0] or "Table")

    with st.spinner("Generating insight questions with LLM..."):
        qcfg = QUGENConfig(
            num_iterations=num_iterations,
            num_samples_per_iteration=1,
            num_questions_per_prompt=max_cards_per_iteration,
        )
        qugen = QUGENPipeline(config=qcfg, llm_client=llm_client)
        cards: List[InsightCard] = qugen.run(table_schema, df=df)
        cards = _deduplicate_cards(cards)

    if not cards:
        st.warning("No Insight Cards were generated. Try a different dataset or adjust the configuration.")
        return

    _section(
        "Generated questions",
        "Candidate questions from the LLM—expand to see breakdown and measure.",
        accent="violet",
    )
    for card in cards:
        with st.expander(card.question, expanded=False):
            st.markdown(f"**Why** · {card.reason or '—'}")
            st.caption(f"Breakdown `{card.breakdown}` · Measure `{card.measure}`")

    with st.spinner("Scoring insights and creating charts..."):
        isgen_cfg = ISGENConfig(
            plot_dir=None,
            max_insights_per_question=3,
            threshold_scale=threshold_scale,
        )
        isgen = ISGENPipeline(config=isgen_cfg, llm_client=llm_client)
        insight_summaries = isgen.run(df, cards=[c.to_dict() for c in cards])

    _section("Insights", "Charts, narrative summary, and recommended next steps.", accent="amber")
    if not insight_summaries:
        st.info(
            "No insights passed the current threshold. Lower **Insight strictness** in the sidebar and rerun."
        )
        return

    for idx, item in enumerate(insight_summaries):
        ins = item.get("insight") or {}
        base_expl = item.get("explanation", "")
        pattern = ins.get("pattern", "")
        question = item.get("question", "")

        if use_llm_explanations:
            description = _generate_llm_description(llm_client, ins, base_expl)
        else:
            description = base_expl
        recommendation = _build_recommendation(ins)

        chart = _make_chart(ins)

        try:
            card_wrap = st.container(border=True)
        except TypeError:
            card_wrap = st.container()

        _accent = ["indigo", "teal", "violet", "amber"][idx % 4]
        with card_wrap:
            st.markdown(
                f'<div class="insight-accent-bar insight-accent-bar--{_accent}"></div>',
                unsafe_allow_html=True,
            )
            st.caption((pattern or "Insight").upper())
            st.subheader(question or "Untitled insight")
            col_chart, col_text = st.columns([1.15, 1], gap="large")
            with col_chart:
                if chart is not None:
                    try:
                        st.plotly_chart(
                            chart,
                            width="stretch",
                            config={"displayModeBar": False},
                            key=f"insight_plot_{idx}",
                        )
                    except TypeError:
                        st.plotly_chart(
                            chart,
                            use_container_width=True,
                            config={"displayModeBar": False},
                            key=f"insight_plot_{idx}",
                        )
                else:
                    st.caption("Chart not available for this insight.")
            with col_text:
                st.markdown('<p class="insight-label">Summary</p>', unsafe_allow_html=True)
                st.markdown(description)
                st.markdown('<p class="insight-label">Recommendation</p>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="insight-reco">{html.escape(recommendation)}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<br/>", unsafe_allow_html=True)


if __name__ == "__main__":
    run_app()

