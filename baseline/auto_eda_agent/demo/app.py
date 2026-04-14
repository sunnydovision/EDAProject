import streamlit as st
import pandas as pd
import json
import os
import toml
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AutoEDA Agent Demo",
    page_icon="📊",
    layout="wide"
)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "Adidas_cleaned.csv"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_FILE = BASE_DIR.parent.parent / ".streamlit" / "config.toml"

# Read config for custom colors
config = toml.load(CONFIG_FILE)
PROMPT_JSON = config.get("prompt_colors", {}).get("json_highlight", "#60a5fa")

# Use theme colors from Streamlit config
PROMPT_BG = st.config.get_option("theme.secondaryBackgroundColor")
PROMPT_TEXT = st.config.get_option("theme.textColor")
PROMPT_HIGHLIGHT = st.config.get_option("theme.primaryColor")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, sep=';')

@st.cache_data
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Main app
st.title("🤖 AutoEDA Agent - Demo Exploratory Data Analysis")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Điều hướng")
page = st.sidebar.radio(
    "Chọn phần để xem:",
    ["Tổng quan", "Input Dataset", "5 Bước Phân Tích", "Kết Quả Insights"]
)

if page == "Tổng quan":
    st.header("📋 Tổng quan AutoEDA Agent")
    st.markdown("""
    ### Giới thiệu
    AutoEDA Agent là hệ thống phân tích dữ liệu tự động sử dụng LLM như các chuyên gia phân tích.
    
    ### 5 Bước Phân Tích
    1. **Data Profiling** - Phân tích ý nghĩa ngữ nghĩa của các cột dữ liệu
    2. **Quality Analysis** - Đánh giá chất lượng dữ liệu và các vấn đề
    3. **Statistical Analysis** - Phân tích thống kê và tương quan
    4. **Pattern Discovery** - Khám phá các mẫu trong dữ liệu
    5. **Insight Extraction** - Trích xuất các insight có giá trị kinh doanh
    """)

elif page == "Input Dataset":
    st.cache_data.clear()  # Clear cache to force reload
    st.header("📁 Input Dataset")
    st.markdown("### Dataset: Adidas_cleaned.csv")
    
    df = load_data()
    st.write(f"**Kích thước:** {df.shape[0]} dòng × {df.shape[1]} cột")
    
    st.markdown("### 5 dòng đầu tiên:")
    st.dataframe(df.head(), use_container_width=True)
    
    st.markdown("### Tổng quan các cột (Kaggle style):")
    
    # Create Kaggle-style overview table
    overview_data = []
    for col in df.columns:
        col_dtype = str(df[col].dtype)
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        # Get sample values (up to 5 unique values)
        sample_values = df[col].dropna().unique()[:5]
        sample_str = ', '.join(map(str, sample_values))
        if len(sample_str) > 50:
            sample_str = sample_str[:50] + '...'
        
        overview_data.append({
            'Cột': col,
            'Kiểu dữ liệu': col_dtype,
            'Giá trị thiếu': f'{missing_count} ({missing_pct:.2f}%)',
            'Giá trị duy nhất': unique_count,
            'Sample values': sample_str
        })
    
    overview_df = pd.DataFrame(overview_data)
    st.dataframe(overview_df, use_container_width=True, hide_index=True)

elif page == "5 Bước Phân Tích":
    st.header("🔬 5 Bước Phân Tích")
    
    # Step 1
    with st.expander("Bước 1: Data Profiling Agent", expanded=False):
        st.markdown("### Quy trình")
        
        st.markdown("**1.1 Initial Exploration**")
        st.markdown("- Input: `df` (DataFrame)")
        st.markdown("- Process: Code phân tích data structure, tính toán số lượng columns, rows, dtypes")
        st.markdown("- Output: `{numerical_cols, categorical_cols, dtypes, missing_counts}`")
        
        st.markdown("**1.2 Semantic Analysis**")
        st.markdown("- Input: `column_samples` (sample values của từng cột)")
        st.markdown("- Process: Gọi LLM để phân tích ý nghĩa từng cột")
        
        @st.dialog("Prompt - Semantic Analysis")
        def semantic_dialog():
            st.markdown("### System Prompt")
            st.markdown(f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; color: {PROMPT_TEXT};">
You are an expert data analyst. Your job is to infer the semantic meaning and classification of dataset columns from their names and sample values.
</div>
""", unsafe_allow_html=True)
            prompt_mode = st.radio("Chế độ hiển thị:", ["Template", "Actual (dữ liệu thực tế)"], key="step1_2_prompt_mode")
            if prompt_mode == "Template":
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Analyze the following dataset columns and infer their semantic meaning.

Dataset: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{n_rows}} rows × {{n_columns}} columns</span>

Column samples (name, dtype, and unique values):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{column_samples_json}}</span>

For EACH column, return:
- semantic_meaning: what this column represents in business terms
- data_type_class: one of ID | Categorical | Numerical | Temporal | Text
- importance: one of high | medium | low
- potential_issues: any quality concerns visible from the sample values
</div>
"""
                st.html(html_content)
            else:
                df = load_data()
                column_samples = {}
                for col in df.columns[:30]:
                    unique_vals = df[col].dropna().unique()
                    if len(unique_vals) <= 20:
                        column_samples[col] = {
                            'unique_count': len(unique_vals),
                            'sample_values': [str(v) for v in unique_vals[:20]],
                            'dtype': str(df[col].dtype)
                        }
                    else:
                        column_samples[col] = {
                            'unique_count': len(unique_vals),
                            'sample_values': [str(v) for v in unique_vals[:10]],
                            'dtype': str(df[col].dtype)
                        }
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Analyze the following dataset columns and infer their semantic meaning.

Dataset: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{len(df)} rows × {len(df.columns)} columns</span>

Column samples (name, dtype, and unique values):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(column_samples, indent=2, ensure_ascii=False)}</span>

For EACH column, return:
- semantic_meaning: what this column represents in business terms
- data_type_class: one of ID | Categorical | Numerical | Temporal | Text
- importance: one of high | medium | low
- potential_issues: any quality concerns visible from the sample values
</div>
"""
                st.html(html_content)
        
        if st.button("Xem Prompt", key="step1_2_prompt"):
            semantic_dialog()
        st.markdown("- Output: `{semantic_meaning, data_type_class, importance, potential_issues}`")
        
        st.markdown("**1.3 Comprehensive Profiling**")
        st.markdown("- Input: Kết quả 1.1 + 1.2")
        st.markdown("- Process: Code combine và compute detailed statistics")
        st.markdown("- Output: `profile.json` đầy đủ thông tin cột")
        
        st.markdown("**1.4 Generate Summary Report**")
        st.markdown("- Input: `profile.json`")
        st.markdown("- Process: Code generate markdown summary")
        st.markdown("- Output: `summary.md`")
        
        st.markdown("### Output")
        profile = load_json(OUTPUT_DIR / "step1_profiling" / "profile.json")
        st.json(profile["columns"])
    
    # Step 2
    with st.expander("Bước 2: Quality Analysis Agent", expanded=False):
        st.markdown("### Quy trình")
        
        st.markdown("**2.1 Compute Quality Metrics**")
        st.markdown("- Input: `df` + `id_columns` từ Step 1")
        st.markdown("- Process: Code tính toán missing values, outliers, duplicates")
        st.markdown("- Output: `{missing_values, outliers, duplicates, total_issues}`")
        
        st.markdown("**2.2 Expert Quality Assessment**")
        st.markdown("- Input: `quality_metrics` + `importance_by_column`")
        st.markdown("- Process: Gọi LLM để interpret và prioritize issues")
        
        @st.dialog("Prompt - Expert Quality Assessment")
        def quality_dialog():
            st.markdown("### System Prompt")
            st.markdown(f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; color: {PROMPT_TEXT};">
You are a data quality expert. Your job is to assess data quality issues and prioritize them based on their business impact.
</div>
""", unsafe_allow_html=True)
            prompt_mode = st.radio("Chế độ hiển thị:", ["Template", "Actual (dữ liệu thực tế)"], key="step2_2_prompt_mode")
            if prompt_mode == "Template":
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Assess the data quality of the following dataset.

Column importance levels (from profiling):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{importance_by_column_json}}</span>

Computed quality metrics:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{quality_metrics_json}}</span>

For each issue found, provide:
1. A description of the issue
2. Severity: high | medium | low
3. Business impact: how this issue affects downstream analysis
4. Recommended action
</div>
"""
                st.html(html_content)
            else:
                profile = load_json(OUTPUT_DIR / "step1_profiling" / "profile.json")
                quality = load_json(OUTPUT_DIR / "step2_quality" / "quality_report.json")
                
                importance_by_column = {}
                id_columns = []
                for col, info in profile["columns"].items():
                    importance_by_column[col] = info["importance"]
                    if info["data_type_class"] == "ID":
                        id_columns.append(col)
                
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Assess the data quality of the following dataset.

Column importance levels (from profiling):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(importance_by_column, indent=2, ensure_ascii=False)}</span>

Note: ID columns excluded from outlier analysis: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{', '.join(id_columns) if id_columns else 'None'}</span>

Computed quality metrics:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(quality['metrics'], indent=2, ensure_ascii=False)}</span>

For each issue found, provide:
1. A description of the issue
2. Severity: high | medium | low
3. Business impact: how this issue affects downstream analysis
4. Recommended action
</div>
"""
                st.html(html_content)
        
        if st.button("Xem Prompt", key="step2_2_prompt"):
            quality_dialog()
        st.markdown("- Output: `{critical_issues, overall_quality_score, priority_actions}`")
        
        st.markdown("**2.3 Combine Metrics & Assessment**")
        st.markdown("- Input: Kết quả 2.1 + 2.2")
        st.markdown("- Process: Code combine metrics và assessment")
        st.markdown("- Output: `quality_report.json` với metrics + assessment")
        
        st.markdown("### Output")
        quality = load_json(OUTPUT_DIR / "step2_quality" / "quality_report.json")
        st.json(quality["assessment"])
    
    # Step 3
    with st.expander("Bước 3: Statistical Analysis Agent", expanded=False):
        st.markdown("### Quy trình")
        
        st.markdown("**3.1 Compute Comprehensive Statistics**")
        st.markdown("- Input: `df` + `id_columns` từ Step 1")
        st.markdown("- Process: Code tính toán descriptive stats, distributions, correlations")
        st.markdown("- Output: `{numerical_stats, categorical_stats, correlations}`")
        
        st.markdown("**3.2 Statistical Interpretation**")
        st.markdown("- Input: `statistics` + `semantic_meanings` + `quality_score`")
        st.markdown("- Process: Gọi LLM để interpret findings trong business context")
        
        @st.dialog("Prompt - Statistical Interpretation")
        def stats_dialog():
            st.markdown("### System Prompt")
            st.markdown(f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; color: {PROMPT_TEXT};">
You are an expert statistician. Your job is to interpret statistical findings in the context of the dataset's business meaning and known data quality issues.
</div>
""", unsafe_allow_html=True)
            prompt_mode = st.radio("Chế độ hiển thị:", ["Template", "Actual (dữ liệu thực tế)"], key="step3_2_prompt_mode")
            if prompt_mode == "Template":
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Interpret the following statistical findings for this dataset.

Column semantic meanings (from Step 1):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{semantic_meanings_json}}</span>

Data quality context (from Step 2):
- Overall quality score: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{quality_score}}</span>
- Columns with significant outliers: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{outlier_columns}}</span>

Computed statistics:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{statistics_json}}</span>

Provide:
1. distribution_patterns: interpret the shape of each numerical distribution
2. strong_correlations: for each pair with |r| > 0.7, explain the relationship
3. key_findings: top 3 most important statistical observations
4. statistical_anomalies: unusual patterns that warrant further investigation
5. recommendations: suggested follow-up analyses
</div>
"""
                st.html(html_content)
            else:
                profile = load_json(OUTPUT_DIR / "step1_profiling" / "profile.json")
                quality = load_json(OUTPUT_DIR / "step2_quality" / "quality_report.json")
                stats = load_json(OUTPUT_DIR / "step3_statistics" / "statistics.json")
                
                semantic_meanings = {}
                for col, info in profile["columns"].items():
                    semantic_meanings[col] = info["semantic_meaning"]
                
                outlier_columns = list(quality["metrics"]["outliers"].keys())
                
                stats_data = {
                    "numerical_stats": stats["statistics"]["numerical_stats"],
                    "strong_correlations": stats["statistics"]["correlations"]["strong_correlations"]
                }
                
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Interpret the following statistical findings for this dataset.

Column semantic meanings (from Step 1):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}</span>

Data quality context (from Step 2):
- Overall quality score: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{quality['assessment']['overall_quality_score']}</span>
- Columns with significant outliers: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{', '.join(outlier_columns) if outlier_columns else 'None'}</span>

Computed statistics:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(stats_data, indent=2, ensure_ascii=False)}</span>

Provide:
1. distribution_patterns: interpret the shape of each numerical distribution
2. strong_correlations: for each pair with |r| > 0.7, explain the relationship
3. key_findings: top 3 most important statistical observations
4. statistical_anomalies: unusual patterns that warrant further investigation
5. recommendations: suggested follow-up analyses
</div>
"""
                st.html(html_content)
        
        if st.button("Xem Prompt", key="step3_2_prompt"):
            stats_dialog()
        st.markdown("- Output: `{distribution_patterns, strong_correlations, key_findings, recommendations}`")
        
        st.markdown("**3.3 Combine Statistics & Interpretation**")
        st.markdown("- Input: Kết quả 3.1 + 3.2")
        st.markdown("- Process: Code combine statistics và interpretation")
        st.markdown("- Output: `statistics.json` với statistics + interpretation")
        
        st.markdown("### Output")
        stats = load_json(OUTPUT_DIR / "step3_statistics" / "statistics.json")
        st.json(stats["interpretation"])
    
    # Step 4
    with st.expander("Bước 4: Pattern Discovery Agent", expanded=False):
        st.markdown("### Quy trình")
        
        st.markdown("**4.1 Pre-compute Aggregations**")
        st.markdown("- Input: `df` + `temporal_columns`")
        st.markdown("- Process: Code tính toán monthly, correlation, group aggregations")
        st.markdown("- Output: `{monthly_aggregations, group_aggregations, correlation_matrix}`")
        
        st.markdown("**4.2 Multi-prompt Analysis**")
        st.markdown("- Input: `aggregations` + `semantic_meanings`")
        st.markdown("- Process: 4 LLM calls cho temporal, correlation, grouping, anomaly patterns")
        
        @st.dialog("Prompt - Temporal Patterns")
        def temporal_dialog():
            st.markdown("### System Prompt")
            st.markdown(f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; color: {PROMPT_TEXT};">
You are a pattern recognition expert. Your job is to identify concrete, evidence-backed patterns in data.
</div>
""", unsafe_allow_html=True)
            prompt_mode = st.radio("Chế độ hiển thị:", ["Template", "Actual (dữ liệu thực tế)"], key="step4_2_prompt_mode")
            if prompt_mode == "Template":
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Discover temporal patterns in this dataset.

Focus: time-based trends, seasonality, growth or decline over time.

Computed monthly aggregations:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{{monthly_aggregations_json}}</span>

For each pattern found:
- Cite specific numbers from the monthly aggregations
- State which months or periods show the pattern
- Assess pattern strength: strong | moderate | weak
</div>
"""
                st.html(html_content)
            else:
                profile = load_json(OUTPUT_DIR / "step1_profiling" / "profile.json")
                quality = load_json(OUTPUT_DIR / "step2_quality" / "quality_report.json")
                
                semantic_meanings = {}
                for col, info in profile["columns"].items():
                    semantic_meanings[col] = info["semantic_meaning"]
                
                df = load_data()
                monthly_agg = {}
                if 'Invoice Date' in df.columns:
                    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
                    monthly_agg = df.groupby(df['Invoice Date'].dt.to_period('M')).agg({
                        'Total Sales': 'sum',
                        'Operating Profit': 'sum',
                        'Units Sold': 'sum'
                    }).head(12).to_dict('index')
                else:
                    monthly_agg = {}
                
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Discover temporal patterns in this dataset.

Focus: time-based trends, seasonality, growth or decline over time.

Column semantic meanings:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}</span>

Data quality score: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{quality['assessment']['overall_quality_score']}</span>

Computed monthly aggregations (first 12 months):
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(monthly_agg, indent=2, ensure_ascii=False)}</span>

For each pattern found:
- Cite specific numbers from the monthly aggregations
- State which months or periods show the pattern
- Assess pattern strength: strong | moderate | weak
</div>
"""
                st.html(html_content)
        
        if st.button("Xem Prompt (Temporal)", key="step4_2_prompt"):
            temporal_dialog()
        st.markdown("- Output: `{patterns}` cho từng category")
        
        st.markdown("**4.3 Consolidate Patterns**")
        st.markdown("- Input: Kết quả 4.2 từ 4 pattern types")
        st.markdown("- Process: Code combine tất cả patterns")
        st.markdown("- Output: `patterns.json` với tất cả patterns")
        
        st.markdown("### Output")
        patterns = load_json(OUTPUT_DIR / "step4_patterns" / "patterns.json")
        st.write(f"**Tổng số patterns:** {patterns['total_patterns']}")
        st.write(f"**Các loại patterns:** {', '.join(patterns['pattern_categories'])}")
        
        for category, pattern_list in patterns["patterns_by_category"].items():
            with st.expander(f"{category} ({len(pattern_list)} patterns)", expanded=False):
                for i, pattern in enumerate(pattern_list[:3], 1):  # Show first 3 patterns per category
                    st.markdown(f"**{i}. {pattern['pattern_name']}**")
                    st.markdown(f"- *Description:* {pattern['description'][:200]}...")
                    st.markdown(f"- *Strength:* {pattern['strength']}")
                    st.markdown(f"- *Variables:* {', '.join(pattern['variables_involved'])}")
    
    # Step 5
    with st.expander("Bước 5: Insight Extraction Agent", expanded=False):
        st.markdown("### Quy trình")
        
        st.markdown("**5.1 Load Prior Analysis**")
        st.markdown("- Input: `profile.json`, `quality_report.json`, `statistics.json`, `patterns.json` từ steps 1-4")
        st.markdown("- Process: Code load và extract context từ 4 files")
        st.markdown("- Output: `semantic_meanings`, `quality_score`, `correlations`, `patterns`")
        
        st.markdown("**5.2 Multi-batch Extraction**")
        st.markdown("- Input: Context từ Step 1-4 + `available_columns`")
        st.markdown("- Process: 5 LLM calls cho 5 insight types (TREND, OUTLIER, CORRELATION, DISTRIBUTION, PATTERN)")
        
        @st.dialog("Prompt - Insight Extraction")
        def insight_dialog():
            st.markdown("### System Prompt")
            st.markdown(f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; color: {PROMPT_TEXT};">
You are an expert data analyst extracting insights for a business audience.
Each insight must be specific, supported by evidence from the prior analysis, and expressed with concrete numbers.
</div>
""", unsafe_allow_html=True)
            prompt_mode = st.radio("Chế độ hiển thị:", ["Template", "Actual (dữ liệu thực tế)"], key="step5_2_prompt_mode")
            if prompt_mode == "Template":
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Extract insights of the following type(s): <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{insight_types}}</span>

AVAILABLE COLUMNS — use ONLY these exact names:
- Numerical: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{numerical_columns}}</span>
- Categorical: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{categorical_columns}}</span>

Context from prior analysis steps:
Step 1 — Column meanings: <span style="color: {PROMPT_JSON}; font-weight: bold;">{{semantic_meanings_json}}</span>
Step 2 — Data quality: Quality score: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{quality_score}}</span>
Step 3 — Statistical findings: <span style="color: {PROMPT_JSON}; font-weight: bold;">{{strong_correlations_json}}</span>
Step 4 — Discovered patterns: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{{relevant_patterns}}</span>

For each insight:
- Write a specific, concrete title
- Include actual numbers in the description
- Reference which step provided the evidence
- List the columns involved
- Choose an appropriate chart type: line | bar | scatter | histogram | box
</div>
"""
                st.html(html_content)
            else:
                profile = load_json(OUTPUT_DIR / "step1_profiling" / "profile.json")
                quality = load_json(OUTPUT_DIR / "step2_quality" / "quality_report.json")
                stats = load_json(OUTPUT_DIR / "step3_statistics" / "statistics.json")
                patterns = load_json(OUTPUT_DIR / "step4_patterns" / "patterns.json")
                
                numerical_cols = []
                categorical_cols = []
                for col, info in profile["columns"].items():
                    if info["data_type_class"] in ["Numerical"]:
                        numerical_cols.append(col)
                    elif info["data_type_class"] in ["Categorical", "Temporal"]:
                        categorical_cols.append(col)
                
                semantic_meanings = {}
                for col, info in profile["columns"].items():
                    semantic_meanings[col] = info["semantic_meaning"]
                
                strong_correlations = stats["statistics"]["correlations"]["strong_correlations"]
                relevant_patterns = patterns["total_patterns"]
                
                html_content = f"""
<div style="background-color: {PROMPT_BG}; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; font-size: 11px; max-height: 300px; overflow-y: auto; color: {PROMPT_TEXT};">
Extract insights of the following type(s): TREND

AVAILABLE COLUMNS — use ONLY these exact names:
- Numerical: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{', '.join(numerical_cols)}</span>
- Categorical: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{', '.join(categorical_cols)}</span>

Context from prior analysis steps:
Step 1 — Column meanings:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}</span>

Step 2 — Data quality: Quality score: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{quality['assessment']['overall_quality_score']}</span>
Step 3 — Statistical findings:
<span style="color: {PROMPT_JSON}; font-weight: bold;">{json.dumps(strong_correlations, indent=2, ensure_ascii=False)}</span>
Step 4 — Discovered patterns: <span style="color: {PROMPT_HIGHLIGHT}; font-weight: bold;">{relevant_patterns}</span> patterns found

For each insight:
- Write a specific, concrete title
- Include actual numbers in the description
- Reference which step provided the evidence
- List the columns involved
- Choose an appropriate chart type: line | bar | scatter | histogram | box
</div>
"""
                st.html(html_content)
        
        if st.button("Xem Prompt", key="step5_2_prompt"):
            insight_dialog()
        st.markdown("- Output: `{insights}` với title, description, variables, chart_type, subspace")
        
        st.markdown("**5.3 Post-processing**")
        st.markdown("- Input: `insights` từ LLM")
        st.markdown("- Process: Code compute view_labels từ data, validate insights")
        st.markdown("- Output: `insights.json` với view_labels được compute từ data")
        
        st.markdown("### Output")
        insights = load_json(OUTPUT_DIR / "step5_insights" / "insights.json")
        st.write(f"**Tổng số insights:** {len(insights)}")
        
        # Show first 5 insights
        for i, insight in enumerate(insights[:5], 1):
            st.markdown(f"**{i}. {insight['title']}**")
            st.markdown(f"- *Type:* {insight['insight_type']}")
            st.markdown(f"- *Description:* {insight['description'][:150]}...")
            st.markdown(f"- *Variables:* {', '.join(insight['variables'])}")
            st.markdown("---")

elif page == "Kết Quả Insights":
    st.header("💡 Kết Quả Insights")
    
    insights = load_json(OUTPUT_DIR / "step5_insights" / "insights.json")
    with open(OUTPUT_DIR / "summary" / "summary.txt", 'r', encoding='utf-8') as f:
        summary = f.read()
    
    # Summary
    st.markdown("### Tổng quan")
    st.text(summary)
    
    # Insights by type
    st.markdown("### Insights theo loại")
    type_counts = {}
    for insight in insights:
        itype = insight['insight_type']
        type_counts[itype] = type_counts.get(itype, 0) + 1
    
    for itype, count in sorted(type_counts.items()):
        st.markdown(f"- **{itype}**: {count} insights")
    
    # Browse insights
    st.markdown("### Xem chi tiết insights")
    selected_idx = st.selectbox(
        "Chọn insight để xem:",
        range(len(insights)),
        format_func=lambda x: f"{x}: {insights[x]['title']}"
    )
    
    insight = insights[selected_idx]
    st.markdown(f"### {insight['title']}")
    st.markdown(f"**Type:** {insight['insight_type']}")
    st.markdown(f"**Description:** {insight['description']}")
    st.markdown(f"**Variables:** {', '.join(insight['variables'])}")
    st.markdown(f"**Chart Type:** {insight['chart_type']}")
    st.markdown(f"**Evidence Source:** {insight['data_evidence']['source_step']}")
    
    # Show chart if exists
    chart_path = OUTPUT_DIR / "step5_insights" / f"insight_{selected_idx:03d}.png"
    if chart_path.exists():
        st.image(str(chart_path), caption=f"Chart: {insight['title']}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Thông tin")
st.sidebar.markdown(f"**Dataset:** Adidas_cleaned.csv")
st.sidebar.markdown(f"**Output directory:** {OUTPUT_DIR}")
