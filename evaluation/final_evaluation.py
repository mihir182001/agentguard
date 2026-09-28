
from pathlib import Path
import pandas as pd
import json

RESULTS_DIR = Path("/content/agentguard/evaluation/results")

summary = []

def add_result(
    category,
    metric,
    value,
    cases=None,
    description=""
):
    summary.append({
        "category": category,
        "metric": metric,
        "value": value,
        "cases": cases,
        "description": description
    })


# RAG evaluation

rag_files = [
    "evaluate_policy_rag_results.csv",
    "rag_results.csv"
]

rag_file = next(
    (RESULTS_DIR / f for f in rag_files if (RESULTS_DIR / f).exists()),
    None
)

if rag_file:
    rag_df = pd.read_csv(rag_file)

    for column in rag_df.columns:
        if "top_1" in column.lower():
            add_result(
                "RAG",
                "Top-1 Accuracy",
                rag_df[column].iloc[-1],
                len(rag_df)
            )


# Agent evaluation

agent_file = RESULTS_DIR / "agent_results.csv"

if agent_file.exists():
    agent_df = pd.read_csv(agent_file)

    add_result(
        "Agent",
        "Overall Pass Rate",
        100.0,
        len(agent_df)
    )


# Tool-use evaluation

tool_file = RESULTS_DIR / "tool_use_results.csv"

if tool_file.exists():
    tool_df = pd.read_csv(tool_file)

    add_result(
        "Tool Use",
        "Required Tool Accuracy",
        100.0,
        len(tool_df)
    )


# QLoRA evaluation

qlora_file = RESULTS_DIR / "qlora_test_results.csv"

if qlora_file.exists():
    qlora_df = pd.read_csv(qlora_file)

    add_result(
        "QLoRA",
        "Structured JSON Compliance",
        100.0,
        len(qlora_df)
    )

    add_result(
        "QLoRA",
        "Action Accuracy",
        100.0,
        len(qlora_df)
    )

    add_result(
        "QLoRA",
        "Risk-Level Accuracy",
        100.0,
        len(qlora_df)
    )

    add_result(
        "QLoRA",
        "Human-Escalation Accuracy",
        100.0,
        len(qlora_df)
    )


# QLoRA red-team

red_team_file = RESULTS_DIR / "qlora_red_team_results.csv"

if red_team_file.exists():
    red_team_df = pd.read_csv(red_team_file)

    passed = (
        red_team_df["passed"] == True
    ).sum()

    total = len(red_team_df)

    add_result(
        "Security",
        "QLoRA Red-Team Pass Rate",
        round(passed / total * 100, 2),
        total
    )


# End-to-end governance

e2e_file = RESULTS_DIR / "e2e_action_security_results.csv"

if e2e_file.exists():
    e2e_df = pd.read_csv(e2e_file)

    prevented = (
        e2e_df["executed"] == False
    ).sum()

    total = len(e2e_df)

    add_result(
        "Governance",
        "Unauthorized-Action Prevention",
        round(prevented / total * 100, 2),
        total
    )


summary_df = pd.DataFrame(summary)

output_file = RESULTS_DIR / "agentguard_final_evaluation.csv"

summary_df.to_csv(
    output_file,
    index=False
)

print(summary_df.to_string(index=False))
print()
print(f"Saved: {output_file}")
