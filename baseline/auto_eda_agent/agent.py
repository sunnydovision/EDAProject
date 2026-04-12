"""
AutoEDA Agentic Baseline

True agentic workflow where each step:
1. Acts as a specialist agent for that step
2. Iteratively refines: write code → execute → evaluate → refine → repeat
3. Uses multi-prompt strategy for comprehensive analysis
4. Verbose logging of all actions (like Cascade)
5. Self-reflects and decides when to stop

Each step is an autonomous agent that doesn't stop until satisfied with results.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Tuple
from openai import OpenAI
import os
from dotenv import load_dotenv
import warnings
import scorer
import re
import time

warnings.filterwarnings('ignore')
load_dotenv()

# Token usage tracking (similar to QUIS)
_SESSION_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "requests": 0,
}
_LAST_MODEL_USED = None


def _add_usage_from_response(resp) -> None:
    """Extract and accumulate token usage from OpenAI response (similar to QUIS)"""
    global _LAST_MODEL_USED
    u = getattr(resp, "usage", None)
    if u is None:
        return
    inp = getattr(u, "prompt_tokens", None)
    out = getattr(u, "completion_tokens", None)
    tot = getattr(u, "total_tokens", None)
    inp_i = int(inp or 0)
    out_i = int(out or 0)
    if tot is None:
        tot_i = inp_i + out_i
    else:
        tot_i = int(tot)
    _SESSION_USAGE["input_tokens"] += inp_i
    _SESSION_USAGE["output_tokens"] += out_i
    _SESSION_USAGE["total_tokens"] += tot_i
    _SESSION_USAGE["requests"] += 1


def get_session_usage() -> Dict[str, Any]:
    """Return copy of accumulated token usage for this process"""
    return {**_SESSION_USAGE}


def _clean_dataframe_like_quis(df: pd.DataFrame, csv_path: str = None) -> pd.DataFrame:
    """
    Clean dataframe using same logic as QUIS (from run_isgen.py lines 71-82).
    This ensures fair comparison between QUIS and Baseline.
    """
    df = df.copy()
    
    # Detect separator from CSV file (same as QUIS)
    sep = ","
    if csv_path:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
            sep = ";" if first_line.count(";") > first_line.count(",") else ","
        except:
            pass
    
    # Clean currency ($), percentage (%), and European number formatting so columns become numeric
    for col in df.columns:
        # Check for object, str, or StringDtype
        dtype_str = str(df[col].dtype).lower()
        is_string_col = df[col].dtype == object or dtype_str in ['str', 'string'] or 'string' in dtype_str
        if is_string_col:
            sample = df[col].dropna().head(20).astype(str).str.strip()
            # Detect columns that look numeric: digits with optional $, %, dots, commas
            numeric_like = sample.str.match(r"^\$?\s*[\d.,]+\s*%?$")
            if numeric_like.sum() >= len(sample) * 0.8:
                cleaned = df[col].astype(str).str.replace(r"[$%]", "", regex=True).str.strip()
                if sep == ";":
                    # EU format: dot=thousands, comma=decimal
                    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                else:
                    # US format: comma=thousands, dot=decimal
                    cleaned = cleaned.str.replace(",", "", regex=False)
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted
    
    return df


class AgenticAutoEDA:
    """
    Agentic AutoEDA - Each step is an autonomous specialist agent.
    
    Each agent iteratively refines its analysis until satisfied.
    """
    
    def __init__(self, data_path: str, model: str = None, api_key: str = None):
        """Initialize Agentic AutoEDA"""
        self.data_path = data_path
        self.model = model or os.getenv('MODEL', 'gpt-4o-mini')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
        # Load data once
        print("📂 Loading dataset...")
        self.df = pd.read_csv(data_path, sep=None, engine='python')
        print(f"✓ Loaded raw: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        
        # Apply QUIS-style cleaning for fair comparison
        print("🧹 Applying QUIS-style data cleaning...")
        self.df = _clean_dataframe_like_quis(self.df, data_path)
        print(f"✓ Cleaned: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        
        # Show column changes
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        print(f"📊 Numeric columns after cleaning: {len(numeric_cols)}")
        print(f"   Sample: {list(numeric_cols)[:5]}...\n")
        
        # Step outputs
        self.step_outputs = {}
        
        # Setup plotting
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def run_autoeda(self, output_dir: str = 'output', max_iterations: int = 3, skip_step5: bool = False) -> Dict[str, Any]:
        """
        Run complete agentic AutoEDA workflow.
        
        Each step runs as autonomous agent with iterative refinement.
        
        Args:
            output_dir: Directory for output files
            max_iterations: Max iterations per step (default: 3)
            skip_step5: Skip step 5 (insight extraction) if True (default: False)
        """
        # Start timing
        start_time = time.time()
        print(f"⏱️  Starting AutoEDA workflow at {time.strftime('%H:%M:%S')}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Data Profiling Agent
        print("\n" + "="*70)
        print("🤖 STEP 1: DATA PROFILING AGENT")
        print("="*70)
        step1_start = time.time()
        step1_dir = f"{output_dir}/step1_profiling"
        os.makedirs(step1_dir, exist_ok=True)
        self.step_outputs['step1'] = self._run_profiling_agent(step1_dir, max_iterations)
        step1_time = time.time() - step1_start
        print(f"⏱️  Step 1 completed in {step1_time:.1f}s")
        
        # Step 2: Quality Analysis Agent
        print("\n" + "="*70)
        print("🤖 STEP 2: QUALITY ANALYSIS AGENT")
        print("="*70)
        step2_start = time.time()
        step2_dir = f"{output_dir}/step2_quality"
        os.makedirs(step2_dir, exist_ok=True)
        self.step_outputs['step2'] = self._run_quality_agent(step2_dir, max_iterations)
        step2_time = time.time() - step2_start
        print(f"⏱️  Step 2 completed in {step2_time:.1f}s")
        
        # Step 3: Statistical Analysis Agent
        print("\n" + "="*70)
        print("🤖 STEP 3: STATISTICAL ANALYSIS AGENT")
        print("="*70)
        step3_start = time.time()
        step3_dir = f"{output_dir}/step3_statistics"
        os.makedirs(step3_dir, exist_ok=True)
        self.step_outputs['step3'] = self._run_statistics_agent(step3_dir, max_iterations)
        step3_time = time.time() - step3_start
        print(f"⏱️  Step 3 completed in {step3_time:.1f}s")
        
        # Step 4: Pattern Discovery Agent
        print("\n" + "="*70)
        print("🤖 STEP 4: PATTERN DISCOVERY AGENT")
        print("="*70)
        step4_start = time.time()
        step4_dir = f"{output_dir}/step4_patterns"
        os.makedirs(step4_dir, exist_ok=True)
        self.step_outputs['step4'] = self._run_pattern_agent(step4_dir, max_iterations)
        step4_time = time.time() - step4_start
        print(f"⏱️  Step 4 completed in {step4_time:.1f}s")
        
        # Step 5: Insight Extraction Agent (optional)
        if not skip_step5:
            print("\n" + "="*70)
            print("🤖 STEP 5: INSIGHT EXTRACTION AGENT")
            print("="*70)
            step5_start = time.time()
            step5_dir = f"{output_dir}/step5_insights"
            os.makedirs(step5_dir, exist_ok=True)
            self.step_outputs['step5'] = self._run_insight_agent(step5_dir)
            self.step_outputs['step5_dir'] = step5_dir  # Store for converter
            step5_time = time.time() - step5_start
            print(f"⏱️  Step 5 completed in {step5_time:.1f}s")
        else:
            print("\n" + "="*70)
            print("⏭️  SKIPPING STEP 5: INSIGHT EXTRACTION")
            print("="*70)
            step5_time = 0
        
        # Generate summary
        print("\n" + "="*70)
        print("📋 GENERATING FINAL SUMMARY")
        print("="*70)
        summary_dir = f"{output_dir}/summary"
        os.makedirs(summary_dir, exist_ok=True)
        self._generate_summary(summary_dir)
        
        # Total time and final stats
        total_time = time.time() - start_time
        print(f"\n⏱️  Total AutoEDA workflow completed in {total_time:.1f}s")
        
        # Get token usage
        token_usage = get_session_usage()
        
        # Save timing info
        timing_info = {
            'total_time': total_time,
            'step_times': {
                'profiling': step1_time,
                'quality': step2_time,
                'statistics': step3_time,
                'patterns': step4_time,
                'insights': step5_time
            },
            'insights_generated': len(self.step_outputs.get('step5', [])),
            'throughput': len(self.step_outputs.get('step5', [])) / total_time if total_time > 0 else 0,
            'token_usage': token_usage
        }
        
        with open(f"{output_dir}/timing.json", 'w') as f:
            json.dump(timing_info, f, indent=2)
        
        # Save token usage to separate file (similar to QUIS)
        usage_output_path = os.getenv('BASELINE_USAGE_OUTPUT', f"{output_dir}/usage.json")
        with open(usage_output_path, 'w') as f:
            json.dump({**token_usage, 'model': self.model}, f, indent=2)
        
        print(f"📊 Generated {len(self.step_outputs.get('step5', []))} insights")
        print(f"⚡ Throughput: {timing_info['throughput']:.2f} insights/second")
        print(f"🔢 Token Usage: {token_usage['total_tokens']:,} total ({token_usage['input_tokens']:,} input + {token_usage['output_tokens']:,} output)")
        print(f"📝 API Requests: {token_usage['requests']}")
        print(f"💾 Timing info saved to {output_dir}/timing.json")
        print(f"💾 Token usage saved to {usage_output_path}")
        
        return self.step_outputs
    
    def _run_profiling_agent(self, output_dir: str, max_iterations: int) -> Dict[str, Any]:
        """
        Data Profiling Agent - Acts as expert data analyst.
        
        Deeply analyzes data:
        - Infers semantic meaning of columns
        - Detects data types and patterns
        - Samples values to understand content
        - Identifies relationships and hierarchies
        """
        print("\n🧠 Agent thinking: I need to deeply understand this dataset like an expert...")
        print("📝 Strategy: Explore → Infer semantics → Profile comprehensively\n")
        
        # Phase 1: Initial exploration
        print("📊 Phase 1: Initial Data Exploration")
        print("  ├─ 🔍 Loading and examining data structure...")
        
        initial_analysis = self._initial_data_exploration()
        
        print(f"  ├─ ✅ Found {len(self.df.columns)} columns, {len(self.df)} rows")
        print(f"  ├─ 📋 Column types: {len(initial_analysis['numerical_cols'])} numerical, {len(initial_analysis['categorical_cols'])} categorical")
        print(f"  └─ 💾 Saving initial findings...\n")
        
        # Phase 2: Deep semantic analysis
        print("📊 Phase 2: Semantic Analysis")
        print("  ├─ 🧠 Analyzing column meanings and relationships...")
        print("  ├─ 🔍 Sampling unique values to infer semantics...")
        print("  ├─ 📊 Detecting patterns and data types...")
        
        semantic_analysis = self._semantic_column_analysis(initial_analysis)
        
        print(f"  ├─ ✅ Analyzed semantic meaning of all columns")
        print(f"  └─ 💾 Saving semantic analysis...\n")
        
        # Phase 3: Comprehensive profiling
        print("📊 Phase 3: Comprehensive Profiling")
        print("  ├─ 📈 Computing detailed statistics...")
        print("  ├─ 🎯 Identifying key variables...")
        print("  ├─ 🔗 Detecting relationships...")
        
        comprehensive_profile = self._create_comprehensive_profile(
            initial_analysis, 
            semantic_analysis
        )
        
        # Save profile
        with open(f"{output_dir}/profile.json", 'w', encoding='utf-8') as f:
            json.dump(comprehensive_profile, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"  ├─ ✅ Profile complete")
        print(f"  └─ 💾 Saved: {output_dir}/profile.json\n")
        
        # Generate human-readable summary
        print("📊 Phase 4: Generating Summary Report")
        self._generate_profile_summary(comprehensive_profile, f"{output_dir}/summary.md")
        print(f"  └─ ✓ Summary saved: {output_dir}/summary.md\n")
        
        return comprehensive_profile
    
    def _initial_data_exploration(self) -> Dict[str, Any]:
        """Initial exploration of dataset structure"""
        
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            'shape': {'rows': len(self.df), 'columns': len(self.df.columns)},
            'columns': list(self.df.columns),
            'numerical_cols': numerical_cols,
            'categorical_cols': categorical_cols,
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'missing_counts': {col: int(self.df[col].isnull().sum()) for col in self.df.columns}
        }
    
    def _semantic_column_analysis(self, initial_analysis: Dict) -> Dict[str, Any]:
        """
        Deep semantic analysis - LLM infers meaning of each column.
        
        For each column:
        - Sample unique values
        - Infer semantic meaning
        - Classify data type
        - Assess importance
        - Identify potential issues
        """
        
        semantic_info = {}
        
        # Prepare column samples for LLM analysis
        column_samples = {}
        for col in self.df.columns[:30]:  # Analyze first 30 columns
            unique_vals = self.df[col].dropna().unique()
            
            if len(unique_vals) <= 20:
                # Show all unique values if few
                column_samples[col] = {
                    'unique_count': len(unique_vals),
                    'sample_values': [str(v) for v in unique_vals[:20]],
                    'dtype': str(self.df[col].dtype)
                }
            else:
                # Sample diverse values
                column_samples[col] = {
                    'unique_count': len(unique_vals),
                    'sample_values': [str(v) for v in unique_vals[:10]],
                    'dtype': str(self.df[col].dtype)
                }
        
        # Ask LLM to analyze semantics
        prompt = f"""You are an expert data analyst. Your job is to infer the semantic meaning and classification of dataset columns from their names and sample values.

Analyze the following dataset columns and infer their semantic meaning.

Dataset: {len(self.df)} rows × {len(self.df.columns)} columns

Column samples (name, dtype, and unique values):
{json.dumps(column_samples, indent=2, ensure_ascii=False)}

For EACH column, return:
- semantic_meaning: what this column represents in business terms (e.g., "gross revenue per transaction", "date of sale")
- data_type_class: one of ID | Categorical | Numerical | Temporal | Text
- importance: one of high | medium | low
- potential_issues: any quality concerns visible from the sample values (e.g., mixed formats, suspicious values, likely nulls)

Return a JSON object where each key is a column name:

{{
  "column_name": {{
    "semantic_meaning": "...",
    "data_type_class": "ID|Categorical|Numerical|Temporal|Text",
    "importance": "high|medium|low",
    "potential_issues": "..."
  }}
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst inferring semantic meaning from data samples."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=8000,
                response_format={"type": "json_object"}
            )
            _add_usage_from_response(response)
            
            semantic_info = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"  ⚠️  Semantic analysis error: {e}")
            semantic_info = {}
        
        return semantic_info
    
    def _create_comprehensive_profile(self, initial: Dict, semantic: Dict) -> Dict[str, Any]:
        """Create comprehensive profile combining structural and semantic analysis"""
        
        profile = {
            'dataset_overview': {
                'shape': initial['shape'],
                'total_columns': len(initial['columns']),
                'numerical_columns': len(initial['numerical_cols']),
                'categorical_columns': len(initial['categorical_cols'])
            },
            'columns': {}
        }
        
        # Profile each column
        for col in self.df.columns:
            col_profile = {
                'dtype': str(self.df[col].dtype),
                'missing_count': int(self.df[col].isnull().sum()),
                'missing_percentage': float(self.df[col].isnull().sum() / len(self.df) * 100)
            }
            
            # Add semantic info if available
            if col in semantic:
                col_profile['semantic_meaning'] = semantic[col].get('semantic_meaning', '')
                col_profile['data_type_class'] = semantic[col].get('data_type_class', '')
                col_profile['importance'] = semantic[col].get('importance', 'medium')
                col_profile['potential_issues'] = semantic[col].get('potential_issues', '')
            
            # Add statistics based on type
            if col in initial['numerical_cols']:
                col_profile['statistics'] = {
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'std': float(self.df[col].std())
                }
            elif col in initial['categorical_cols']:
                value_counts = self.df[col].value_counts()
                col_profile['unique_count'] = int(self.df[col].nunique())
                col_profile['top_values'] = {
                    str(k): int(v) for k, v in value_counts.head(10).items()
                }
            
            profile['columns'][col] = col_profile
        
        return profile
    
    def _generate_profile_summary(self, profile: Dict, output_path: str):
        """Generate human-readable markdown summary"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Data Profile Summary\n\n")
            
            f.write("## Dataset Overview\n\n")
            overview = profile['dataset_overview']
            f.write(f"- **Rows**: {overview['shape']['rows']:,}\n")
            f.write(f"- **Columns**: {overview['total_columns']}\n")
            f.write(f"  - Numerical: {overview['numerical_columns']}\n")
            f.write(f"  - Categorical: {overview['categorical_columns']}\n\n")
            
            f.write("## Key Columns\n\n")
            
            # Show high importance columns first
            high_importance = [
                (col, info) for col, info in profile['columns'].items()
                if info.get('importance') == 'high'
            ]
            
            if high_importance:
                f.write("### High Importance Columns\n\n")
                for col, info in high_importance[:10]:
                    f.write(f"**{col}**\n")
                    if 'semantic_meaning' in info:
                        f.write(f"- Meaning: {info['semantic_meaning']}\n")
                    if 'data_type_class' in info:
                        f.write(f"- Type: {info['data_type_class']}\n")
                    f.write(f"- Missing: {info['missing_percentage']:.1f}%\n\n")
            
            f.write("## Data Quality\n\n")
            missing_cols = [
                (col, info['missing_percentage']) 
                for col, info in profile['columns'].items()
                if info['missing_percentage'] > 0
            ]
            
            if missing_cols:
                f.write("Columns with missing values:\n\n")
                for col, pct in sorted(missing_cols, key=lambda x: x[1], reverse=True)[:10]:
                    f.write(f"- **{col}**: {pct:.1f}%\n")
            else:
                f.write("No missing values detected.\n")
    
    def _run_quality_agent(self, output_dir: str, max_iterations: int) -> Dict[str, Any]:
        """
        Quality Analysis Agent - Acts as data quality expert.
        
        Analyzes quality issues:
        - Missing values and patterns
        - Outliers and anomalies (excluding ID columns)
        - Inconsistencies and errors
        - Data integrity issues
        """
        print("\n🧠 Agent thinking: I need to thoroughly assess data quality like an expert...")
        print("📝 Strategy: Compute quality metrics → Analyze patterns → Identify issues\n")
        
        # Load profile.json to get ID columns and importance levels
        profile_path = f"{output_dir}/../step1_profiling/profile.json"
        profile = {}
        id_columns = []
        importance_by_column = {}
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            # Extract ID columns and importance levels
            for col_name, col_data in profile.get('columns', {}).items():
                if col_data.get('data_type_class') == 'ID':
                    id_columns.append(col_name)
                importance_by_column[col_name] = col_data.get('importance', 'medium')
            
            print(f"  ├─ 📋 Loaded profile: {len(id_columns)} ID columns identified")
            print(f"  ├─ 📋 Importance levels loaded for {len(importance_by_column)} columns\n")
        except Exception as e:
            print(f"  ⚠️  Could not load profile.json: {e}")
        
        # Phase 1: Compute quality metrics
        print("📊 Phase 1: Computing Quality Metrics")
        print("  ├─ 🔍 Analyzing missing values...")
        print("  ├─ 📊 Detecting outliers (excluding ID columns)...")
        print("  ├─ 🔎 Checking duplicates...")
        
        quality_metrics = self._compute_quality_metrics(id_columns)
        
        print(f"  ├─ ✅ Found {quality_metrics['total_issues']} quality issues")
        print(f"  └─ 💾 Saving metrics...\n")
        
        # Phase 2: LLM analyzes quality issues
        print("📊 Phase 2: Expert Quality Assessment")
        print("  ├─ 🧠 Interpreting quality metrics...")
        print("  ├─ 🔍 Identifying critical issues...")
        print("  ├─ 📋 Prioritizing problems...")
        
        quality_assessment = self._expert_quality_assessment(quality_metrics, importance_by_column, id_columns)
        
        print(f"  ├─ ✅ Quality assessment complete")
        print(f"  └─ 💾 Saving assessment...\n")
        
        # Combine metrics and assessment
        quality_report = {
            'metrics': quality_metrics,
            'assessment': quality_assessment,
            'summary': {
                'total_issues': quality_metrics['total_issues'],
                'critical_issues': len(quality_assessment.get('critical_issues', [])),
                'data_quality_score': quality_assessment.get('overall_quality_score', 0)
            }
        }
        
        # Save report
        with open(f"{output_dir}/quality_report.json", 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Quality report saved: {output_dir}/quality_report.json\n")
        
        # Generate summary
        self._generate_quality_summary(quality_report, f"{output_dir}/summary.md")
        print(f"✓ Summary saved: {output_dir}/summary.md\n")
        
        return quality_report
    
    def _compute_quality_metrics(self, id_columns: List[str] = None) -> Dict[str, Any]:
        """Compute quality metrics directly, excluding ID columns from outlier analysis"""
        
        if id_columns is None:
            id_columns = []
        
        metrics = {
            'missing_values': {},
            'outliers': {},
            'duplicates': int(self.df.duplicated().sum()),
            'total_issues': 0
        }
        
        # Missing values
        for col in self.df.columns:
            missing_count = int(self.df[col].isnull().sum())
            if missing_count > 0:
                metrics['missing_values'][col] = {
                    'count': missing_count,
                    'percentage': float(missing_count / len(self.df) * 100)
                }
        
        # Outliers (IQR method for numerical columns, excluding ID columns)
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            # Skip ID columns for outlier analysis
            if col in id_columns:
                continue
                
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_mask = (self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR))
            outlier_count = int(outlier_mask.sum())
            
            if outlier_count > 0:
                metrics['outliers'][col] = {
                    'count': outlier_count,
                    'percentage': float(outlier_count / len(self.df) * 100),
                    'lower_bound': float(Q1 - 1.5 * IQR),
                    'upper_bound': float(Q3 + 1.5 * IQR)
                }
        
        metrics['total_issues'] = len(metrics['missing_values']) + len(metrics['outliers']) + (1 if metrics['duplicates'] > 0 else 0)
        
        return metrics
    
    def _expert_quality_assessment(self, metrics: Dict, importance_by_column: Dict, id_columns: List[str]) -> Dict[str, Any]:
        """LLM acts as quality expert to assess issues with column importance weighting"""
        
        prompt = f"""You are a data quality expert. Your job is to assess data quality issues and prioritize them based on their business impact.

Assess the data quality of the following dataset.

Column importance levels (from profiling):
{json.dumps(importance_by_column, indent=2, ensure_ascii=False)}

Note: The following columns are identifier fields and have been excluded from outlier analysis:
{id_columns}

Computed quality metrics:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

For each issue found, provide:
1. A description of the issue
2. Severity: high | medium | low — weighted by the importance of the affected column
3. Business impact: how this issue affects downstream analysis
4. Recommended action

Also provide:
- overall_quality_score: integer 0–100 reflecting overall dataset reliability
- priority_actions: top 3 actions to address the most critical issues

Return JSON:

{{
  "critical_issues": [
    {{
      "issue": "...",
      "severity": "high|medium|low",
      "impact": "...",
      "recommendation": "..."
    }}
  ],
  "overall_quality_score": 0,
  "priority_actions": ["...", "...", "..."],
  "detailed_analysis": "..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data quality expert providing professional assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=4000,
                response_format={"type": "json_object"}
            )
            _add_usage_from_response(response)
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"  ⚠️  Quality assessment error: {e}")
            return {
                'critical_issues': [],
                'overall_quality_score': 50,
                'priority_actions': []
            }
    
    def _generate_quality_summary(self, report: Dict, output_path: str):
        """Generate quality summary markdown"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Data Quality Report\n\n")
            
            f.write("## Summary\n\n")
            summary = report['summary']
            f.write(f"- **Total Issues**: {summary['total_issues']}\n")
            f.write(f"- **Critical Issues**: {summary['critical_issues']}\n")
            f.write(f"- **Quality Score**: {summary['data_quality_score']}/100\n\n")
            
            f.write("## Missing Values\n\n")
            missing = report['metrics']['missing_values']
            if missing:
                for col, info in sorted(missing.items(), key=lambda x: x[1]['percentage'], reverse=True)[:10]:
                    f.write(f"- **{col}**: {info['percentage']:.1f}% ({info['count']} rows)\n")
            else:
                f.write("No missing values detected.\n")
            
            f.write("\n## Outliers\n\n")
            outliers = report['metrics']['outliers']
            if outliers:
                for col, info in sorted(outliers.items(), key=lambda x: x[1]['percentage'], reverse=True)[:10]:
                    f.write(f"- **{col}**: {info['percentage']:.1f}% ({info['count']} outliers)\n")
            else:
                f.write("No significant outliers detected.\n")
            
            f.write("\n## Critical Issues\n\n")
            critical = report['assessment'].get('critical_issues', [])
            if critical:
                for issue in critical[:5]:
                    f.write(f"### {issue.get('issue', 'Unknown')}\n")
                    f.write(f"- **Severity**: {issue.get('severity', 'unknown')}\n")
                    f.write(f"- **Impact**: {issue.get('impact', '')}\n")
                    f.write(f"- **Recommendation**: {issue.get('recommendation', '')}\n\n")
    
    def _run_statistics_agent(self, output_dir: str, max_iterations: int) -> Dict[str, Any]:
        """
        Statistical Analysis Agent - Acts as expert statistician.
        
        Computes and interprets:
        - Descriptive statistics
        - Distributions and normality
        - Correlations and relationships
        - Statistical significance
        """
        print("\n🧠 Agent thinking: I need to analyze statistics like an expert statistician...")
        print("📝 Strategy: Compute stats → Analyze distributions → Find correlations → Interpret\n")
        
        # Load profile.json and quality_report.json for context
        profile_path = f"{output_dir}/../step1_profiling/profile.json"
        quality_path = f"{output_dir}/../step2_quality/quality_report.json"
        
        semantic_meanings = {}
        id_columns = []
        quality_score = 0
        outlier_columns = []
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            # Extract semantic meanings and ID columns
            for col_name, col_data in profile.get('columns', {}).items():
                semantic_meanings[col_name] = col_data.get('semantic_meaning', '')
                if col_data.get('data_type_class') == 'ID':
                    id_columns.append(col_name)
            
            print(f"  ├─ 📋 Loaded profile: {len(semantic_meanings)} semantic meanings, {len(id_columns)} ID columns\n")
        except Exception as e:
            print(f"  ⚠️  Could not load profile.json: {e}\n")
        
        try:
            with open(quality_path, 'r', encoding='utf-8') as f:
                quality_report = json.load(f)
            
            quality_score = quality_report.get('summary', {}).get('data_quality_score', 0)
            outlier_columns = list(quality_report.get('metrics', {}).get('outliers', {}).keys())
            
            print(f"  ├─ 📋 Loaded quality report: score={quality_score}, {len(outlier_columns)} outlier columns\n")
        except Exception as e:
            print(f"  ⚠️  Could not load quality_report.json: {e}\n")
        
        # Phase 1: Compute comprehensive statistics
        print("📊 Phase 1: Computing Comprehensive Statistics")
        print("  ├─ 📈 Descriptive statistics...")
        print("  ├─ 📊 Distribution analysis...")
        print("  ├─ 🔗 Correlation analysis...")
        
        statistics = self._compute_comprehensive_statistics()
        
        print(f"  ├─ ✅ Computed statistics for {len(statistics['numerical_stats'])} numerical columns")
        print(f"  └─ 💾 Saving statistics...\n")
        
        # Phase 2: LLM interprets statistical findings
        print("📊 Phase 2: Statistical Interpretation")
        print("  ├─ 🧠 Interpreting distributions...")
        print("  ├─ 🔍 Analyzing correlations...")
        print("  ├─ 📋 Identifying statistical patterns...")
        
        interpretation = self._expert_statistical_interpretation(statistics, semantic_meanings, quality_score, outlier_columns, id_columns)
        
        print(f"  ├─ ✅ Statistical interpretation complete")
        print(f"  └─ 💾 Saving interpretation...\n")
        
        # Combine statistics and interpretation
        stats_report = {
            'statistics': statistics,
            'interpretation': interpretation,
            'summary': {
                'numerical_columns': len(statistics['numerical_stats']),
                'categorical_columns': len(statistics['categorical_stats']),
                'strong_correlations': len(interpretation.get('strong_correlations', [])),
                'key_findings': interpretation.get('key_findings', [])
            }
        }
        
        # Save report
        with open(f"{output_dir}/statistics.json", 'w', encoding='utf-8') as f:
            json.dump(stats_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Statistics saved: {output_dir}/statistics.json\n")
        
        # Generate summary
        self._generate_statistics_summary(stats_report, f"{output_dir}/summary.md")
        print(f"✓ Summary saved: {output_dir}/summary.md\n")
        
        return stats_report
    
    def _compute_comprehensive_statistics(self) -> Dict[str, Any]:
        """Compute comprehensive statistics directly"""
        
        stats = {
            'numerical_stats': {},
            'categorical_stats': {},
            'correlations': {}
        }
        
        # Numerical statistics
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            stats['numerical_stats'][col] = {
                'count': int(self.df[col].count()),
                'mean': float(self.df[col].mean()),
                'median': float(self.df[col].median()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                'max': float(self.df[col].max()),
                'q25': float(self.df[col].quantile(0.25)),
                'q75': float(self.df[col].quantile(0.75)),
                'skewness': float(self.df[col].skew()),
                'kurtosis': float(self.df[col].kurtosis())
            }
        
        # Categorical statistics
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:20]:  # Limit to first 20
            value_counts = self.df[col].value_counts()
            stats['categorical_stats'][col] = {
                'unique_count': int(self.df[col].nunique()),
                'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'distribution': {str(k): int(v) for k, v in value_counts.head(10).items()}
            }
        
        # Correlations
        if len(numerical_cols) > 1:
            corr_matrix = self.df[numerical_cols].corr()
            # Find strong correlations (>0.7 or <-0.7)
            strong_corrs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_corrs.append({
                            'var1': corr_matrix.columns[i],
                            'var2': corr_matrix.columns[j],
                            'correlation': float(corr_val)
                        })
            stats['correlations']['strong_correlations'] = strong_corrs
        
        return stats
    
    def _expert_statistical_interpretation(self, statistics: Dict, semantic_meanings: Dict, quality_score: int, outlier_columns: List[str], id_columns: List[str]) -> Dict[str, Any]:
        """LLM acts as statistician to interpret findings with context from prior steps"""
        
        prompt = f"""You are an expert statistician. Your job is to interpret statistical findings in the context of the dataset's business meaning and known data quality issues.

Interpret the following statistical findings for this dataset.

Column semantic meanings (from Step 1):
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

Data quality context (from Step 2):
- Overall quality score: {quality_score}
- Columns with significant outliers: {outlier_columns}
  When interpreting means and distributions for these columns, note that summary statistics may be influenced by outliers.
- Columns flagged as identifiers (exclude from statistical interpretation): {id_columns}

Computed statistics:
{json.dumps(statistics, indent=2, ensure_ascii=False)}

Provide:
1. distribution_patterns: interpret the shape of each numerical distribution (skewness, kurtosis, mean vs median gaps) in business terms
2. strong_correlations: for each pair with |r| > 0.7, explain what the relationship means and whether it is likely structural or behavioral
3. key_findings: top 3 most important statistical observations
4. statistical_anomalies: unusual patterns that warrant further investigation
5. recommendations: suggested follow-up analyses

Return JSON:

{{
  "distribution_patterns": "...",
  "strong_correlations": [
    {{
      "variables": "...",
      "interpretation": "...",
      "strength": "strong|moderate|weak"
    }}
  ],
  "key_findings": ["...", "...", "..."],
  "statistical_anomalies": ["...", "..."],
  "recommendations": ["...", "..."]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert statistician interpreting data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=4000,
                response_format={"type": "json_object"}
            )
            _add_usage_from_response(response)
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"  ⚠️  Statistical interpretation error: {e}")
            return {
                'distribution_patterns': '',
                'strong_correlations': [],
                'key_findings': []
            }
    
    def _generate_statistics_summary(self, report: Dict, output_path: str):
        """Generate statistics summary markdown"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Statistical Analysis Report\n\n")
            
            f.write("## Summary\n\n")
            summary = report['summary']
            f.write(f"- **Numerical Columns**: {summary['numerical_columns']}\n")
            f.write(f"- **Categorical Columns**: {summary['categorical_columns']}\n")
            f.write(f"- **Strong Correlations**: {summary['strong_correlations']}\n\n")
            
            f.write("## Key Findings\n\n")
            findings = report['interpretation'].get('key_findings', [])
            for finding in findings:
                f.write(f"- {finding}\n")
            
            f.write("\n## Strong Correlations\n\n")
            corrs = report['interpretation'].get('strong_correlations', [])
            if corrs:
                for corr in corrs:
                    f.write(f"### {corr.get('variables', 'Unknown')}\n")
                    f.write(f"- **Strength**: {corr.get('strength', 'unknown')}\n")
                    f.write(f"- **Interpretation**: {corr.get('interpretation', '')}\n\n")
            else:
                f.write("No strong correlations found.\n")
    
    def _run_pattern_agent(self, output_dir: str, max_iterations: int) -> Dict[str, Any]:
        """
        Pattern Discovery Agent - Acts as pattern recognition expert.
        
        Discovers patterns using multi-prompt strategy with pre-computed aggregations:
        - Temporal patterns (trends, seasonality)
        - Correlation patterns (relationships)
        - Grouping patterns (clusters, segments)
        - Anomaly patterns (unusual behaviors)
        """
        print("\n🧠 Agent thinking: I need to discover ALL patterns like a pattern recognition expert...")
        print("📝 Strategy: Pre-compute aggregations → Multi-prompt analysis\n")
        
        # Load prior outputs
        profile_path = f"{output_dir}/../step1_profiling/profile.json"
        quality_path = f"{output_dir}/../step2_quality/quality_report.json"
        statistics_path = f"{output_dir}/../step3_statistics/statistics.json"
        
        profile = {}
        quality_report = {}
        statistics = {}
        semantic_meanings = {}
        temporal_columns = []
        strong_correlations = []
        outlier_flags = {}
        distribution_stats = {}
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            # Extract semantic meanings and temporal columns
            for col_name, col_data in profile.get('columns', {}).items():
                semantic_meanings[col_name] = col_data.get('semantic_meaning', '')
                if col_data.get('data_type_class') == 'Temporal':
                    temporal_columns.append(col_name)
            
            print(f"  ├─ 📋 Loaded profile: {len(semantic_meanings)} semantic meanings, {len(temporal_columns)} temporal columns\n")
        except Exception as e:
            print(f"  ⚠️  Could not load profile.json: {e}\n")
        
        try:
            with open(quality_path, 'r', encoding='utf-8') as f:
                quality_report = json.load(f)
            
            outlier_flags = quality_report.get('metrics', {}).get('outliers', {})
            
            print(f"  ├─ 📋 Loaded quality report: {len(outlier_flags)} outlier columns\n")
        except Exception as e:
            print(f"  ⚠️  Could not load quality_report.json: {e}\n")
        
        try:
            with open(statistics_path, 'r', encoding='utf-8') as f:
                statistics = json.load(f)
            
            strong_correlations = statistics.get('statistics', {}).get('correlations', {}).get('strong_correlations', [])
            distribution_stats = statistics.get('statistics', {}).get('numerical_stats', {})
            
            print(f"  ├─ 📋 Loaded statistics: {len(strong_correlations)} strong correlations, {len(distribution_stats)} distribution stats\n")
        except Exception as e:
            print(f"  ⚠️  Could not load statistics.json: {e}\n")
        
        # Pre-compute aggregations
        print("📊 Pre-computing aggregations for pattern discovery...")
        aggregations = self._compute_pattern_aggregations(temporal_columns, semantic_meanings)
        print(f"  ├─ ✅ Computed aggregations: {len(aggregations.get('monthly_aggregations', {}))} monthly, {len(aggregations.get('group_aggregations', {}))} group\n")
        
        # Pattern categories to analyze
        pattern_categories = [
            {'name': 'Temporal Patterns', 'focus': 'time-based trends, seasonality, cycles'},
            {'name': 'Correlation Patterns', 'focus': 'strong relationships between variables'},
            {'name': 'Grouping Patterns', 'focus': 'natural clusters and segments'},
            {'name': 'Anomaly Patterns', 'focus': 'unusual behaviors and outliers'}
        ]
        
        all_patterns = {}
        
        for idx, category in enumerate(pattern_categories, 1):
            print(f"\n📊 Pattern Category {idx}/{len(pattern_categories)}: {category['name']}")
            print(f"  ├─ 🎯 Focus: {category['focus']}")
            print(f"  ├─ 🧠 Analyzing data for {category['name'].lower()}...")
            print(f"  ├─ 🔍 Using pre-computed aggregations...")
            
            # LLM discovers patterns for this category
            patterns = self._discover_patterns_by_category(
                category, 
                aggregations, 
                semantic_meanings, 
                strong_correlations, 
                outlier_flags, 
                distribution_stats
            )
            
            if patterns:
                all_patterns[category['name']] = patterns
                print(f"  ├─ ✅ Found {len(patterns)} {category['name'].lower()}")
                print(f"  └─ 💾 Saving patterns...\n")
            else:
                print(f"  └─ ⚠️  No patterns found for this category\n")
        
        # Consolidate all patterns
        print("🔗 Consolidating all discovered patterns...")
        consolidated = {
            'pattern_categories': list(all_patterns.keys()),
            'total_patterns': sum(len(p) for p in all_patterns.values()),
            'patterns_by_category': all_patterns
        }
        
        with open(f"{output_dir}/patterns.json", 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Consolidated {consolidated['total_patterns']} patterns across {len(all_patterns)} categories\n")
        
        # Generate summary
        self._generate_pattern_summary(consolidated, f"{output_dir}/summary.md")
        print(f"✓ Summary saved: {output_dir}/summary.md\n")
        
        return consolidated
    
    def _compute_pattern_aggregations(self, temporal_columns: List[str], semantic_meanings: Dict) -> Dict[str, Any]:
        """Pre-compute aggregations for pattern discovery"""
        aggregations = {
            'monthly_aggregations': {},
            'group_aggregations': {}
        }
        
        # Monthly aggregations (if temporal column exists)
        if temporal_columns:
            temporal_col = temporal_columns[0]
            try:
                self.df[temporal_col] = pd.to_datetime(self.df[temporal_col], errors='coerce')
                self.df['month'] = self.df[temporal_col].dt.to_period('M').astype(str)
                
                # Get key numerical columns for aggregation
                numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
                
                for col in numerical_cols[:5]:  # Limit to first 5 numerical columns
                    monthly_agg = self.df.groupby('month')[col].agg(['sum', 'mean', 'count']).to_dict()
                    aggregations['monthly_aggregations'][col] = monthly_agg
            except Exception as e:
                print(f"  ⚠️  Could not compute monthly aggregations: {e}")
        
        # Group aggregations for categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        for cat_col in categorical_cols[:5]:  # Limit to first 5 categorical columns
            for num_col in numerical_cols[:3]:  # Limit to first 3 numerical columns
                try:
                    group_agg = self.df.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count']).to_dict()
                    if cat_col not in aggregations['group_aggregations']:
                        aggregations['group_aggregations'][cat_col] = {}
                    aggregations['group_aggregations'][cat_col][num_col] = group_agg
                except Exception as e:
                    continue
        
        return aggregations
    
    def _discover_patterns_by_category(self, category: Dict, aggregations: Dict, semantic_meanings: Dict, strong_correlations: List, outlier_flags: Dict, distribution_stats: Dict) -> List[Dict[str, Any]]:
        """LLM discovers patterns for specific category with pre-computed aggregations"""
        
        # System prompt (same for all categories)
        system_prompt = "You are a pattern recognition expert. Your job is to identify concrete, evidence-backed patterns in data. You must only report patterns that are directly supported by the numbers provided. Do not speculate or infer patterns beyond what the evidence shows."
        
        # Build category-specific prompt
        if category['name'] == 'Temporal Patterns':
            prompt = f"""Discover temporal patterns in this dataset.

Focus: time-based trends, seasonality, growth or decline over time, cyclical behavior.

Computed monthly aggregations:
{json.dumps(aggregations.get('monthly_aggregations', {}), indent=2, ensure_ascii=False)}

Column semantic meanings:
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

Data quality score: {aggregations.get('quality_score', 'N/A')}

For each pattern found:
- Cite specific numbers from the monthly aggregations above
- State which months or periods show the pattern
- Assess pattern strength: strong | moderate | weak

Return JSON:

{{
  "patterns": [
    {{
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific numbers)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }}
  ]
}}"""
        
        elif category['name'] == 'Correlation Patterns':
            prompt = f"""Discover correlation patterns in this dataset.

Focus: strong relationships between variables, co-movement, potential dependencies.

Strong correlations computed from data (|r| > 0.7):
{json.dumps(strong_correlations, indent=2, ensure_ascii=False)}

Column semantic meanings:
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

Statistical interpretation from Step 3:
{json.dumps(distribution_stats, indent=2, ensure_ascii=False)}

For each pattern found:
- Reference the specific r value
- Explain the direction and likely business meaning of the relationship
- Note whether the correlation may be structural (e.g., one variable derived from another) or behavioral

Return JSON:

{{
  "patterns": [
    {{
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include r value and direction)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }}
  ]
}}"""
        
        elif category['name'] == 'Grouping Patterns':
            prompt = f"""Discover grouping patterns in this dataset.

Focus: differences between segments, dominant groups, uneven distributions across categories.

Computed group aggregations:
{json.dumps(aggregations.get('group_aggregations', {}), indent=2, ensure_ascii=False)}

Column semantic meanings:
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

For each pattern found:
- Cite specific group values from the aggregations above
- Compare groups directly where relevant (e.g., "Group A is 3× Group B")
- Assess whether the difference is meaningful for business decisions

Return JSON:

{{
  "patterns": [
    {{
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific group values)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }}
  ]
}}"""
        
        elif category['name'] == 'Anomaly Patterns':
            prompt = f"""Discover anomaly patterns in this dataset.

Focus: unusual values, outliers, spikes, unexpected distributions, zero-inflation.

Outlier flags from Step 2:
{json.dumps(outlier_flags, indent=2, ensure_ascii=False)}

Distribution statistics from Step 3:
{json.dumps(distribution_stats, indent=2, ensure_ascii=False)}

Column semantic meanings:
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

For each anomaly found:
- Cite specific statistics (e.g., mean vs median gap, outlier count, min/max)
- Assess whether the anomaly is likely a data quality issue or a real business event
- Suggest how it should be handled in downstream analysis

Return JSON:

{{
  "patterns": [
    {{
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific statistics)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_completion_tokens=8000,
                response_format={"type": "json_object"}
            )
            _add_usage_from_response(response)
            
            result = json.loads(response.choices[0].message.content)
            return result.get('patterns', [])
        except Exception as e:
            print(f"  ⚠️  Pattern discovery error: {e}")
            return []
    
    def _generate_pattern_summary(self, patterns: Dict, output_path: str):
        """Generate pattern summary markdown"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Pattern Discovery Report\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Patterns**: {patterns['total_patterns']}\n")
            f.write(f"- **Pattern Categories**: {len(patterns['pattern_categories'])}\n\n")
            
            for category_name, category_patterns in patterns['patterns_by_category'].items():
                f.write(f"## {category_name}\n\n")
                f.write(f"Found {len(category_patterns)} patterns:\n\n")
                
                for pattern in category_patterns[:5]:  # Show top 5
                    f.write(f"### {pattern.get('pattern_name', 'Unknown')}\n")
                    f.write(f"- **Description**: {pattern.get('description', '')}\n")
                    f.write(f"- **Strength**: {pattern.get('strength', 'unknown')}\n")
                    f.write(f"- **Variables**: {', '.join(pattern.get('variables_involved', []))}\n")
                    f.write(f"- **Relevance**: {pattern.get('business_relevance', '')}\n\n")
    
    def _run_insight_agent(self, output_dir: str, max_iterations: int = 3) -> List[Dict[str, Any]]:
        """
        Insight Extraction Agent - Extracts insights without ISGEN scoring.
        
        Extracts all insights without scoring or threshold filtering.
        
        Args:
            output_dir: Output directory for insights
            max_iterations: Max iterations to avoid infinite loop (default: 3)
        """
        print("\n🧠 Agent thinking: I need to extract all valuable insights without scoring...")
        print(f"📝 Strategy: Extract all insights, no scoring or threshold filtering\n")
        
        # Load all prior outputs for unified context
        print("📋 Loading all prior analysis outputs for unified context...")
        profile_path = f"{output_dir}/../step1_profiling/profile.json"
        quality_path = f"{output_dir}/../step2_quality/quality_report.json"
        statistics_path = f"{output_dir}/../step3_statistics/statistics.json"
        patterns_path = f"{output_dir}/../step4_patterns/patterns.json"
        
        profile = {}
        quality_report = {}
        statistics = {}
        patterns = {}
        semantic_meanings = {}
        quality_score = 0
        critical_issues = []
        statistical_findings = []
        strong_correlations = []
        discovered_patterns = []
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            # Extract semantic meanings
            for col_name, col_data in profile.get('columns', {}).items():
                semantic_meanings[col_name] = col_data.get('semantic_meaning', '')
            
            print(f"  ├─ 📋 Loaded profile: {len(semantic_meanings)} semantic meanings\n")
        except Exception as e:
            print(f"  ⚠️  Could not load profile.json: {e}\n")
        
        try:
            with open(quality_path, 'r', encoding='utf-8') as f:
                quality_report = json.load(f)
            
            quality_score = quality_report.get('summary', {}).get('data_quality_score', 0)
            critical_issues = quality_report.get('assessment', {}).get('critical_issues', [])
            
            print(f"  ├─ 📋 Loaded quality report: score={quality_score}, {len(critical_issues)} critical issues\n")
        except Exception as e:
            print(f"  ⚠️  Could not load quality_report.json: {e}\n")
        
        try:
            with open(statistics_path, 'r', encoding='utf-8') as f:
                statistics = json.load(f)
            
            statistical_findings = statistics.get('interpretation', {}).get('key_findings', [])
            strong_correlations = statistics.get('statistics', {}).get('correlations', {}).get('strong_correlations', [])
            
            print(f"  ├─ 📋 Loaded statistics: {len(statistical_findings)} findings, {len(strong_correlations)} strong correlations\n")
        except Exception as e:
            print(f"  ⚠️  Could not load statistics.json: {e}\n")
        
        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
            
            # Flatten all patterns
            for category, category_patterns in patterns.get('patterns_by_category', {}).items():
                for pattern in category_patterns:
                    discovered_patterns.append({
                        'category': category,
                        'name': pattern.get('pattern_name', ''),
                        'description': pattern.get('description', ''),
                        'variables': pattern.get('variables_involved', [])
                    })
            
            print(f"  ├─ 📋 Loaded patterns: {len(discovered_patterns)} patterns across categories\n")
        except Exception as e:
            print(f"  ⚠️  Could not load patterns.json: {e}\n")
        
        all_processed_insights = []
        used_titles = set()  # Track titles to avoid duplicates
        iteration = 0
        
        # Insight categories to extract
        insight_categories = [
            {'types': ['TREND'], 'focus': 'temporal trends and directional changes'},
            {'types': ['OUTLIER', 'ANOMALY'], 'focus': 'unusual values and anomalies'},
            {'types': ['CORRELATION'], 'focus': 'relationships between variables'},
            {'types': ['DISTRIBUTION', 'COMPARISON'], 'focus': 'distributions and group comparisons'},
            {'types': ['PATTERN'], 'focus': 'recurring patterns and cycles'}
        ]
        
        while iteration < max_iterations:
            iteration += 1
            
            if iteration > 1:
                print(f"\n🔄 Iteration {iteration}:")
                print(f"   Total insights so far: {len(all_processed_insights)}")
            
            all_insights = []
            
            for idx, category in enumerate(insight_categories, 1):
                print(f"\n📊 Insight Batch {idx}/{len(insight_categories)}: {', '.join(category['types'])}")
                print(f"  ├─ 🎯 Focus: {category['focus']}")
                
                print(f"  ├─ 💭 Using unified context from all prior steps...")
                print(f"  ├─ ✍️  Generating insight extraction prompt...")
                
                # Pass unified context to avoid duplicates
                insights = self._extract_insights_by_category(
                    category, 
                    output_dir, 
                    used_titles,
                    semantic_meanings,
                    quality_score,
                    critical_issues,
                    statistical_findings,
                    strong_correlations,
                    discovered_patterns
                )
                
                if insights:
                    print(f"  ├─ ✅ Extracted {len(insights)} insights")
                    all_insights.extend(insights)
                    print(f"  └─ 📈 Total insights so far: {len(all_insights)}\n")
                else:
                    print(f"  └─ ⚠️  No insights extracted for this category\n")
            
            print(f"✓ Total insights extracted this iteration: {len(all_insights)}\n")
            
            # Process insights: generate charts without scoring
            print("🎨 Generating visualizations for all insights...")
            
            for insight_data in all_insights:
                title = insight_data.get('title', '')
                
                # Skip duplicates
                if title in used_titles:
                    continue
                used_titles.add(title)
                
                idx = len(all_processed_insights)
                insight_id = f"insight_{idx:03d}"
                
                print(f"  📊 {idx+1}: {title[:60]}...")
                
                # Get chart type from LLM response
                chart_type = insight_data.get('chart_type', 'bar')
                
                # Generate chart
                chart_filename = f"insight_{idx:03d}.png"
                chart_path = self._generate_chart(insight_data, f"{output_dir}/{chart_filename}")
                
                processed_insight = {
                    'insight_id': insight_id,
                    'title': title,
                    'description': insight_data.get('description', ''),
                    'insight_type': insight_data.get('type', ''),
                    'chart_path': chart_path,
                    'data_evidence': insight_data.get('evidence', {}),
                    'variables': insight_data.get('variables', []),
                    'chart_type': chart_type,
                    'subspace': insight_data.get('subspace', []),  # Extract subspace from LLM response
                    'view_labels': insight_data.get('view_labels', [])  # Extract view_labels from post-processing
                }
                
                all_processed_insights.append(processed_insight)
                print(f"    ✓ Chart generated")
        
        # Save all insights without filtering
        print(f"\n💾 Saving all insights...")
        
        def convert_to_native(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        insights_native = convert_to_native(all_processed_insights)
        
        with open(f"{output_dir}/insights.json", 'w', encoding='utf-8') as f:
            json.dump(insights_native, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Final: {len(all_processed_insights)} insights extracted (no scoring)")
        print(f"✓ Insights saved: {output_dir}/insights.json\n")
        
        return all_processed_insights
    
    def _extract_insights_by_category(self, category: Dict, output_dir: str, used_titles: set = None, semantic_meanings: Dict = None, quality_score: int = 0, critical_issues: List = None, statistical_findings: List = None, strong_correlations: List = None, discovered_patterns: List = None) -> List[Dict[str, Any]]:
        """Extract insights for a specific category using LLM with unified context from all prior steps"""
        
        if used_titles is None:
            used_titles = set()
        if semantic_meanings is None:
            semantic_meanings = {}
        if critical_issues is None:
            critical_issues = []
        if statistical_findings is None:
            statistical_findings = []
        if strong_correlations is None:
            strong_correlations = []
        if discovered_patterns is None:
            discovered_patterns = []
        
        # Get actual column names from dataset
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()[:20]
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()[:20]
        
        # Get unique values for categorical columns (for subspace generation)
        categorical_values = {}
        for col in categorical_cols:
            unique_vals = self.df[col].dropna().unique()
            # Limit to top 10 values to avoid too much context
            categorical_values[col] = unique_vals[:10].tolist()
        
        # Build exclusion text if there are used titles
        exclusion_text = ""
        if used_titles:
            exclusion_text = f"\n\nIMPORTANT: Avoid these already-extracted insights:\n{chr(10).join(['- ' + t for t in list(used_titles)[:10]])}\n\nGenerate DIFFERENT insights with different angles and variables."
        
        # Build unified context according to PROMPTS.md
        prompt = f"""Extract insights of the following type(s): {', '.join(category['types'])}

AVAILABLE COLUMNS — use ONLY these exact names in "variables" and "subspace":
- Numerical: {', '.join(numerical_cols)}
- Categorical: {', '.join(categorical_cols)}

CRITICAL: Do NOT use derived or computed column names (e.g., "month", "year", "quarter", "day").
If a temporal insight is needed, use the original date column name (e.g., "Invoice Date").
Even if a "month" column exists in the dataframe, DO NOT use it. Always use the original date column.

VALID SUBSPACE VALUES — when using subspace, the value MUST be taken from this list exactly as written:
{json.dumps(categorical_values, indent=2, ensure_ascii=False)}

Do NOT invent subspace values. Only use values that appear in the list above.

Context from prior analysis steps:

Step 1 — Column meanings:
{json.dumps(semantic_meanings, indent=2, ensure_ascii=False)}

Step 2 — Quality Assessment:
- Overall quality score: {quality_score}
- Critical issues: {json.dumps(critical_issues[:5], indent=2, ensure_ascii=False)}

Step 3 — Statistical Analysis:
- Key statistical findings: {json.dumps(statistical_findings, indent=2, ensure_ascii=False)}
- Strong correlations: {json.dumps(strong_correlations, indent=2, ensure_ascii=False)}

Step 4 — Discovered patterns (relevant to {', '.join(category['types'])}):
{json.dumps(discovered_patterns[:10], indent=2, ensure_ascii=False)}{exclusion_text}

Already extracted insights (do not repeat these):
{used_titles}

SUBSPACE RULES:
- Use subspace only when the insight is specifically about a subset of data
- Subspace must be a column that exists in the categorical columns list above
- Subspace value must be an actual value that exists in that column
- Each insight uses at most ONE subspace condition: [["column_name", "value"]]
- For global insights (whole dataset): "subspace": []
- Do NOT use numerical columns or derived columns as subspace

For each insight:
- Write a specific, concrete title
- Include actual numbers in the description
- Reference which step provided the evidence
- List the columns involved (from available columns only)
- Choose an appropriate chart type: line | bar | scatter | histogram | box

Return JSON:
{{
  "insights": [
    {{
      "title": "...",
      "description": "... (include specific numbers)",
      "type": "{', '.join(category['types'])}",
      "variables": ["column_name_1", "column_name_2"],
      "evidence": {{
        "source_step": "step3_statistics|step4_patterns|step2_quality",
        "key_statistics": "...",
        "data_points": "..."
      }},
      "chart_type": "line|bar|scatter|histogram|box",
      "subspace": []
    }}
  ]
}}

Extract as many valuable insights as possible."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst extracting insights for a business audience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_completion_tokens=16000,
                response_format={"type": "json_object"}
            )
            _add_usage_from_response(response)

            result = json.loads(response.choices[0].message.content)
            insights = result.get('insights', [])

            # Post-processing: compute view_labels for each insight
            insights = self._compute_view_labels(insights)

            return insights
        except Exception as e:
            print(f"    ⚠️  Error extracting insights: {e}")
            return []

    def _compute_view_labels(self, insights):
        """
        Post-processing: compute view_labels for each insight based on subspace filter.
        This ensures labels always match the subspace-filtered data and pass faithfulness checks.
        """
        processed_insights = []

        for insight in insights:
            try:
                # Get subspace condition
                subspace = insight.get('subspace', [])

                # 1. Validate subspace (if not empty)
                if subspace and subspace != []:
                    # Validate subspace column exists in df.columns
                    if len(subspace) == 1 and len(subspace[0]) == 2:
                        col, val = subspace[0]
                        if col not in self.df.columns:
                            print(f"    ⚠️  Skipping insight: invalid subspace column '{col}'")
                            continue
                        # Validate subspace value exists in df[col].unique()
                        unique_vals = self.df[col].dropna().unique().tolist()
                        if val not in unique_vals:
                            print(f"    ⚠️  Skipping insight: subspace value '{val}' not found in data for column '{col}'")
                            continue
                    else:
                        # Invalid subspace format
                        print(f"    ⚠️  Skipping insight: invalid subspace format {subspace}")
                        continue

                # 2. Apply subspace filter
                if not subspace or subspace == []:
                    # Global insight - use full dataframe
                    filtered_df = self.df
                else:
                    # Subspace insight - apply filter
                    # Format: [["column_name", "value"]]
                    col, val = subspace[0]
                    # Convert both to string for comparison
                    filtered_df = self.df[self.df[col].astype(str) == str(val)].copy()

                # 3. Validate breakdown column
                variables = insight.get('variables', [])
                if not variables:
                    print(f"    ⚠️  Skipping insight: no variables specified")
                    continue

                # Use first variable as breakdown column
                breakdown_col = variables[0]

                # Check that breakdown column exists in filtered_df.columns
                if breakdown_col not in filtered_df.columns:
                    print(f"    ⚠️  Skipping insight: breakdown column '{breakdown_col}' not found")
                    continue

                # 4. Compute view_labels
                view_labels = sorted(filtered_df[breakdown_col].dropna().unique().tolist())

                # If view_labels is empty: drop insight
                if not view_labels:
                    print(f"    ⚠️  Skipping insight: filtered dataframe is empty")
                    continue

                # 5. Attach view_labels to insight
                insight['view_labels'] = view_labels

                processed_insights.append(insight)

            except Exception as e:
                print(f"    ⚠️  Error processing insight: {e}")
                continue

        return processed_insights
    
    # Code generation methods
    def _generate_profiling_code(self, output_dir: str, iteration: int) -> str:
        """Generate profiling code with LLM"""
        
        prompt = f"""Write Python code to generate comprehensive data profile (iteration {iteration}).

Dataset: '{self.data_path}'
Output: '{output_dir}/profile.json', '{output_dir}/summary.md'

Requirements:
1. Load data: pd.read_csv('{self.data_path}', sep=None, engine='python')
2. Generate profile with:
   - Basic info (shape, columns, dtypes, memory)
   - Numerical columns: min, max, mean, std, quartiles, missing
   - Categorical columns: unique count, top values, missing
3. Save to JSON (use default=str for serialization)
4. Create markdown summary

Return ONLY executable Python code."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Python code generator. Return only executable code, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=2000
        )
        _add_usage_from_response(response)
        
        code = response.choices[0].message.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    def _generate_quality_code(self, output_dir: str, iteration: int, previous_issues: List) -> str:
        """Generate quality analysis code"""
        
        focus = "comprehensive quality analysis" if iteration == 1 else f"additional quality issues beyond: {previous_issues}"
        
        prompt = f"""Write Python code for {focus} (iteration {iteration}).

Dataset: '{self.data_path}'
Output: '{output_dir}/quality_report.json'

Requirements:
1. Load data: pd.read_csv('{self.data_path}', sep=None, engine='python')
2. Analyze: missing values, outliers (IQR), duplicates, type issues
3. Save report to JSON (use default=str)

Return ONLY executable Python code."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Python code generator. Return only executable code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=2000
        )
        _add_usage_from_response(response)
        
        code = response.choices[0].message.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    def _generate_statistics_code(self, output_dir: str, iteration: int) -> str:
        """Generate statistics code"""
        
        prompt = f"""Write Python code for statistical analysis (iteration {iteration}).

Dataset: '{self.data_path}'
Output: '{output_dir}/statistics.json'

Requirements:
1. Load data: pd.read_csv('{self.data_path}', sep=None, engine='python')
2. Compute: descriptive stats, correlations, distributions
3. Save to JSON (use default=str)

Return ONLY executable Python code."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Python code generator. Return only executable code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=2000
        )
        _add_usage_from_response(response)
        
        code = response.choices[0].message.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    def _generate_pattern_code(self, output_dir: str, category: Dict, idx: int) -> str:
        """Generate pattern discovery code for specific category"""
        
        output_file = f"{output_dir}/patterns_{category['name'].lower().replace(' ', '_')}.json"
        
        prompt = f"""Write Python code to discover {category['name']}: {category['focus']}.

Dataset: '{self.data_path}'
Output: '{output_file}'

Requirements:
1. Load data: pd.read_csv('{self.data_path}', sep=None, engine='python')
2. Focus on: {category['focus']}
3. Save discovered patterns to JSON (use default=str)

Return ONLY executable Python code."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Python code generator. Return only executable code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=2000
        )
        _add_usage_from_response(response)
        
        code = response.choices[0].message.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    # Execution and evaluation methods
    def _execute_code(self, code: str, output_dir: str) -> Tuple[bool, Any]:
        """Execute generated code safely"""
        try:
            exec_globals = {
                'pd': pd,
                'np': np,
                'json': json,
                'plt': plt,
                'sns': sns,
                '__file__': f"{output_dir}/code.py"
            }
            exec(code, exec_globals)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def _evaluate_profile(self, output_dir: str) -> Tuple[bool, str]:
        """Evaluate if profile is comprehensive"""
        try:
            with open(f"{output_dir}/profile.json", 'r') as f:
                profile = json.load(f)
            
            # Check completeness
            has_basic = 'basic_info' in profile or 'shape' in profile
            has_numerical = 'numerical_summary' in profile or any('numerical' in str(k).lower() for k in profile.keys())
            has_categorical = 'categorical_summary' in profile or any('categorical' in str(k).lower() for k in profile.keys())
            
            if has_basic and has_numerical and has_categorical:
                return True, ""
            else:
                missing = []
                if not has_basic: missing.append("basic info")
                if not has_numerical: missing.append("numerical summary")
                if not has_categorical: missing.append("categorical summary")
                return False, f"Missing: {', '.join(missing)}"
        except:
            return False, "Profile file not found or invalid"
    
    def _check_for_more_quality_issues(self, output_dir: str) -> Tuple[bool, List]:
        """Check if more quality issues can be found"""
        # Simplified - in real agent, would analyze report
        return False, []
    
    def _evaluate_statistics_coverage(self, output_dir: str) -> bool:
        """Evaluate if statistics are comprehensive"""
        try:
            with open(f"{output_dir}/statistics.json", 'r') as f:
                stats = json.load(f)
            return len(stats) > 0
        except:
            return False
    
    # Chart generation
    def _generate_chart(self, insight_data: Dict[str, Any], output_path: str) -> str:
        """Generate visualization for insight"""
        try:
            insight_type = insight_data.get('type', '')
            variables = insight_data.get('variables', [])
            
            # Validate variables exist in dataset
            valid_vars = [v for v in variables if v in self.df.columns]
            if not valid_vars:
                # No valid variables, create placeholder
                raise ValueError(f"No valid columns found in {variables}")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            chart_created = False
            
            if insight_type == 'TREND' and len(valid_vars) >= 2:
                # Plot relationship: x-axis = first var, y-axis = second var
                var_x, var_y = valid_vars[0], valid_vars[1]
                if self.df[var_y].dtype in [np.float64, np.int64]:
                    # Group by x and plot mean of y
                    if self.df[var_x].dtype in [np.float64, np.int64]:
                        self.df.plot.scatter(x=var_x, y=var_y, ax=ax, alpha=0.6)
                    else:
                        self.df.groupby(var_x)[var_y].mean().plot(kind='line', ax=ax, marker='o', linewidth=2)
                    ax.set_xlabel(var_x)
                    ax.set_ylabel(var_y)
                    chart_created = True
            elif insight_type == 'TREND' and len(valid_vars) == 1:
                # Single variable trend - plot over index
                var = valid_vars[0]
                if self.df[var].dtype in [np.float64, np.int64]:
                    self.df[var].plot(ax=ax, linewidth=2)
                    ax.set_ylabel(var)
                    chart_created = True
            elif insight_type in ['OUTLIER', 'ANOMALY'] and len(valid_vars) >= 1:
                var = valid_vars[0]
                if self.df[var].dtype in [np.float64, np.int64]:
                    self.df.boxplot(column=var, ax=ax)
                    chart_created = True
            elif insight_type == 'CORRELATION' and len(valid_vars) >= 2:
                var1, var2 = valid_vars[0], valid_vars[1]
                if (self.df[var1].dtype in [np.float64, np.int64] and 
                    self.df[var2].dtype in [np.float64, np.int64]):
                    self.df.plot.scatter(x=var1, y=var2, ax=ax, alpha=0.5)
                    ax.set_xlabel(var1)
                    ax.set_ylabel(var2)
                    chart_created = True
            elif insight_type == 'DISTRIBUTION' and len(valid_vars) >= 1:
                var = valid_vars[0]
                if self.df[var].dtype in [np.float64, np.int64]:
                    self.df[var].hist(bins=30, ax=ax, edgecolor='black')
                    ax.set_xlabel(var)
                    ax.set_ylabel('Frequency')
                    chart_created = True
            elif insight_type == 'COMPARISON' and len(valid_vars) >= 1:
                var = valid_vars[0]
                value_counts = self.df[var].value_counts().head(10)
                value_counts.plot(kind='bar', ax=ax)
                ax.set_xlabel(var)
                ax.set_ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                chart_created = True
            elif insight_type == 'PATTERN' and len(valid_vars) >= 1:
                var = valid_vars[0]
                if self.df[var].dtype in [np.float64, np.int64]:
                    self.df[var].plot(ax=ax, linewidth=2)
                    ax.set_ylabel(var)
                else:
                    self.df[var].value_counts().head(10).plot(kind='bar', ax=ax)
                    ax.set_xlabel(var)
                    ax.set_ylabel('Count')
                    plt.xticks(rotation=45, ha='right')
                chart_created = True
            
            # Fallback: try to plot first valid variable
            if not chart_created and valid_vars:
                var = valid_vars[0]
                if self.df[var].dtype in [np.float64, np.int64]:
                    self.df[var].hist(bins=30, ax=ax, edgecolor='black')
                    ax.set_xlabel(var)
                    ax.set_ylabel('Frequency')
                else:
                    self.df[var].value_counts().head(10).plot(kind='bar', ax=ax)
                    ax.set_xlabel(var)
                    ax.set_ylabel('Count')
                    plt.xticks(rotation=45, ha='right')
            
            ax.set_title(insight_data.get('title', ''), fontsize=14, fontweight='bold', wrap=True)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        except Exception as e:
            # Create placeholder chart with error message
            fig, ax = plt.subplots(figsize=(10, 6))
            variables = insight_data.get('variables', [])
            error_msg = f'Chart not available\n(Variables: {variables})'
            ax.text(0.5, 0.5, error_msg, ha='center', va='center', fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(insight_data.get('title', ''), fontsize=14, fontweight='bold', wrap=True)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  ⚠️  Chart generation failed: {e}")
            return output_path
    
    def _extract_values_for_scoring(self, insight_data: Dict, variables: List[str]) -> List[float]:
        """Extract values for ISGEN scoring"""
        values = []
        if variables and len(variables) > 0:
            var = variables[0]
            if var in self.df.columns:
                try:
                    if self.df[var].dtype in [np.float64, np.int64, np.int32, np.float32]:
                        values = self.df[var].dropna().values.tolist()[:100]
                    else:
                        values = self.df[var].value_counts().values.tolist()
                except:
                    pass
        return values
    
    def _generate_summary(self, output_dir: str):
        """Generate final summary and QUIS-compatible output"""
        insights = self.step_outputs.get('step5', [])
        
        total = len(insights)
        
        # Check if insights have scores (if not, skip score-related calculations)
        has_scores = len(insights) > 0 and 'score' in insights[0]
        
        if has_scores:
            passed = sum(1 for i in insights if i['score']['passed'])
            pass_rate = (passed / total * 100) if total > 0 else 0
            avg_score = sum(i['score']['pattern_score'] for i in insights) / total if total > 0 else 0
            top_insights = sorted(insights, key=lambda x: x['score']['pattern_score'], reverse=True)[:10]
        else:
            passed = 0
            pass_rate = 0
            avg_score = 0
            top_insights = insights[:10] if total > 0 else []
        
        type_counts = {}
        pattern_counts = {}
        for i in insights:
            itype = i['insight_type']
            if has_scores:
                ptype = i['score'].get('pattern_type', 'UNKNOWN')
            else:
                ptype = 'UNKNOWN'
            type_counts[itype] = type_counts.get(itype, 0) + 1
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        
        with open(f"{output_dir}/summary.txt", 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("AGENTIC AUTOEDA BASELINE - SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Insights: {total}\n")
            f.write(f"Passed ISGEN Threshold: {passed}/{total} ({pass_rate:.1f}%)\n")
            f.write(f"Average Pattern Score: {avg_score:.3f}\n\n")
            
            f.write("Insights by Type:\n")
            for itype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  • {itype}: {count}\n")
            f.write("\n")
            
            f.write("Insights by ISGEN Pattern:\n")
            for ptype, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  • {ptype}: {count}\n")
            f.write("\n")
            
            f.write("Top 10 Insights:\n")
            for i, insight in enumerate(top_insights, 1):
                if has_scores:
                    score_info = insight['score']
                    passed_mark = "✓" if score_info['passed'] else "✗"
                    f.write(f"  {i}. {passed_mark} {insight['insight_id']}: {insight['title']}\n")
                    f.write(f"     Pattern: {score_info['pattern_type']}, Score: {score_info['pattern_score']:.3f}\n")
                else:
                    f.write(f"  {i}. {insight['insight_id']}: {insight['title']}\n")
                    f.write(f"     Type: {insight['insight_type']}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"✓ Summary saved: {output_dir}/summary.txt")
        
        # Convert to QUIS-compatible format
        print("\n🔄 Converting to QUIS-compatible format...")
        try:
            from output_converter import OutputConverter
            converter = OutputConverter(self.df)
            
            # Get insights path from step5 output
            insights_path = f"{self.step_outputs.get('step5_dir', 'output/step5_insights')}/insights.json"
            quis_output_dir = f"{output_dir.replace('/summary', '')}/quis_format"
            
            result = converter.convert_insights(insights_path, quis_output_dir)
            
            print(f"✓ QUIS-compatible output saved:")
            print(f"  📄 InsightCards: {quis_output_dir}/insight_cards.json")
            print(f"  📄 Insights: {quis_output_dir}/insights.json")
        except Exception as e:
            print(f"⚠️  QUIS conversion failed: {e}")
            print(f"   You can manually convert using: python output_converter.py")
    
    # Fallback methods
    def _create_basic_profile(self, output_dir: str):
        """Fallback profile"""
        profile = {
            'shape': {'rows': len(self.df), 'columns': len(self.df.columns)},
            'columns': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }
        with open(f"{output_dir}/profile.json", 'w') as f:
            json.dump(profile, f, indent=2)
        with open(f"{output_dir}/summary.md", 'w') as f:
            f.write(f"# Data Profile\n\nShape: {self.df.shape}\n")
    
    def _create_basic_quality_report(self, output_dir: str):
        """Fallback quality report"""
        report = {
            'missing_values': {col: int(self.df[col].isnull().sum()) for col in self.df.columns},
            'duplicates': int(self.df.duplicated().sum())
        }
        with open(f"{output_dir}/quality_report.json", 'w') as f:
            json.dump(report, f, indent=2)
    
    def _create_basic_statistics(self, output_dir: str):
        """Fallback statistics"""
        stats = {'numerical': self.df.describe().to_dict()}
        with open(f"{output_dir}/statistics.json", 'w') as f:
            json.dump(stats, f, indent=2, default=str)
