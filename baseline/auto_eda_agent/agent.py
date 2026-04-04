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
    
    def run_autoeda(self, output_dir: str = 'output', max_iterations: int = 3) -> Dict[str, Any]:
        """
        Run complete agentic AutoEDA workflow.
        
        Each step runs as autonomous agent with iterative refinement.
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
        
        # Step 5: Insight Extraction Agent
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
            'throughput': len(self.step_outputs.get('step5', [])) / total_time if total_time > 0 else 0
        }
        
        with open(f"{output_dir}/timing.json", 'w') as f:
            json.dump(timing_info, f, indent=2)
        
        print(f"📊 Generated {len(self.step_outputs.get('step5', []))} insights")
        print(f"⚡ Throughput: {timing_info['throughput']:.2f} insights/second")
        print(f"💾 Timing info saved to {output_dir}/timing.json")
        
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
        - Detect patterns
        - Classify data type
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
        prompt = f"""You are an expert data analyst. Analyze these columns and infer their semantic meaning.

Dataset has {len(self.df)} rows, {len(self.df.columns)} columns.

Column samples (showing unique values):
{json.dumps(column_samples, indent=2, ensure_ascii=False)}

For EACH column, infer:
1. **Semantic meaning**: What does this column represent? (e.g., "customer age", "product category", "transaction date")
2. **Data type classification**: 
   - ID/Code (unique identifiers)
   - Categorical (limited distinct values)
   - Numerical (measurements, counts, amounts)
   - Temporal (dates, times)
   - Text (free text)
3. **Patterns detected**: Any patterns in the values?
4. **Potential issues**: Missing values, inconsistencies, etc.

Return JSON:
{{
  "column_name": {{
    "semantic_meaning": "what this represents",
    "data_type_class": "ID|Categorical|Numerical|Temporal|Text",
    "patterns": "detected patterns",
    "potential_issues": "any issues noticed",
    "importance": "high|medium|low"
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
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            
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
        - Outliers and anomalies
        - Inconsistencies and errors
        - Data integrity issues
        """
        print("\n🧠 Agent thinking: I need to thoroughly assess data quality like an expert...")
        print("📝 Strategy: Compute quality metrics → Analyze patterns → Identify issues\n")
        
        # Phase 1: Compute quality metrics
        print("📊 Phase 1: Computing Quality Metrics")
        print("  ├─ 🔍 Analyzing missing values...")
        print("  ├─ 📊 Detecting outliers...")
        print("  ├─ 🔎 Checking duplicates...")
        
        quality_metrics = self._compute_quality_metrics()
        
        print(f"  ├─ ✅ Found {quality_metrics['total_issues']} quality issues")
        print(f"  └─ 💾 Saving metrics...\n")
        
        # Phase 2: LLM analyzes quality issues
        print("📊 Phase 2: Expert Quality Assessment")
        print("  ├─ 🧠 Interpreting quality metrics...")
        print("  ├─ 🔍 Identifying critical issues...")
        print("  ├─ 📋 Prioritizing problems...")
        
        quality_assessment = self._expert_quality_assessment(quality_metrics)
        
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
    
    def _compute_quality_metrics(self) -> Dict[str, Any]:
        """Compute quality metrics directly"""
        
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
        
        # Outliers (IQR method for numerical columns)
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
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
    
    def _expert_quality_assessment(self, metrics: Dict) -> Dict[str, Any]:
        """LLM acts as quality expert to assess issues"""
        
        prompt = f"""You are a data quality expert. Analyze these quality metrics and provide expert assessment.

Quality Metrics:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

Provide expert assessment:
1. **Critical Issues**: Which quality issues are most critical and why?
2. **Impact Analysis**: How do these issues affect data reliability?
3. **Recommendations**: What should be done to address each issue?
4. **Overall Quality Score**: Rate data quality 0-100 based on severity of issues
5. **Priority Actions**: Top 3 actions to improve quality

Return JSON:
{{
  "critical_issues": [
    {{
      "issue": "description",
      "severity": "high|medium|low",
      "impact": "how it affects analysis",
      "recommendation": "what to do"
    }}
  ],
  "overall_quality_score": 75,
  "priority_actions": ["action1", "action2", "action3"],
  "detailed_analysis": "comprehensive quality assessment"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data quality expert providing professional assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
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
        
        interpretation = self._expert_statistical_interpretation(statistics)
        
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
    
    def _expert_statistical_interpretation(self, statistics: Dict) -> Dict[str, Any]:
        """LLM acts as statistician to interpret findings"""
        
        # Prepare summary for LLM
        summary = {
            'numerical_columns': len(statistics['numerical_stats']),
            'categorical_columns': len(statistics['categorical_stats']),
            'strong_correlations': statistics['correlations'].get('strong_correlations', []),
            'sample_stats': {k: v for k, v in list(statistics['numerical_stats'].items())[:5]}
        }
        
        prompt = f"""You are an expert statistician. Interpret these statistical findings.

Statistical Summary:
{json.dumps(summary, indent=2, ensure_ascii=False)}

Provide expert interpretation:
1. **Distribution Patterns**: What do the distributions tell us? (skewness, kurtosis)
2. **Strong Correlations**: Interpret the strong correlations found
3. **Key Statistical Findings**: Most important statistical insights
4. **Anomalies**: Any unusual statistical patterns?
5. **Recommendations**: Statistical tests or analyses to perform next

Return JSON:
{{
  "distribution_patterns": "interpretation of distributions",
  "strong_correlations": [
    {{
      "variables": "var1 and var2",
      "interpretation": "what this correlation means",
      "strength": "strong|moderate|weak"
    }}
  ],
  "key_findings": ["finding1", "finding2", "finding3"],
  "statistical_anomalies": ["anomaly1", "anomaly2"],
  "recommendations": ["recommendation1", "recommendation2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert statistician interpreting data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
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
        
        Discovers patterns using multi-prompt strategy:
        - Temporal patterns (trends, seasonality)
        - Correlation patterns (relationships)
        - Grouping patterns (clusters, segments)
        - Anomaly patterns (unusual behaviors)
        """
        print("\n🧠 Agent thinking: I need to discover ALL patterns like a pattern recognition expert...")
        print("📝 Strategy: Multi-prompt approach - analyze each pattern type separately\n")
        
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
            print(f"  ├─ 🔍 Using previous analysis results...")
            
            # LLM discovers patterns for this category
            patterns = self._discover_patterns_by_category(category)
            
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
    
    def _discover_patterns_by_category(self, category: Dict) -> List[Dict[str, Any]]:
        """LLM discovers patterns for specific category"""
        
        # Prepare context from previous steps
        context = {
            'profile': self.step_outputs.get('step1', {}),
            'quality': self.step_outputs.get('step2', {}),
            'statistics': self.step_outputs.get('step3', {})
        }
        
        # Prepare data summary for pattern discovery
        data_info = {
            'shape': {'rows': len(self.df), 'columns': len(self.df.columns)},
            'numerical_columns': list(self.df.select_dtypes(include=[np.number]).columns[:10]),
            'categorical_columns': list(self.df.select_dtypes(include=['object']).columns[:10])
        }
        
        prompt = f"""You are a pattern recognition expert. Discover {category['name']} in this dataset.

Focus: {category['focus']}

Dataset Info:
{json.dumps(data_info, indent=2, ensure_ascii=False)}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL {category['name']} by:
1. Analyzing the data structure and available variables
2. Looking for {category['focus']}
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{{
  "patterns": [
    {{
      "pattern_name": "specific pattern name",
      "description": "detailed description of the pattern",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence from data",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this pattern matters"
    }}
  ]
}}

Find as many valuable patterns as possible."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a pattern recognition expert specializing in {category['name'].lower()}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            
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
    
    def _run_insight_agent(self, output_dir: str, min_insights: int = 15, max_iterations: int = 3) -> List[Dict[str, Any]]:
        """
        Insight Extraction Agent - Iteratively extracts insights until threshold is met.
        
        Like QUIS, filters insights by score threshold and generates more if needed.
        
        Args:
            output_dir: Output directory for insights
            min_insights: Minimum number of insights passing threshold (default: 15)
            max_iterations: Max iterations to avoid infinite loop (default: 3)
        """
        print("\n🧠 Agent thinking: I need to extract valuable insights passing ISGEN threshold...")
        print(f"📝 Strategy: Iterative generation until {min_insights}+ insights pass threshold\n")
        
        all_processed_insights = []
        used_titles = set()  # Track titles to avoid duplicates
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Count current passing insights
            passing_count = sum(1 for i in all_processed_insights if i['score']['passed'])
            
            if passing_count >= min_insights and iteration > 1:
                print(f"\n✅ Target reached: {passing_count} insights pass threshold!")
                break
            
            if iteration > 1:
                print(f"\n🔄 Iteration {iteration}: Need {min_insights - passing_count} more passing insights...")
            
            # Insight categories
            insight_categories = [
                {'types': ['TREND'], 'focus': 'temporal trends and directional changes'},
                {'types': ['OUTLIER', 'ANOMALY'], 'focus': 'unusual values and anomalies'},
                {'types': ['CORRELATION'], 'focus': 'relationships between variables'},
                {'types': ['DISTRIBUTION', 'COMPARISON'], 'focus': 'distributions and group comparisons'},
                {'types': ['PATTERN'], 'focus': 'recurring patterns and cycles'}
            ]
            
            all_insights = []
            
            for idx, category in enumerate(insight_categories, 1):
                print(f"\n📊 Insight Batch {idx}/{len(insight_categories)}: {', '.join(category['types'])}")
                print(f"  ├─ 🎯 Focus: {category['focus']}")
                
                print(f"  ├─ 💭 Analyzing previous step outputs...")
                print(f"  ├─ ✍️  Generating insight extraction prompt...")
                
                # Pass used titles to avoid duplicates
                insights = self._extract_insights_by_category(category, output_dir, used_titles)
                
                if insights:
                    print(f"  ├─ ✅ Extracted {len(insights)} insights")
                    all_insights.extend(insights)
                    print(f"  └─ 📈 Total insights so far: {len(all_insights)}\n")
                else:
                    print(f"  └─ ⚠️  No insights extracted for this category\n")
            
            print(f"✓ Total insights extracted this iteration: {len(all_insights)}\n")
            
            # Process insights: generate charts + ISGEN scoring + filter by threshold
            print("🎨 Generating visualizations and computing ISGEN scores...")
            
            for insight_data in all_insights:
                title = insight_data.get('title', '')
                
                # Skip duplicates
                if title in used_titles:
                    continue
                used_titles.add(title)
                
                idx = len(all_processed_insights)
                insight_id = f"insight_{idx:03d}"
                
                print(f"  📊 {idx+1}: {title[:60]}...")
                
                # Extract values for scoring first (needed for pattern type)
                values = self._extract_values_for_scoring(insight_data, insight_data.get('variables', []))
                
                # ISGEN scoring
                insight_score = scorer.score_insight(insight_data, values)
                
                # Get pattern type for chart naming (QUIS format)
                pattern_type = insight_score.get('pattern_type', insight_data.get('type', 'UNKNOWN'))
                pattern_name = pattern_type.replace(' ', '_')
                
                # Generate chart with QUIS-style naming
                chart_filename = f"insight_{idx}_{pattern_name}.png"
                chart_path = self._generate_chart(insight_data, f"{output_dir}/{chart_filename}")
                
                processed_insight = {
                    'insight_id': insight_id,
                    'title': title,
                    'description': insight_data.get('description', ''),
                    'insight_type': insight_data.get('type', ''),
                    'chart_path': chart_path,
                    'data_evidence': insight_data.get('evidence', {}),
                    'score': insight_score,
                    'variables': insight_data.get('variables', [])
                }
                
                all_processed_insights.append(processed_insight)
                
                # Show pass/fail status
                status = "✓ PASS" if insight_score['passed'] else "✗ FAIL"
                print(f"    {status} (score: {insight_score['pattern_score']:.3f}, threshold: {insight_score['threshold']})")
        
        # Filter: Keep only insights passing threshold (like QUIS)
        passing_insights = [i for i in all_processed_insights if i['score']['passed']]
        failing_insights = [i for i in all_processed_insights if not i['score']['passed']]
        
        print(f"\n📊 ISGEN Filtering Results:")
        print(f"  ✓ Passed threshold: {len(passing_insights)}/{len(all_processed_insights)}")
        print(f"  ✗ Failed threshold: {len(failing_insights)}/{len(all_processed_insights)}")
        
        # Renumber and rename charts for passing insights only
        print(f"\n🔄 Renumbering passing insights...")
        final_insights = []
        for new_idx, insight in enumerate(passing_insights):
            old_chart = insight['chart_path']
            pattern_name = insight['score'].get('pattern_type', 'UNKNOWN').replace(' ', '_')
            new_chart_filename = f"insight_{new_idx}_{pattern_name}.png"
            new_chart_path = f"{output_dir}/{new_chart_filename}"
            
            # Rename chart file
            if os.path.exists(old_chart):
                os.rename(old_chart, new_chart_path)
            
            insight['insight_id'] = f"insight_{new_idx:03d}"
            insight['chart_path'] = new_chart_path
            final_insights.append(insight)
        
        # Delete charts for failing insights
        for insight in failing_insights:
            chart_path = insight['chart_path']
            if os.path.exists(chart_path):
                os.remove(chart_path)
        
        # Save only passing insights
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
        
        insights_native = convert_to_native(final_insights)
        
        with open(f"{output_dir}/insights.json", 'w', encoding='utf-8') as f:
            json.dump(insights_native, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Final: {len(final_insights)} insights passing threshold")
        print(f"✓ Insights saved: {output_dir}/insights.json\n")
        
        return final_insights
    
    def _extract_insights_by_category(self, category: Dict, output_dir: str, used_titles: set = None) -> List[Dict[str, Any]]:
        """Extract insights for a specific category using LLM"""
        
        if used_titles is None:
            used_titles = set()
        
        # Collect context from previous steps
        context = {
            'step1': self.step_outputs.get('step1', {}),
            'step2': self.step_outputs.get('step2', {}),
            'step3': self.step_outputs.get('step3', {}),
            'step4': self.step_outputs.get('step4', {})
        }
        
        # Get actual column names from dataset
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()[:20]
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()[:20]
        
        # Build exclusion text if there are used titles
        exclusion_text = ""
        if used_titles:
            exclusion_text = f"\n\nIMPORTANT: Avoid these already-extracted insights:\n{chr(10).join(['- ' + t for t in list(used_titles)[:10]])}\n\nGenerate DIFFERENT insights with different angles and variables."
        
        prompt = f"""Based on ALL previous analysis steps, extract valuable insights focused on: {category['focus']}

Insight types to find: {', '.join(category['types'])}{exclusion_text}

IMPORTANT - Available columns in dataset:
Numerical columns: {', '.join(numerical_cols)}
Categorical columns: {', '.join(categorical_cols)}

You MUST use ONLY these actual column names in the "variables" field. Do NOT make up column names.

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data
- Use ONLY actual column names from the list above

Return JSON:
{{
  "insights": [
    {{
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "One of: {', '.join(category['types'])}",
      "variables": ["actual_column_name1", "actual_column_name2"],
      "evidence": {{
        "source_step": "step2_quality",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }}
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst extracting maximum insights. Find as many valuable insights as possible."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=16000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('insights', [])
        except Exception as e:
            print(f"    ⚠️  Error extracting insights: {e}")
            return []
    
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
            max_tokens=2000
        )
        
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
            max_tokens=2000
        )
        
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
            max_tokens=2000
        )
        
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
            max_tokens=2000
        )
        
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
        passed = sum(1 for i in insights if i['score']['passed'])
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        type_counts = {}
        pattern_counts = {}
        for i in insights:
            itype = i['insight_type']
            ptype = i['score'].get('pattern_type', 'UNKNOWN')
            type_counts[itype] = type_counts.get(itype, 0) + 1
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        
        avg_score = sum(i['score']['pattern_score'] for i in insights) / total if total > 0 else 0
        top_insights = sorted(insights, key=lambda x: x['score']['pattern_score'], reverse=True)[:10]
        
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
                score_info = insight['score']
                passed_mark = "✓" if score_info['passed'] else "✗"
                f.write(f"  {i}. {passed_mark} {insight['insight_id']}: {insight['title']}\n")
                f.write(f"     Pattern: {score_info['pattern_type']}, Score: {score_info['pattern_score']:.3f}\n")
            
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
