from __future__ import annotations

from .models import InsightCard, TableSchema

# --- Figure 7: Natural Language Statistics Prompt (paper Appendix) ---
STATS_PROMPT_TEMPLATE = """Basic Statistical Questions
What statistical metrics would you like to know about the following database?

Example Schema (zomato):
[STAT] What is the name of the restaurant with high number of reviews? [/STAT]
[STAT] What is the name of the restaurant with the most diverse cuisine? [/STAT]
[STAT] What are the different cuisines present? [/STAT]
[STAT] What are the total number of tables in hotels and airbnbs? [/STAT]

Here is the schema to use:
{table_schema}

INSTRUCTIONS:
- list the stats within the [STAT] and end with [/STAT] tags, e.g:
[STAT] How many restaurants are in the table? [/STAT]
- Don't write anything other than the STAT
"""


def build_stats_prompt(table_schema: TableSchema) -> str:
    return STATS_PROMPT_TEMPLATE.format(table_schema=table_schema.to_prompt_string())


# --- Figure 6: QUGen main prompt template ---
TASK_DESCRIPTION = """Task Description : The task is to analyze a table (presented as its schema) for the purpose of Exploratory Data Analysis. Having examined the schema, you have to generate meaningful questions, and corresponding to each question a breakdown, measure and a reason. This piece of information will be further processed to generate interesting and relevant insights from the table.

An insight is interesting if it helps identify one or more of the following:
Meaningful relationships between variables, trends, influence of one variable over the other, anomalies or outliers."""

INSTRUCTIONS = """Instructions :
1) Understand the Schema: Review the schema carefully to understand the data structure and types of columns available.
2) Identify Insights: Think about the different types of insights we want to uncover, such as relationships between columns, trends or anomalies. Use the provided schema and natural language stats to identify relevant and meaningful insights.
3) Formulate Questions: Based on the insights, formulate questions that can reveal meaningful information. Ensure that the questions are unique, relevant and not a repetition of the examples. Do not use questions related to simple data statistics (e.g., maximum length of a column).
4) Identify breakdown and measure dimensions for the question:
Insights are obtained when a measure is compared across a breakdown dimension.
The measure is a quantity of interest expressed in terms of variables of the table. It consists of
- A measure function (aggregation) - COUNT, MEAN, MIN, MAX
- A measure column - a numerical column of the table
The breakdown dimension is a variable of the table across which we would like to compare values of measure to obtain meaningful insights.
If the breakdown or measure dimension is absent in the question, generate relevant and related dimensions from the schema which can help provide a good insight.
5) Formulate a Reason: Explain what makes the question insightful and mention the reason for why the selected measure and breakdown can give a good insight. Explain why the combination of the question, breakdown and measure can help identify meaningful relationships between variables, or showcase trends, or identify outliers/anomalies.
6) Use [INSIGHT] Tags: Format each question using the [INSIGHT] and [/INSIGHT] tags."""


MEASURE_DIVERSITY_INSTRUCTION = """CRITICAL — Measure Diversity Rule:
Each Insight Card MUST use a DIFFERENT measure column. Do NOT repeat the same measure column across multiple cards.
Spread your questions across as many different numerical columns as possible (e.g. revenue, cost, weight, frequency, distance, satisfaction score, profit margin, etc.).
If you have N questions, aim for at least N different measure columns."""


def _format_example(schema_str: str, cards: list[InsightCard]) -> str:
    parts = [f"[EXAMPLE TABLE SCHEMA]\n{schema_str}\n[OUTPUT]"]
    for i, c in enumerate(cards, 1):
        parts.append(f"Insight Card {i}\n{c.to_prompt_string()}")
    parts.append("[/OUTPUT]")
    return "\n".join(parts)


def build_qugen_prompt(
    table_schema: TableSchema,
    natural_language_stats: str,
    example_schemas_and_cards: list[tuple[TableSchema, list[InsightCard]]],
    num_questions: int = 10,
    used_measures: list[str] | None = None,
) -> str:
    """
    Build the full QUGEN prompt (Figure 6).
    example_schemas_and_cards: few-shot examples (schema + list of Insight Cards).
    used_measures: measure columns already used in previous iterations (for diversity).
    """
    parts = [
        TASK_DESCRIPTION,
        INSTRUCTIONS,
        "Examples :",
    ]
    for schema, cards in example_schemas_and_cards:
        parts.append(_format_example(schema.to_prompt_string(), cards))

    parts.append("Test Dataset :")
    parts.append("This is the information for the dataset you have to work on:")
    parts.append("Schema")
    parts.append(f"[Test Table SCHEMA]\n{table_schema.to_prompt_string()}")
    parts.append("NATURAL LANGUAGE STATS:")
    parts.append(natural_language_stats)
    parts.append("")

    diversity_hint = MEASURE_DIVERSITY_INSTRUCTION
    if used_measures:
        avoid_list = ", ".join(sorted(set(used_measures)))
        diversity_hint += f"\nMeasure columns already covered: [{avoid_list}]. Strongly prefer OTHER numerical columns not in this list."

    parts.append(diversity_hint)
    parts.append("")
    parts.append(f"Please proceed to generate {num_questions} unique and insightful questions based on the provided schema and instructions.")
    parts.append("Format each Insight Card with REASON:, QUESTION:, BREAKDOWN:, MEASURE: and wrap each card in [INSIGHT] and [/INSIGHT] tags.")

    return "\n".join(parts)
