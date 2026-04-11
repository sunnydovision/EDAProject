import base64
import glob
import hashlib
import html
import json
import os
import re
from datetime import datetime
from functools import lru_cache
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from quis.qugen.models import schema_from_dataframe, InsightCard
from quis.qugen.pipeline import QUGENPipeline, QUGENConfig
from quis.qugen.llm_client import get_default_llm_client, BaseLLMClient
from quis.isgen.pipeline import ISGENPipeline, ISGENConfig
from quis.isgen.views import parse_measure


st.set_page_config(
    page_title="Sun Smart Report",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="wb_sunny",
)

load_dotenv()

# ---------------------------------------------------------------------------
# Cached I/O (History / large CSV) — reduces reload latency on tab switch & pager
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading dataset…", ttl=300)
def _cached_load_csv(path: str) -> pd.DataFrame | None:
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    df = pd.read_csv(path, sep=sep, decimal="," if sep == ";" else ".")
    return _clean_dataframe(df, sep=sep)


@st.cache_data(show_spinner="Loading report…", ttl=120)
def _cached_load_insights_json(path: str) -> list | None:
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


@st.cache_data(show_spinner=False, ttl=45)
def _cached_discover_history(_project_root: str) -> tuple:
    """Tuple of dicts so cache key can include root; refresh every ~45s for new JSON files."""
    root = _project_root
    results = []
    for path in sorted(glob.glob(os.path.join(root, "insights_summary*.json"))):
        fname = os.path.basename(path)
        name = fname.replace("insights_summary_", "").replace("insights_summary", "").replace(".json", "")
        if not name:
            name = "default"
        cards_path = path.replace("insights_summary", "insight_cards")
        csv_candidates = [
            os.path.join(root, "data", f"{name}.csv"),
            os.path.join(root, "data", f"{name.title()}.csv"),
            os.path.join(root, "data", f"{name.upper()}.csv"),
            os.path.join(root, "data", f"{name.capitalize()}.csv"),
            os.path.join(root, f"{name}.csv"),
        ]
        # Adidas retail pipeline: insights_summary_adidas_cleaned.json → data/Adidas_cleaned.csv
        nl = name.lower()
        if nl == "adidas_cleaned":
            for ad in (
                os.path.join(root, "data", "Adidas_cleaned.csv"),
                os.path.join(root, "data", "adidas_cleaned.csv"),
            ):
                if os.path.isfile(ad):
                    csv_candidates = [ad] + [p for p in csv_candidates if p != ad]
                    break
        if not any(os.path.isfile(p) for p in csv_candidates):
            for p in glob.glob(os.path.join(root, "data", "*.csv")):
                if os.path.basename(p).lower() == f"{name.lower()}.csv":
                    csv_candidates.insert(0, p)
        csv_path = next((p for p in csv_candidates if os.path.isfile(p)), None)
        results.append({
            "label": name.replace("_", " ").title(),
            "insights_path": path,
            "cards_path": cards_path if os.path.isfile(cards_path) else None,
            "csv_path": csv_path,
        })
    return tuple(results)


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------
_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@lru_cache(maxsize=16)
def _icon_b64(filename: str) -> str:
    """Return a base64 data-URI for a PNG icon in the assets folder."""
    path = os.path.join(_ASSET_DIR, filename)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"


def _icon_img(filename: str, height: int = 48, extra_style: str = "") -> str:
    """Return an <img> tag for an asset icon."""
    uri = _icon_b64(filename)
    if not uri:
        return ""
    return f'<img src="{uri}" height="{height}" style="object-fit:contain;{extra_style}" />'


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
_SURFACE = "#060e20"
_SURFACE_LOW = "#091328"
_SURFACE_MID = "#0f1930"
_SURFACE_HIGH = "#141f38"
_SURFACE_HIGHEST = "#192540"
_SURFACE_BRIGHT = "#1f2b49"
_PRIMARY = "#a3a6ff"
_PRIMARY_DIM = "#6063ee"
_TERTIARY = "#c6fff3"
_TERTIARY_DIM = "#48e5d0"
_ON_SURFACE = "#dee5ff"
_ON_SURFACE_VAR = "#a3aac4"
_OUTLINE_VAR = "#40485d"
_ERROR = "#ff6e84"


def _init_llm_client() -> BaseLLMClient:
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    use_mock = st.session_state.get("use_mock_llm", not has_key)
    if not use_mock and not has_key:
        use_mock = True
    return get_default_llm_client(use_mock=use_mock)


def _clean_dataframe(df: pd.DataFrame, sep: str = ",") -> pd.DataFrame:
    """Clean currency ($), percentage (%), and European number formatting."""
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(20).astype(str).str.strip()
            numeric_like = sample.str.match(r"^\$?\s*[\d.,]+\s*%?$")
            if numeric_like.sum() >= len(sample) * 0.8:
                cleaned = df[col].astype(str).str.replace(r"[$%]", "", regex=True).str.strip()
                if sep == ";":
                    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted
    return df


# ───────────────────────────────────────────────────────────────────────────
# CSS
# ───────────────────────────────────────────────────────────────────────────
def _style_app():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

        :root {{
            --surface: {_SURFACE};
            --surface-low: {_SURFACE_LOW};
            --surface-mid: {_SURFACE_MID};
            --surface-high: {_SURFACE_HIGH};
            --surface-highest: {_SURFACE_HIGHEST};
            --surface-bright: {_SURFACE_BRIGHT};
            --primary: {_PRIMARY};
            --primary-dim: {_PRIMARY_DIM};
            --tertiary: {_TERTIARY};
            --tertiary-dim: {_TERTIARY_DIM};
            --on-surface: {_ON_SURFACE};
            --on-surface-var: {_ON_SURFACE_VAR};
            --outline-var: {_OUTLINE_VAR};
            --error: {_ERROR};
        }}

        html, body, [class*="css"] {{
            font-family: "Inter", system-ui, -apple-system, sans-serif;
            color: var(--on-surface);
            font-size: 1.2675rem;
        }}
        .stApp {{ background: var(--surface) !important; }}

        /* Hide Streamlit chrome */
        [data-testid="stHeader"] {{
            background: transparent !important;
            height: 0 !important; min-height: 0 !important; overflow: hidden !important;
        }}
        [data-testid="stToolbar"], #MainMenu,
        [data-testid="stSidebar"], [data-testid="collapsedControl"],
        [data-testid="stStatusWidget"] {{ display: none !important; }}

        section[data-testid="stMain"] .block-container,
        .stMain .block-container,
        [data-testid="stMain"] .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1500px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            background: transparent;
        }}

        /* ── Tabs styled as top navigation ── */
        .stTabs [data-baseweb="tab-list"] {{
            background: transparent !important;
            border-radius: 0;
            padding: 0;
            gap: 0.25rem;
            border-bottom: 1px solid rgba(64, 72, 93, 0.2);
            margin-bottom: 1.5rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: "Inter", sans-serif;
            font-weight: 500;
            font-size: 1.02rem;
            color: var(--on-surface-var);
            border-radius: 0;
            height: auto;
            padding: 0.6rem 1.25rem;
            background: transparent !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--on-surface) !important;
            background: transparent !important;
            font-weight: 600;
            border-bottom: 2px solid var(--primary) !important;
        }}
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

        /* ── Topbar ── */
        .cl-topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0 1.25rem;
            margin-bottom: 0.25rem;
            position: relative;
            z-index: 2;
        }}
        .cl-topbar-left {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            flex-wrap: nowrap;
            min-width: 0;
        }}
        .cl-topbar-icon {{
            color: var(--primary);
            font-size: clamp(1.375rem, 2vw + 0.75rem, 2.75rem) !important;
            flex-shrink: 0;
        }}
        .cl-topbar-title,
        .stMarkdown p.cl-topbar-title,
        div[data-testid="stMarkdownContainer"] p.cl-topbar-title {{
            font-family: "Manrope", sans-serif !important;
            font-weight: 800 !important;
            font-size: clamp(1.625rem, 2.5vw + 1.25rem, 4rem) !important;
            line-height: 1.05 !important;
            color: var(--on-surface) !important;
            letter-spacing: -0.03em;
            margin: 0 !important;
            white-space: nowrap !important;
        }}

        /* ── Neuron corner decorations (fixed, non-interactive) ── */
        section[data-testid="stMain"] {{
            position: relative;
            z-index: 1;
        }}
        .cl-corner-deco-anchor {{
            height: 0;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .cl-corner-deco {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }}
        .cl-neuron-corner {{
            position: absolute;
            object-fit: contain;
            mix-blend-mode: screen;
        }}
        /* Nhỏ + mờ — gợi ý nền */
        .cl-neuron-corner--tl {{
            top: 3.25rem;
            left: -0.5rem;
            width: min(240px, 26vw);
            transform: rotate(-9deg);
            opacity: 0.18;
            filter: saturate(1.1) brightness(1.04)
                drop-shadow(0 0 20px rgba(72, 229, 208, 0.18));
        }}
        /* Lớn + rõ — điểm nhấn góc phải trên */
        .cl-neuron-corner--tr {{
            top: 1.5rem;
            right: -4rem;
            width: min(720px, 74vw);
            transform: scaleX(-1) rotate(7deg);
            opacity: 0.82;
            filter: saturate(1.5) brightness(1.2) contrast(1.1)
                drop-shadow(0 0 48px rgba(72, 229, 208, 0.55));
        }}
        /* Rất lớn + khá mờ — khối sâu phía dưới */
        .cl-neuron-corner--bl {{
            bottom: -3rem;
            left: -10rem;
            width: min(1050px, 96vw);
            max-height: 72vh;
            transform: rotate(5deg);
            opacity: 0.28;
            filter: saturate(1.2) brightness(1.08)
                drop-shadow(0 0 56px rgba(72, 229, 208, 0.22));
        }}
        /* Nhỏ vừa + rõ nhất — chi tiết sắc ở góc phải dưới */
        .cl-neuron-corner--br {{
            bottom: 0.5rem;
            right: -0.75rem;
            width: min(320px, 36vw);
            transform: scaleX(-1) rotate(-11deg);
            opacity: 0.88;
            filter: saturate(1.45) brightness(1.22) contrast(1.12)
                drop-shadow(0 0 32px rgba(72, 229, 208, 0.5));
        }}

        /* ── Hero ── */
        .cl-hero {{
            background: transparent;
            padding: 1.5rem 0;
            position: relative;
        }}
        .cl-hero-title {{
            font-family: "Manrope", sans-serif;
            font-weight: 800;
            font-size: 2.4rem;
            color: var(--on-surface);
            margin: 0 0 0.75rem;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }}
        .cl-hero-sub {{
            font-size: 1.08rem;
            color: var(--on-surface-var);
            line-height: 1.6;
            margin: 0 0 1.25rem;
            max-width: 48ch;
        }}

        /* ── Insight preview card (hero right) ── */
        .cl-preview {{
            background: var(--surface-low);
            border: 1px solid rgba(64, 72, 93, 0.25);
            border-radius: 20px;
            padding: 1.25rem 1.5rem;
            position: relative;
            overflow: hidden;
            margin-bottom: 2rem;
            isolation: isolate;
        }}
        .cl-preview::before {{
            content: "";
            position: absolute;
            top: -60px; right: -60px;
            width: 250px; height: 250px;
            background: radial-gradient(circle, rgba(163,166,255,0.06) 0%, transparent 70%);
            pointer-events: none;
        }}
        .cl-preview-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.65rem 1rem;
            margin-bottom: 1rem;
        }}
        .cl-preview-header-badges {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-end;
            gap: 0.45rem;
            max-width: 100%;
        }}
        .cl-preview-title {{
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--tertiary);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .cl-preview-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        .cl-preview-mini {{
            background: var(--surface-mid);
            border-radius: 12px;
            padding: 0.85rem 1rem;
        }}
        .cl-preview-mini-label {{
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--on-surface);
            margin: 0 0 0.15rem;
        }}
        .cl-preview-mini-sub {{
            font-size: 0.72rem;
            color: var(--on-surface-var);
            margin: 0;
        }}
        .cl-preview-mini-value {{
            font-family: "Manrope", sans-serif;
            font-size: 1.35rem;
            font-weight: 800;
            margin: 0.25rem 0 0;
        }}
        .cl-preview-mini-value--up {{ color: var(--tertiary); }}
        .cl-preview-mini-value--primary {{ color: var(--primary); }}
        .cl-preview-footer {{
            background: var(--surface-mid);
            border-radius: 14px;
            padding: 0.85rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: nowrap;
            margin-top: 0.75rem;
            margin-bottom: 0;
            position: relative;
            z-index: 1;
        }}
        .cl-preview-footer--compact {{
            padding: 0.65rem 0.95rem;
        }}
        .cl-preview-stat-line {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--on-surface);
            margin: 0;
            line-height: 1.35;
        }}
        .cl-preview-stat-num {{
            font-family: "Manrope", sans-serif;
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--tertiary);
            margin-right: 0.35rem;
        }}
        .cl-report-metrics-spacer {{
            display: block;
            min-height: 1px;
            margin-top: 1.25rem;
            margin-bottom: 0.25rem;
            clear: both;
        }}
        .cl-preview-big {{
            font-family: "Manrope", sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: var(--on-surface);
            margin: 0;
            line-height: 1;
        }}
        .cl-preview-big-label {{
            font-size: 0.95rem;
            color: var(--on-surface-var);
            margin: 0;
        }}

        /* ── Section header ── */
        .cl-section {{
            padding: 0.5rem 0;
            margin: 1.25rem 0 0.5rem;
        }}
        .cl-section-row {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}
        .cl-section-title {{
            font-family: "Manrope", sans-serif;
            font-weight: 700;
            font-size: 1.02rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--on-surface);
            margin: 0;
        }}
        .cl-section-desc {{
            font-size: 1.05rem;
            color: var(--on-surface-var);
            margin: 0.3rem 0 0;
        }}

        /* ── Metric cards (equal height; labels one line when space allows) ── */
        .cl-metric {{
            background: var(--surface-mid);
            border: 1px solid rgba(64, 72, 93, 0.15);
            border-radius: 14px;
            padding: 1rem 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-width: 0;
            box-sizing: border-box;
            min-height: 6.25rem;
            height: 100%;
        }}
        .cl-metric-body {{
            flex: 1;
            min-width: 0;
        }}
        .cl-metric-icon {{
            width: 48px; height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .cl-metric-icon--primary {{ background: rgba(163, 166, 255, 0.12); color: var(--primary); }}
        .cl-metric-icon--tertiary {{ background: rgba(198, 255, 243, 0.1); color: var(--tertiary); }}
        .cl-metric-icon--dim {{ background: rgba(163, 170, 196, 0.1); color: var(--on-surface-var); }}
        .cl-metric-icon--accent {{ background: rgba(255, 110, 132, 0.1); color: var(--error); }}
        .cl-metric-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: var(--on-surface-var);
            margin: 0 0 0.15rem;
            white-space: nowrap;
            line-height: 1.25;
        }}
        .cl-metric-value {{
            font-family: "Manrope", sans-serif;
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--on-surface);
            margin: 0;
            line-height: 1.1;
        }}

        h1, h2, h3, h4 {{
            font-family: "Manrope", sans-serif !important;
            color: var(--on-surface) !important;
        }}

        /* ── Settings card ── */
        .cl-settings-card {{
            background: var(--surface-mid);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }}

        .stExpander {{
            background: var(--surface-mid) !important;
            border: 1px solid rgba(64, 72, 93, 0.15) !important;
            border-radius: 12px !important;
        }}
        .stExpander summary span {{
            color: var(--on-surface) !important;
            font-weight: 600 !important;
        }}

        /* ── Generated question: insight body inside expander ── */
        .cl-q-insight {{
            padding: 0.1rem 0 0.2rem;
        }}
        .cl-q-insight-why {{
            font-size: 1.05rem;
            line-height: 1.65;
            color: var(--on-surface);
            margin: 0 0 1rem;
        }}
        .cl-q-insight-why-keyword {{
            font-weight: 700;
            color: var(--on-surface);
        }}
        .cl-q-insight-why-sep {{
            color: var(--on-surface-var);
            font-weight: 500;
        }}
        .cl-q-insight-why-text {{
            font-weight: 400;
        }}
        .cl-q-insight-meta {{
            font-size: 0.92rem;
            line-height: 1.55;
            padding-top: 0.75rem;
            margin-top: 0.15rem;
            border-top: 1px solid rgba(64, 72, 93, 0.28);
        }}
        .cl-q-insight-meta-k {{
            color: var(--on-surface-var);
            font-weight: 600;
            margin-right: 0.35rem;
        }}
        .cl-q-insight-meta-mid {{
            color: var(--on-surface-var);
            margin: 0 0.4rem;
        }}
        .cl-q-insight-meta-v {{
            color: var(--tertiary);
            font-weight: 600;
        }}

        /* ── Insight card: header above chart (merged layout) ── */
        .cl-insight-card-head {{
            position: relative;
            padding-top: 0.45rem;
            margin: -0.15rem 0 0.35rem 0;
        }}
        .cl-insight-card-head--primary::before,
        .cl-insight-card-head--tertiary::before,
        .cl-insight-card-head--dim::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            border-radius: 8px 8px 0 0;
        }}
        .cl-insight-card-head--primary::before {{ background: linear-gradient(90deg, var(--primary), var(--primary-dim)); }}
        .cl-insight-card-head--tertiary::before {{ background: linear-gradient(90deg, var(--tertiary), var(--tertiary-dim)); }}
        .cl-insight-card-head--dim::before {{ background: linear-gradient(90deg, var(--on-surface-var), var(--surface-bright)); }}
        .cl-insight-question--tight {{ margin-bottom: 0.35rem !important; }}

        div[data-testid="stFileUploader"] {{
            background: var(--surface-low);
            border: 2px dashed rgba(64, 72, 93, 0.3);
            border-radius: 14px;
            padding: 1rem;
            transition: all 0.3s;
        }}
        div[data-testid="stFileUploader"]:hover {{
            border-color: rgba(163, 166, 255, 0.5);
            background: var(--surface-mid);
        }}

        .stDataFrame, [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}
        footer {{ visibility: hidden; height: 0; }}

        /* ── Glass panel ── */
        .glass-panel {{
            background: rgba(20, 31, 56, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(64, 72, 93, 0.15);
            border-radius: 14px;
            padding: 0.85rem 1.15rem;
        }}

        /* ── Chips ── */
        .ai-chip {{
            display: inline-flex; align-items: center; gap: 0.4rem;
            font-size: 0.88rem; font-weight: 600;
            letter-spacing: 0.04em;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
            border: 1px solid rgba(198, 255, 243, 0.2);
            background: rgba(101, 253, 230, 0.08);
            color: var(--tertiary);
        }}
        .ai-chip--primary {{
            border-color: rgba(163, 166, 255, 0.2);
            background: rgba(163, 166, 255, 0.08);
            color: var(--primary);
        }}
        .ai-chip--dim {{
            border-color: rgba(163, 170, 196, 0.15);
            background: rgba(163, 170, 196, 0.06);
            color: var(--on-surface-var);
        }}

        /* ── Insight card ── */
        .cl-insight-card {{
            background: var(--surface-mid);
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            margin-bottom: 0.85rem;
            position: relative; overflow: hidden;
        }}
        .cl-insight-card::before {{
            content: "";
            position: absolute; top: 0; left: 0;
            width: 100%; height: 3px;
        }}
        .cl-insight-card--primary::before {{ background: linear-gradient(90deg, var(--primary), var(--primary-dim)); }}
        .cl-insight-card--tertiary::before {{ background: linear-gradient(90deg, var(--tertiary), var(--tertiary-dim)); }}
        .cl-insight-card--dim::before {{ background: linear-gradient(90deg, var(--on-surface-var), var(--surface-bright)); }}
        .cl-insight-pattern {{
            font-size: 0.85rem; font-weight: 700;
            letter-spacing: 0.12em; text-transform: uppercase;
            color: var(--tertiary); margin: 0 0 0.4rem;
        }}
        .cl-insight-question {{
            font-family: "Manrope", sans-serif;
            font-size: 1.25rem; font-weight: 700;
            color: var(--on-surface); margin: 0 0 1rem; line-height: 1.4;
        }}

        .cl-label {{
            font-size: 0.88rem; font-weight: 700;
            letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--on-surface-var); margin: 0 0 0.4rem;
        }}
        .cl-body {{ font-size: 1.08rem; color: var(--on-surface); line-height: 1.65; }}
        .cl-reco {{
            font-size: 1.06rem; color: var(--on-surface); line-height: 1.6;
            padding: 0.85rem 1rem;
            background: rgba(163, 166, 255, 0.06);
            border-radius: 12px; margin-top: 0.3rem;
        }}

        @keyframes cl-pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.6; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
        }}
        .cl-pulse {{
            width: 10px; height: 10px; border-radius: 50%;
            background: radial-gradient(circle, var(--tertiary), transparent);
            animation: cl-pulse 2s ease-in-out infinite; display: inline-block;
        }}

        .cl-empty {{
            text-align: center; padding: 2rem 1.5rem;
            background: var(--surface-low);
            border: 2px dashed rgba(64, 72, 93, 0.25);
            border-radius: 16px; color: var(--on-surface-var);
        }}
        .cl-empty strong {{ color: var(--on-surface); }}

        /* ── Textarea ── */
        [data-testid="stTextArea"] textarea {{
            background: #000000 !important;
            border: 1px solid rgba(64, 72, 93, 0.15) !important;
            border-radius: 12px !important;
            color: var(--on-surface) !important;
            font-family: "Inter", sans-serif !important;
            font-size: 1.1rem !important;
        }}
        [data-testid="stTextArea"] textarea::placeholder {{
            color: rgba(163, 170, 196, 0.5) !important;
        }}
        [data-testid="stTextArea"] textarea:focus {{
            border-color: rgba(163, 166, 255, 0.5) !important;
            box-shadow: 0 0 0 4px rgba(163, 166, 255, 0.1) !important;
        }}

        /* ── Primary button ── */
        button[kind="primary"], button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dim) 100%) !important;
            color: #0a0081 !important;
            font-family: "Manrope", sans-serif !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            border: none !important;
            border-radius: 12px !important;
            height: 3.2rem !important;
            box-shadow: 0 8px 24px -8px rgba(163, 166, 255, 0.3) !important;
            transition: transform 0.15s !important;
        }}
        button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
            transform: scale(1.02) !important;
        }}

        .cl-security {{
            text-align: center;
            color: rgba(163, 170, 196, 0.4);
            font-size: 0.8rem; font-weight: 500;
            letter-spacing: 0.2em; text-transform: uppercase;
            margin-top: 0.75rem; margin-bottom: 0;
        }}

        .cl-pager-info {{
            font-size: 0.98rem;
            color: var(--on-surface-var);
            font-weight: 500; margin: 0;
            min-width: 10ch; text-align: center;
        }}

        /* ── History tab (reference layout) ── */
        .cl-history-wrap {{
            position: relative;
            margin: 0 -0.5rem 1.5rem;
            padding: 1.5rem 1.25rem 2rem;
            border-radius: 24px;
            background: linear-gradient(165deg, rgba(11, 14, 20, 0.95) 0%, rgba(15, 25, 48, 0.5) 50%, rgba(6, 14, 32, 0.9) 100%);
            border: 1px solid rgba(79, 179, 255, 0.08);
            overflow: hidden;
        }}
        .cl-history-wrap::before {{
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                radial-gradient(2px 2px at 20% 30%, rgba(79, 179, 255, 0.35), transparent),
                radial-gradient(2px 2px at 80% 20%, rgba(163, 166, 255, 0.25), transparent),
                radial-gradient(1.5px 1.5px at 50% 60%, rgba(72, 229, 208, 0.3), transparent),
                radial-gradient(1.5px 1.5px at 70% 80%, rgba(79, 179, 255, 0.2), transparent);
            background-size: 100% 100%;
            opacity: 0.45;
            pointer-events: none;
        }}
        .cl-history-wrap::after {{
            content: "";
            position: absolute;
            top: 10%; left: 35%; right: 15%; bottom: 20%;
            background:
                linear-gradient(90deg, transparent 0%, rgba(79, 179, 255, 0.04) 50%, transparent 100%),
                linear-gradient(180deg, transparent 40%, rgba(79, 179, 255, 0.03) 100%);
            pointer-events: none;
        }}
        .cl-preview-glow {{
            box-shadow: 0 0 0 1px rgba(79, 179, 255, 0.12),
                        0 8px 40px -12px rgba(0, 212, 255, 0.25),
                        0 24px 64px -24px rgba(0, 0, 0, 0.5);
            border-color: rgba(79, 179, 255, 0.2) !important;
        }}
        .cl-history-select {{
            margin-bottom: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ───────────────────────────────────────────────────────────────────────────
# UI components
# ───────────────────────────────────────────────────────────────────────────
def _topbar():
    st.markdown(
        """
        <div class="cl-topbar">
            <div class="cl-topbar-left">
                <span class="material-symbols-outlined cl-topbar-icon">wb_sunny</span>
                <p class="cl-topbar-title">Sun Smart Report</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _neuron_corner_decorations():
    """Subtle fixed neuron art in viewport corners (different sizes); does not capture clicks."""
    uri = _icon_b64("neuron_icon.png")
    if not uri:
        return
    st.markdown(
        f"""
        <div class="cl-corner-deco-anchor">
            <div class="cl-corner-deco" aria-hidden="true">
                <img src="{uri}" alt="" class="cl-neuron-corner cl-neuron-corner--tl" />
                <img src="{uri}" alt="" class="cl-neuron-corner cl-neuron-corner--tr" />
                <img src="{uri}" alt="" class="cl-neuron-corner cl-neuron-corner--bl" />
                <img src="{uri}" alt="" class="cl-neuron-corner cl-neuron-corner--br" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section(title: str, description: str = "", icon: str = "auto_awesome", img_icon: str = ""):
    desc_html = f'<p class="cl-section-desc">{description}</p>' if description else ""
    if img_icon:
        icon_html = _icon_img(img_icon, height=31, extra_style="vertical-align:middle;margin-right:2px;")
    else:
        icon_html = f'<span class="material-symbols-outlined" style="font-size:22px;color:{_TERTIARY};">{icon}</span>'
    st.markdown(
        f"""
        <div class="cl-section">
            <div class="cl-section-row">
                {icon_html}
                <h3 class="cl-section-title">{title}</h3>
            </div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(icon: str, icon_variant: str, label: str, value: str, img_icon: str = ""):
    if img_icon:
        icon_inner = _icon_img(img_icon, height=35)
    else:
        icon_inner = f'<span class="material-symbols-outlined" style="font-size:29px;">{icon}</span>'
    st.markdown(
        f"""<div class="cl-metric">
            <div class="cl-metric-icon cl-metric-icon--{icon_variant}">
                {icon_inner}
            </div>
            <div class="cl-metric-body">
                <p class="cl-metric-label">{label}</p>
                <p class="cl-metric-value">{value}</p>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _insight_preview(df: pd.DataFrame | None, insight_summaries: list | None):
    """Right-side hero preview card with insight stats."""
    n_insights = len(insight_summaries) if insight_summaries else 0
    n_rows = f"{len(df):,}" if df is not None else "—"
    n_cols = str(len(df.columns)) if df is not None else "—"

    patterns: dict[str, int] = {}
    if insight_summaries:
        for item in insight_summaries:
            ins = item.get("insight") or {}
            p = (ins.get("pattern") or "Other").title()
            patterns[p] = patterns.get(p, 0) + 1

    top_patterns = sorted(patterns.items(), key=lambda x: -x[1])[:4]

    mini_cards = ""
    _colors = [_TERTIARY, _PRIMARY, _ON_SURFACE_VAR, _ERROR]
    for i, (pname, pcount) in enumerate(top_patterns):
        color = _colors[i % len(_colors)]
        mini_cards += f"""
        <div class="cl-preview-mini">
            <p class="cl-preview-mini-label">{html.escape(pname)}</p>
            <p class="cl-preview-mini-sub">pattern insights</p>
            <p class="cl-preview-mini-value" style="color:{color};">{pcount}</p>
        </div>"""

    if not mini_cards:
        mini_cards = """
        <div class="cl-preview-mini" style="grid-column: 1/-1; text-align:center;">
            <p class="cl-preview-mini-label" style="color:var(--on-surface-var);">No insights yet</p>
            <p class="cl-preview-mini-sub">Upload data and run the AI agent</p>
        </div>"""

    st.markdown(
        f"""
        <div class="cl-preview">
            <div class="cl-preview-header">
                <p class="cl-preview-title">
                    {_icon_img("icon_insight.png", height=22)}
                    Insights Overview
                </p>
                <div class="cl-preview-header-badges">
                    <span class="ai-chip--dim ai-chip" style="font-size:0.7rem;padding:0.25rem 0.6rem;">
                        {n_rows} rows &middot; {n_cols} cols
                    </span>
                </div>
            </div>
            <div class="cl-preview-grid">{mini_cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _file_mtime_label(path: str | None) -> str:
    if not path or not os.path.isfile(path):
        return "—"
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y")
    except OSError:
        return "—"


def _render_history_preview_charts(insight_data: list, key_suffix: str = "0"):
    """History hero right column: Insight mix (donut) + footer counts."""
    pattern_counts: dict[str, int] = {}
    for item in insight_data:
        ins = item.get("insight") or {}
        p = (ins.get("pattern") or "Other").replace("_", " ").title()
        pattern_counts[p] = pattern_counts.get(p, 0) + 1

    fig_pie = None
    if pattern_counts:
        fig_pie = px.pie(
            names=list(pattern_counts.keys()),
            values=list(pattern_counts.values()),
            hole=0.58,
            template="plotly_dark",
            color_discrete_sequence=[_TERTIARY, _PRIMARY, _ON_SURFACE_VAR, _ERROR, "#87ceeb", "#dda0dd"],
        )
        fig_pie.update_layout(
            height=440,
            margin=dict(l=24, r=200, t=52, b=32),
            paper_bgcolor="rgba(15, 25, 48, 0.6)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                font=dict(size=15),
                orientation="v",
                yanchor="middle",
                y=0.5,
                x=1.02,
                xanchor="left",
            ),
            title=dict(
                text="Insight mix",
                font=dict(size=20, color=_ON_SURFACE, family="Manrope, sans-serif"),
                x=0,
                xanchor="left",
            ),
            font=dict(family="Inter, system-ui, sans-serif", size=16, color=_ON_SURFACE_VAR),
        )

    if fig_pie is not None:
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False}, key=f"hist_prev_pie_{key_suffix}")
    else:
        st.caption("No patterns to chart.")

def _render_overview_metrics_optional(df: pd.DataFrame | None, n_insights: int):
    """Four equal metric cards: AI Insight count, then dataset shape."""
    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1:
        _metric_card("auto_awesome", "tertiary", "AI Insight", str(n_insights), img_icon="icon_insight.png")
    with m2:
        _metric_card("grid_view", "primary", "Rows", f"{len(df):,}" if df is not None else "—", img_icon="icon_csv.png")
    with m3:
        _metric_card("view_column", "tertiary", "Columns", str(len(df.columns)) if df is not None else "—", img_icon="icon_database.png")
    with m4:
        nc = len(df.select_dtypes(include="number").columns) if df is not None else 0
        _metric_card("functions", "dim", "Numeric Features", str(nc) if df is not None else "—", img_icon="icon_chart.png")


# ───────────────────────────────────────────────────────────────────────────
# LLM helpers (unchanged)
# ───────────────────────────────────────────────────────────────────────────
def _generate_llm_description(llm: BaseLLMClient, insight: dict, base_explanation: str) -> str:
    breakdown = insight.get("breakdown", "")
    measure = insight.get("measure", "")
    pattern = insight.get("pattern", "")
    subspace = insight.get("subspace") or []
    filters_desc = ", ".join(f"{c}={v}" for c, v in subspace) if subspace else "overall data"
    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []
    preview_rows = [f"- {breakdown} = {labels[i]} \u2192 {measure} = {values[i]}" for i in range(min(5, len(labels)))]
    prompt = f"""You are a data analyst explaining insights to a non-technical business user.

Insight:
- Pattern: {pattern}
- Breakdown: {breakdown}
- Measure: {measure}
- Segment: {filters_desc}

Sample data:
{chr(10).join(preview_rows) or "No numeric sample available."}

Base description:
\"\"\"{base_explanation}\"\"\"

Rewrite clearly and concisely in 3-4 bullets:
- Focus on the key takeaway and business meaning.
- Highlight top/bottom groups or trends.
- Keep language simple.""".strip()

    try:
        text = llm.complete(prompt, temperature=0.6, max_tokens=512)
        if not text:
            return base_explanation
        lowered = text.lower()
        if "[insight]" in lowered or "reason:" in lowered or "question:" in lowered:
            return base_explanation
        return text
    except Exception:
        return base_explanation


def _insight_expl_cache_key(ins: dict, use_llm: bool) -> str:
    """Stable key for Rich LLM explanation cache (pagination / fragment reruns)."""
    mock = bool(st.session_state.get("use_mock_llm", False))
    parts = [
        "1" if use_llm else "0",
        "1" if mock else "0",
        str(ins.get("pattern", "")),
        str(ins.get("question", "")),
        str(ins.get("breakdown", "")),
        str(ins.get("measure", "")),
        str(ins.get("subspace", "")),
        str(ins.get("view_labels", "")),
        str(ins.get("view_values", "")),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8", errors="replace")).hexdigest()[:48]


def _get_llm_description_cached(
    llm: BaseLLMClient, ins: dict, base_expl: str, use_llm: bool,
) -> str:
    if not use_llm:
        return base_expl
    if "insight_expl_cache" not in st.session_state:
        st.session_state.insight_expl_cache = {}
    ck = _insight_expl_cache_key(ins, use_llm)
    cache: dict = st.session_state.insight_expl_cache
    if ck in cache:
        return cache[ck]
    text = _generate_llm_description(llm, ins, base_expl)
    cache[ck] = text
    return text


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _deduplicate_cards(cards: List[InsightCard]) -> List[InsightCard]:
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
    pattern = (insight.get("pattern") or "").lower()
    breakdown = insight.get("breakdown", "group")
    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []
    if not labels or not values:
        return "Continue monitoring data to confirm this insight and prioritize the highest-impact segments."
    pairs = list(zip(labels, values))
    top_label, top_value = max(pairs, key=lambda x: x[1])
    low_label, low_value = min(pairs, key=lambda x: x[1])
    if "trend" in pattern:
        return (f"Set up time-based alerts for {breakdown}. If the trend declines, investigate the most recent period "
                f"and run targeted experiments over 1-2 cycles.")
    if "attribution" in pattern:
        return (f"{top_label} is the top contributor ({top_value:,.2f}). Protect this segment (retention, inventory), "
                f"and build growth plans for the remaining groups.")
    if "outstanding" in pattern:
        return (f"{top_label} stands out significantly. Determine whether this is an opportunity or a dependency risk. "
                f"Also investigate why {low_label} is low ({low_value:,.2f}).")
    return (f"Prioritize action on {top_label} (highest value), then plan improvements for "
            f"{low_label} to balance performance across {breakdown}.")


_DARK_PALETTE = [
    "#a3a6ff", "#8387ff", "#c6fff3", "#48e5d0", "#ff6e84",
    "#d73357", "#c7d5ed", "#65fde6", "#9396ff", "#54eed8",
    "#6063ee", "#a70138", "#dee5ff", "#ffa07a", "#87ceeb",
    "#dda0dd", "#98fb98", "#f0e68c", "#ff69b4", "#00ced1",
]


def _downsample_trend_series(labels: list, values: list, measure: str) -> tuple[list, list]:
    """
    Aggregate dense daily (or finer) trend data to month/week buckets so the line is readable.
    Does not change pipeline scores; display-only.
    """
    if len(labels) != len(values) or len(labels) < 2:
        return labels, values

    agg_name, _ = parse_measure(measure or "MEAN(x)")
    ts = pd.to_datetime(pd.Series(labels, dtype=object), errors="coerce")
    if ts.isna().mean() > 0.35:
        return labels, values

    v = pd.to_numeric(pd.Series(values), errors="coerce")
    df = pd.DataFrame({"t": ts, "v": v}).dropna(subset=["t", "v"])
    if len(df) < 2:
        return labels, values

    df["t"] = df["t"].dt.normalize()

    if agg_name in ("sum", "count"):
        day = df.groupby("t", sort=True)["v"].sum()
    elif agg_name == "mean":
        day = df.groupby("t", sort=True)["v"].mean()
    elif agg_name == "min":
        day = df.groupby("t", sort=True)["v"].min()
    elif agg_name == "max":
        day = df.groupby("t", sort=True)["v"].max()
    else:
        day = df.groupby("t", sort=True)["v"].mean()

    span_days = int((day.index.max() - day.index.min()).days)
    n = len(day)

    # Already sparse enough for labels to stay legible
    if n <= 16 and span_days <= 48:
        out_labels = [idx.strftime("%d/%m/%y") for idx in day.index]
        return out_labels, [float(x) for x in day.tolist()]

    if span_days > 700 and n > 40:
        rule = "QE"
    elif span_days > 50 or n > 28:
        rule = "MS"
    elif n > 22:
        rule = "W-MON"
    else:
        out_labels = [idx.strftime("%d/%m/%y") for idx in day.index]
        return out_labels, [float(x) for x in day.tolist()]

    rs = day.resample(rule)
    if agg_name in ("sum", "count"):
        g = rs.sum()
    elif agg_name == "mean":
        g = rs.mean()
    elif agg_name == "min":
        g = rs.min()
    elif agg_name == "max":
        g = rs.max()
    else:
        g = rs.mean()
    g = g.dropna()
    if len(g) < 2:
        out_labels = [idx.strftime("%d/%m/%y") for idx in day.index]
        return out_labels, [float(x) for x in day.tolist()]

    if rule == "QE":
        out_labels = [idx.strftime("%b %Y") for idx in g.index]
    else:
        out_labels = [idx.strftime("%d/%m/%y") for idx in g.index]
    return out_labels, [float(x) for x in g.tolist()]


def _make_chart(insight: dict):
    labels = insight.get("view_labels") or []
    values = insight.get("view_values") or []
    breakdown = insight.get("breakdown", "")
    measure = insight.get("measure", "")
    pattern = (insight.get("pattern") or "").lower()
    if not labels or not values or len(labels) != len(values):
        return None
    if "trend" in pattern:
        labels, values = _downsample_trend_series(list(labels), list(values), measure)
    df_chart = pd.DataFrame({breakdown or "Category": labels, measure or "Value": values})
    cat_col = breakdown or "Category"
    val_col = measure or "Value"

    if "trend" in pattern:
        fig = px.line(df_chart, x=cat_col, y=val_col, markers=True, template="plotly_dark")
    elif "attribution" in pattern:
        n_pie = len(labels)
        abs_vals = [abs(v) for v in values]
        sorted_idx = sorted(range(n_pie), key=lambda i: -abs_vals[i])
        pie_colors = [_DARK_PALETTE[i % len(_DARK_PALETTE)] for i in range(n_pie)]
        if n_pie >= 1:
            pie_colors[sorted_idx[0]] = _TERTIARY
        if n_pie >= 2:
            pie_colors[sorted_idx[1]] = _PRIMARY
        fig = px.pie(
            df_chart,
            names=cat_col,
            values=val_col,
            template="plotly_dark",
            hole=0,
            color_discrete_sequence=pie_colors,
        )
    else:
        fig = px.bar(df_chart, x=cat_col, y=val_col, template="plotly_dark")

    y_tickformat = None
    if values and "attribution" not in pattern:
        vmax = max(abs(float(v)) for v in values)
        if vmax >= 1_000_000:
            y_tickformat = ".2s"
        elif vmax >= 10_000:
            y_tickformat = ",.0f"

    if "attribution" in pattern:
        fig.update_traces(
            marker=dict(line=dict(color=_SURFACE_MID, width=1)),
            textinfo="label+percent",
            textposition="inside",
            insidetextorientation="auto",
        )
        fig.update_layout(
            height=380,
            margin=dict(l=16, r=120, t=44, b=16),
            paper_bgcolor=_SURFACE_MID,
            plot_bgcolor=_SURFACE_MID,
            font=dict(family="Inter, system-ui, sans-serif", size=15, color=_ON_SURFACE_VAR),
            title=dict(
                text="Attribution",
                font=dict(size=16, color=_ON_SURFACE, family="Manrope, sans-serif"),
                x=0.02,
                xanchor="left",
            ),
            dragmode=False,
            showlegend=True,
            legend=dict(
                font=dict(size=13),
                orientation="v",
                yanchor="middle",
                y=0.5,
                x=1.02,
                xanchor="left",
            ),
        )
        return fig

    fig.update_layout(
        height=380, margin=dict(l=16, r=16, t=44, b=16),
        plot_bgcolor=_SURFACE_MID, paper_bgcolor=_SURFACE_MID,
        font=dict(family="Inter, system-ui, sans-serif", size=15, color=_ON_SURFACE_VAR),
        xaxis=dict(title=dict(text=breakdown or "", font=dict(size=14, color=_ON_SURFACE_VAR)),
                    gridcolor=_SURFACE_HIGH, linecolor=_OUTLINE_VAR, tickangle=-35, tickfont=dict(size=14),
                    nticks=14, automargin=True),
        yaxis=dict(title=dict(text=measure or "", font=dict(size=14, color=_ON_SURFACE_VAR)),
                    gridcolor=_SURFACE_HIGH, linecolor=_OUTLINE_VAR, zerolinecolor=_OUTLINE_VAR, tickfont=dict(size=14),
                    tickformat=y_tickformat if y_tickformat else None),
        title=dict(text=f"{pattern.title() if pattern else 'View'}",
                   font=dict(size=16, color=_ON_SURFACE, family="Manrope, sans-serif"), x=0.02, xanchor="left"),
        dragmode=False, showlegend=False,
    )
    if "trend" in pattern:
        fig.update_traces(
            line=dict(color=_TERTIARY, width=2.5),
            marker=dict(size=9, color=_TERTIARY, line=dict(width=1.5, color="#ffffff")),
        )
    else:
        n = len(labels)
        abs_vals = [abs(v) for v in values]
        sorted_idx = sorted(range(n), key=lambda i: -abs_vals[i])
        bar_colors = [_DARK_PALETTE[i % len(_DARK_PALETTE)] for i in range(n)]
        if n >= 2:
            bar_colors[sorted_idx[0]] = _TERTIARY
            bar_colors[sorted_idx[1]] = _PRIMARY
        fig.update_traces(marker_color=bar_colors, marker_line=dict(color=_SURFACE_MID, width=1))
    return fig


# ───────────────────────────────────────────────────────────────────────────
# Pagination & results
# ───────────────────────────────────────────────────────────────────────────
_INSIGHTS_PER_PAGE = 5
_TABLE_ROWS_PER_PAGE = 20


def _pager(key: str, total: int, per_page: int):
    total_pages = max(1, (total + per_page - 1) // per_page)
    if key not in st.session_state:
        st.session_state[key] = 0
    page = max(0, min(st.session_state[key], total_pages - 1))
    st.session_state[key] = page
    start = page * per_page
    end = min(start + per_page, total)
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("Previous", key=f"{key}_prev", disabled=page == 0, use_container_width=True):
            st.session_state[key] = page - 1
    with col_info:
        st.markdown(f'<p class="cl-pager-info">Page {page + 1} of {total_pages} &middot; {total} total</p>', unsafe_allow_html=True)
    with col_next:
        if st.button("Next", key=f"{key}_next", disabled=page >= total_pages - 1, use_container_width=True):
            st.session_state[key] = page + 1
    return start, end


def _canonical_pattern(pattern: str) -> str:
    """Map stored pattern strings to one of ISGEN PATTERNS, or Other."""
    from quis.isgen.models import (
        ATTRIBUTION,
        DISTRIBUTION_DIFFERENCE,
        OUTSTANDING_VALUE,
        PATTERNS,
        TREND,
    )

    raw = (pattern or "").strip()
    if not raw:
        return "Other"
    low = raw.lower().replace("_", " ")
    for p in PATTERNS:
        if p.lower() == low:
            return p
    if "distribution" in low:
        return DISTRIBUTION_DIFFERENCE
    if "outstanding" in low:
        return OUTSTANDING_VALUE
    if "attribution" in low:
        return ATTRIBUTION
    if "trend" in low:
        return TREND
    return "Other"


def _group_insights_by_pattern(
    summaries: list[dict],
) -> tuple[dict[str, list[tuple[int, dict]]], list[tuple[int, dict]]]:
    from quis.isgen.models import PATTERNS

    buckets: dict[str, list[tuple[int, dict]]] = {p: [] for p in PATTERNS}
    other: list[tuple[int, dict]] = []
    for idx, item in enumerate(summaries):
        ins = item.get("insight") or {}
        cp = _canonical_pattern(ins.get("pattern", ""))
        if cp in buckets:
            buckets[cp].append((idx, item))
        else:
            other.append((idx, item))
    return buckets, other


def _render_generated_question_insight_body(
    reason: str,
    breakdown: str,
    measure: str,
    em: str,
) -> None:
    """Expanded content under a candidate question: Why · narrative and Breakdown / Measure."""
    rs = (reason or "").strip() or em
    bd = (breakdown or "").strip() or em
    ms = (measure or "").strip() or em
    st.markdown(
        f"""<div class="cl-q-insight">
            <p class="cl-q-insight-why">
                <span class="cl-q-insight-why-keyword">Why</span><span class="cl-q-insight-why-sep"> · </span><span class="cl-q-insight-why-text">{html.escape(rs)}</span>
            </p>
            <div class="cl-q-insight-meta">
                <span class="cl-q-insight-meta-k">Breakdown</span>
                <span class="cl-q-insight-meta-v">{html.escape(bd)}</span>
                <span class="cl-q-insight-meta-mid"> · </span>
                <span class="cl-q-insight-meta-k">Measure</span>
                <span class="cl-q-insight-meta-v">{html.escape(ms)}</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_one_insight_card(
    item: dict,
    orig_idx: int,
    llm_client,
    use_llm_explanations: bool,
    plot_key_prefix: str,
    accent_idx: int = 0,
):
    _accents = ["primary", "tertiary", "dim"]
    ins = item.get("insight") or {}
    base_expl = item.get("explanation", "")
    pattern = ins.get("pattern", "")
    question = item.get("question", "")
    why_reason = ins.get("reason", "") or ""
    breakdown = ins.get("breakdown", "") or ""
    measure = ins.get("measure", "") or ""
    description = _get_llm_description_cached(llm_client, ins, base_expl, use_llm_explanations)
    recommendation = _build_recommendation(ins)
    chart = _make_chart(ins)
    accent = _accents[accent_idx % len(_accents)]
    plot_key = f"{plot_key_prefix}_{orig_idx}"
    _em = "\u2014"

    try:
        insight_stack = st.container(border=True)
    except TypeError:
        insight_stack = st.container()
    with insight_stack:
        st.markdown(
            f"""<div class="cl-insight-card-head cl-insight-card-head--{accent}">
            <p class="cl-insight-pattern">{html.escape((pattern or "Insight").upper())}</p>
        </div>""",
            unsafe_allow_html=True,
        )
        with st.expander(question or "Untitled insight", expanded=False):
            _render_generated_question_insight_body(why_reason, breakdown, measure, _em)

        col_chart, col_text = st.columns([1.15, 1], gap="large")
        with col_chart:
            if chart is not None:
                try:
                    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False}, key=plot_key)
                except TypeError:
                    st.plotly_chart(chart, config={"displayModeBar": False}, key=plot_key)
            else:
                st.caption("Chart not available for this insight.")
        with col_text:
            st.markdown('<p class="cl-label">Summary</p>', unsafe_allow_html=True)
            if description:
                st.markdown(description)
            else:
                st.caption(_em)
            st.markdown('<p class="cl-label" style="margin-top:1rem;">Recommendation</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="cl-reco">{html.escape(recommendation)}</div>', unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)


def _render_insights_section_core(
    insight_summaries: list[dict],
    llm_client,
    use_llm_explanations: bool,
    pager_base: str,
    plot_key_prefix: str,
):
    from quis.isgen.models import PATTERNS

    with st.spinner("Loading charts and summaries…"):
        buckets, other = _group_insights_by_pattern(insight_summaries)
        tabs = st.tabs(list(PATTERNS))
        for tab, pat in zip(tabs, PATTERNS):
            with tab:
                bucket = buckets[pat]
                if not bucket:
                    st.caption("No insights of this type.")
                    continue
                pk = f"{pager_base}_{pat.replace(' ', '_')}"
                i_start, i_end = _pager(pk, len(bucket), _INSIGHTS_PER_PAGE)
                for local_i in range(i_start, i_end):
                    orig_idx, item = bucket[local_i]
                    _render_one_insight_card(
                        item,
                        orig_idx,
                        llm_client,
                        use_llm_explanations,
                        plot_key_prefix,
                        accent_idx=local_i,
                    )
        if other:
            with st.expander(f"Uncategorized patterns ({len(other)})", expanded=False):
                pk = f"{pager_base}_Other"
                o_start, o_end = _pager(pk, len(other), _INSIGHTS_PER_PAGE)
                for local_i in range(o_start, o_end):
                    orig_idx, item = other[local_i]
                    _render_one_insight_card(
                        item,
                        orig_idx,
                        llm_client,
                        use_llm_explanations,
                        plot_key_prefix,
                        accent_idx=local_i,
                    )


_fragment_fn = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None)
if _fragment_fn is not None:
    _render_insights_section_core = _fragment_fn(_render_insights_section_core)


def _render_insights_section(
    insight_summaries: list[dict],
    llm_client,
    use_llm_explanations: bool,
    pager_base: str,
    plot_key_prefix: str,
):
    _render_insights_section_core(
        insight_summaries,
        llm_client,
        use_llm_explanations,
        pager_base,
        plot_key_prefix,
    )


def _render_overview_metrics(df: pd.DataFrame, n_insights: int):
    """Four equal metric cards: AI Insight, Rows, Columns, Numeric Features."""
    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1:
        _metric_card("auto_awesome", "tertiary", "AI Insight", str(n_insights), img_icon="icon_insight.png")
    with m2:
        _metric_card("grid_view", "primary", "Rows", f"{len(df):,}", img_icon="icon_csv.png")
    with m3:
        _metric_card("view_column", "tertiary", "Columns", str(len(df.columns)), img_icon="icon_database.png")
    with m4:
        num_cols = len(df.select_dtypes(include="number").columns)
        _metric_card("functions", "dim", "Numeric Features", str(num_cols), img_icon="icon_chart.png")


def _render_results(df, _cards, insight_summaries, llm_client, use_llm_explanations, threshold_scale):
    st.markdown(
        '<div class="cl-report-metrics-spacer" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    _render_overview_metrics(df, len(insight_summaries) if insight_summaries else 0)

    _section("Dataset Overview", icon="analytics", img_icon="icon_chart.png")
    c1, c2 = st.columns([1.55, 1])
    with c1:
        try:
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)
        except TypeError:
            st.dataframe(df.head(50), hide_index=True)
    with c2:
        st.markdown('<p class="cl-label">Column Types</p>', unsafe_allow_html=True)
        try:
            st.dataframe(pd.DataFrame({"Column": df.columns, "Dtype": df.dtypes.astype(str)}),
                         use_container_width=True, hide_index=True)
        except TypeError:
            st.dataframe(pd.DataFrame({"Column": df.columns, "Dtype": df.dtypes.astype(str)}), hide_index=True)

    _section("Insights", "Visualizations, narrative, and recommended actions.", icon="insights", img_icon="icon_insight.png")
    if not insight_summaries:
        st.info("No insights passed the current threshold. Lower **Insight strictness** in Settings.")
        return
    _render_insights_section(
        insight_summaries,
        llm_client,
        use_llm_explanations,
        pager_base="i_page",
        plot_key_prefix="insight_plot",
    )


# ───────────────────────────────────────────────────────────────────────────
# History helpers
# ───────────────────────────────────────────────────────────────────────────
def _load_csv_file(path: str) -> pd.DataFrame | None:
    """Prefer cached reader for large files / History tab."""
    return _cached_load_csv(path)


def _discover_history() -> list[dict]:
    root = os.path.dirname(os.path.abspath(__file__))
    return list(_cached_discover_history(root))


def _render_history_insights(
    insight_summaries: list[dict],
    llm_client,
    use_llm_explanations: bool,
    pager_key: str = "hist_i_page",
):
    if not insight_summaries:
        st.info("No insights in this analysis.")
        return
    _render_insights_section(
        insight_summaries,
        llm_client,
        use_llm_explanations,
        pager_base=pager_key,
        plot_key_prefix=f"{pager_key}_plot",
    )


# ───────────────────────────────────────────────────────────────────────────
# Main app
# ───────────────────────────────────────────────────────────────────────────
def run_app():
    _style_app()
    _topbar()
    _neuron_corner_decorations()

    _defaults = {
        "pipeline_cards": None,
        "pipeline_insights": None,
        "processed_file": None,
        "use_mock_llm": not bool(os.getenv("OPENAI_API_KEY")),
        "max_cards": 8,
        "num_iterations": 2,
        "threshold_scale": 0.7,
        "llm_explanations": True,
    }
    for k, v in _defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if "insight_expl_cache" not in st.session_state:
        st.session_state.insight_expl_cache = {}

    llm_client = _init_llm_client()

    tab_home, tab_history, tab_settings = st.tabs(["Home", "History", "Settings"])

    # ==================================================================
    # HOME TAB
    # ==================================================================
    with tab_home:
        cached_cards = st.session_state.pipeline_cards
        cached_insights = st.session_state.pipeline_insights

        # -- Hero: two columns --
        hero_left, hero_right = st.columns([1.1, 1], gap="large")
        with hero_left:
            neural_img = _icon_img("icon_neural.png", height=80, extra_style="position:absolute;top:8px;right:12px;opacity:0.18;")
            st.markdown(
                f"""<div class="cl-hero" style="position:relative;overflow:hidden;">
                    {neural_img}
                    <p class="cl-hero-title">AI\u2014Powered Dataset Analysis</p>
                    <p class="cl-hero-sub">
                        Upload CSV files and let AI automatically generate
                        in-depth EDA reports and business insights in seconds.
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )

            fname = st.session_state.get("processed_file")
            if fname:
                st.markdown(
                    f"""<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">
                        <span class="ai-chip--primary ai-chip">
                            <span class="material-symbols-outlined" style="font-size:16px;">description</span>
                            {html.escape(fname)}
                        </span>
                        <span class="ai-chip--dim ai-chip">
                            <span class="material-symbols-outlined" style="font-size:16px;">schedule</span>
                            Current session
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )

            up_col, gen_col = st.columns(2)
            with up_col:
                uploaded = st.file_uploader(
                    "Upload New Dataset", type=["csv"],
                    help="Semicolon-delimited CSV and European number formats are auto-detected.",
                    label_visibility="collapsed",
                )
            with gen_col:
                generate_btn = st.button(
                    "\u2728 Generate New Report",
                    use_container_width=True,
                    type="primary",
                    disabled=uploaded is None and st.session_state.pipeline_cards is None,
                )

        with hero_right:
            df_for_preview = None
            if uploaded is not None:
                try:
                    df_for_preview = pd.read_csv(uploaded)
                except Exception:
                    uploaded.seek(0)
                    try:
                        df_for_preview = pd.read_csv(uploaded, sep=None, engine="python")
                    except Exception:
                        uploaded.seek(0)
                        df_for_preview = pd.read_csv(uploaded, sep=";", engine="python")
                uploaded.seek(0)
                first_line = uploaded.readline().decode("utf-8", errors="ignore")
                detected_sep = ";" if first_line.count(";") > first_line.count(",") else ","
                df_for_preview = _clean_dataframe(df_for_preview, sep=detected_sep)
                uploaded.seek(0)
            _insight_preview(df_for_preview, cached_insights)

        # -- Process uploaded file --
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
            except Exception:
                uploaded.seek(0)
                try:
                    df = pd.read_csv(uploaded, sep=None, engine="python")
                except Exception:
                    uploaded.seek(0)
                    df = pd.read_csv(uploaded, sep=";", engine="python")
            uploaded.seek(0)
            first_line = uploaded.readline().decode("utf-8", errors="ignore")
            detected_sep = ";" if first_line.count(";") > first_line.count(",") else ","
            df = _clean_dataframe(df, sep=detected_sep)

            if df.empty:
                st.warning("The uploaded CSV appears to be empty.")
            else:
                if st.session_state.processed_file != uploaded.name:
                    st.session_state.pipeline_cards = None
                    st.session_state.pipeline_insights = None

                if generate_btn:
                    table_schema = schema_from_dataframe(df, table_name=os.path.splitext(uploaded.name)[0] or "Table")
                    max_cards = st.session_state.max_cards
                    iters = st.session_state.num_iterations
                    ts = st.session_state.threshold_scale

                    with st.spinner("Agent is generating insight questions..."):
                        qcfg = QUGENConfig(num_iterations=iters, num_samples_per_iteration=1, num_questions_per_prompt=max_cards)
                        qugen = QUGENPipeline(config=qcfg, llm_client=llm_client)
                        cards: List[InsightCard] = qugen.run(table_schema, df=df)
                        cards = _deduplicate_cards(cards)

                    if cards:
                        with st.spinner("Scoring insights and generating visualizations..."):
                            isgen_cfg = ISGENConfig(plot_dir=None, max_insights_per_question=3, threshold_scale=ts)
                            isgen = ISGENPipeline(config=isgen_cfg, llm_client=llm_client)
                            insight_summaries = isgen.run(df, cards=[c.to_dict() for c in cards])
                        st.session_state.pipeline_cards = cards
                        st.session_state.pipeline_insights = insight_summaries
                        st.session_state.processed_file = uploaded.name
                    else:
                        st.warning("No Insight Cards generated. Try a different dataset or adjust settings.")

                cached_cards = st.session_state.pipeline_cards
                cached_insights = st.session_state.pipeline_insights
                if cached_cards is not None and cached_insights is not None:
                    use_llm_expl = st.session_state.llm_explanations
                    _render_results(df, cached_cards, cached_insights, llm_client, use_llm_expl, st.session_state.threshold_scale)
        elif uploaded is None and st.session_state.pipeline_cards is None:
            csv_icon = _icon_img("icon_csv.png", height=64, extra_style="display:block;margin:0 auto 0.75rem;opacity:0.7;")
            st.markdown(
                f"""<div class="cl-empty">
                    {csv_icon}
                    <strong>No file yet.</strong><br/>
                    <span style="font-size:1.08rem;">Upload a CSV to initialize the AI agent.</span>
                </div>""",
                unsafe_allow_html=True,
            )

    # ==================================================================
    # HISTORY TAB (reference layout: hero + preview + metrics + table)
    # ==================================================================
    with tab_history:
        history = _discover_history()
        if not history:
            db_icon = _icon_img("icon_database.png", height=64, extra_style="display:block;margin:0 auto 0.75rem;opacity:0.7;")
            st.markdown(
                f"""<div class="cl-empty">
                    {db_icon}
                    <strong>No previous analyses found.</strong><br/>
                    <span style="font-size:1.08rem;">Run the pipeline from Home or via CLI to generate results.</span>
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            labels = [h["label"] for h in history]
            preferred = (os.getenv("SUN_SMART_DEFAULT_HISTORY") or "").strip().lower()
            default_idx = 0
            if preferred:
                for i, h in enumerate(history):
                    base = os.path.basename(h["insights_path"]).lower()
                    slug = base.replace("insights_summary_", "").replace(".json", "")
                    if slug == preferred or preferred in slug:
                        default_idx = i
                        break
            else:
                for i, h in enumerate(history):
                    if "insights_summary_adidas_cleaned.json" in h["insights_path"].replace("\\", "/"):
                        default_idx = i
                        break
            selected_idx = st.selectbox(
                "Saved analysis",
                range(len(labels)),
                format_func=lambda i: labels[i],
                index=min(default_idx, max(len(labels) - 1, 0)),
                key="history_dataset_select",
            )

            entry = history[selected_idx]
            insight_data = _cached_load_insights_json(entry["insights_path"]) or []

            hist_df: pd.DataFrame | None = None
            if entry["csv_path"]:
                hist_df = _cached_load_csv(entry["csv_path"])
                if hist_df is not None and hist_df.empty:
                    hist_df = None

            last_lbl = _file_mtime_label(entry["insights_path"])
            ds_name = html.escape(entry["label"])

            h_left, h_right = st.columns([1.05, 1], gap="large")
            with h_left:
                st.markdown(
                    f"""<div class="cl-history-wrap" style="pointer-events:auto;">
                        <div class="cl-hero" style="padding:0;">
                            <p class="cl-hero-title" style="font-size:clamp(1.6rem, 4vw, 2.1rem);">AI\u2014Powered Dataset Analysis</p>
                            <p class="cl-hero-sub" style="margin-bottom:1rem;">
                                Open a saved report to review EDA metrics, questions, and AI insights from a previous run.
                            </p>
                            <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0;">
                                <span class="ai-chip--primary ai-chip">
                                    <span class="material-symbols-outlined" style="font-size:16px;">description</span>
                                    {ds_name}
                                </span>
                                <span class="ai-chip--dim ai-chip">
                                    <span class="material-symbols-outlined" style="font-size:16px;">schedule</span>
                                    Last analyzed: {html.escape(last_lbl)}
                                </span>
                            </div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Upload New Dataset", use_container_width=True, type="primary", key="hist_btn_upload"):
                        st.info("Switch to the **Home** tab and use **Upload New Dataset** to load a CSV.")
                with b2:
                    if st.button("\u2728 Generate New Report", use_container_width=True, key="hist_btn_report"):
                        st.info("Switch to the **Home** tab, upload data, then click **Generate New Report**.")

            with h_right:
                _render_history_preview_charts(insight_data, key_suffix=str(selected_idx))

            _render_overview_metrics_optional(hist_df, len(insight_data))

            _section("Dataset Overview", icon="analytics", img_icon="icon_chart.png")
            if hist_df is not None:
                t_start, t_end = _pager(f"hist_tbl_{selected_idx}", len(hist_df), _TABLE_ROWS_PER_PAGE)
                chunk = hist_df.iloc[t_start:t_end]
                try:
                    st.dataframe(chunk, use_container_width=True, hide_index=True)
                except TypeError:
                    st.dataframe(chunk, hide_index=True)
            else:
                st.caption("No CSV found for this analysis — metrics above show insight counts only.")

            _section("Insights", f"{len(insight_data)} insights from this analysis.", icon="insights", img_icon="icon_insight.png")
            _render_history_insights(
                insight_data,
                llm_client,
                st.session_state.llm_explanations,
                pager_key=f"hist_i_{selected_idx}",
            )

    # ==================================================================
    # SETTINGS TAB
    # ==================================================================
    with tab_settings:
        st.markdown(
            """<div class="cl-hero" style="padding:1rem 0;">
                <p class="cl-hero-title" style="font-size:1.8rem;">Settings</p>
                <p class="cl-hero-sub" style="margin-bottom:0;">
                    Configure the AI agent behaviour, LLM parameters, and insight thresholds.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        _section("LLM Configuration", icon="smart_toy")
        st.markdown('<div class="cl-settings-card">', unsafe_allow_html=True)
        has_key = bool(os.getenv("OPENAI_API_KEY"))
        st.toggle("Mock LLM (no API key needed)", key="use_mock_llm",
                   help="Uses a built-in mock model instead of calling OpenAI." + ("" if has_key else " **No API key detected.**"))
        if not st.session_state.use_mock_llm and not has_key:
            st.warning("OPENAI_API_KEY not set — mock mode recommended.")
        st.toggle("Rich LLM explanations", key="llm_explanations", help="If off, show template explanations only.")
        st.markdown('</div>', unsafe_allow_html=True)

        _section("Pipeline Parameters", icon="tune")
        st.markdown('<div class="cl-settings-card">', unsafe_allow_html=True)
        st.slider("Questions per LLM call", min_value=4, max_value=12, step=2, key="max_cards")
        st.slider("LLM iterations", min_value=1, max_value=5, key="num_iterations")
        st.slider("Insight strictness", min_value=0.3, max_value=1.0, step=0.1, key="threshold_scale",
                   help="Lower = more insights kept (relaxed thresholds).")
        st.markdown('</div>', unsafe_allow_html=True)

        _section("About", icon="info")
        st.markdown(
            """<div class="cl-settings-card">
                <p class="cl-label">Platform</p>
                <p style="margin:0;color:var(--on-surface);font-size:1.1rem;">Sun Smart Report &mdash; Agentic EDA</p>
                <p class="cl-label" style="margin-top:0.75rem;">Encryption</p>
                <p style="margin:0;color:var(--on-surface-var);font-size:1.05rem;">AES-256 Cloud Standard</p>
            </div>""",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    run_app()
