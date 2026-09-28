# AgentGuard

## Enterprise LLM & Agent Evaluation, Security and Governance Platform

AgentGuard is a synthetic financial-services AI platform for evaluating and governing LLM-powered agents.

The project combines:

- Policy-grounded RAG
- LangGraph agent orchestration
- Tool use
- Structured LLM decision-making
- QLoRA fine-tuning
- Automated evaluation
- Red-team security testing
- Action governance
- Human approval boundaries
- End-to-end unauthorized-action prevention

The central design principle is:

> **The LLM is not the security boundary.**

The model can recommend an action, but executable financial or transaction-changing actions must pass through an independent governance layer.

## Architecture

```text
Customer Case
     |
     v
  FastAPI
     |
     v
LangGraph Agent
     |
     +----------------+----------------+
     |                |                |
     v                v                v
Customer Tool   Transaction Tool   Policy RAG
     |                |                |
     v                v                v
Customer DB    Transaction DB    Policy Docs
     |                |                |
     +----------------+----------------+
                      |
                      v
               Agent Decision
                      |
                      v
                Action Guard
                  /       \
                 /         \
                v           v
           Blocked      Human Approval
                              |
                              v
                       Action Executor
```

## Problem

Enterprise LLM agents can generate useful decisions but introduce risks when they:

- follow malicious instructions
- access data belonging to another customer
- bypass policies
- execute unauthorized financial actions
- incorrectly confirm transactions
- expose system or developer instructions
- bypass human review

AgentGuard evaluates these behaviours separately from model capability and places a deterministic governance layer between model decisions and executable actions.

## Core Components

### 1. Policy RAG

The system retrieves relevant synthetic financial policies using semantic retrieval with FAISS and sentence-transformer embeddings.

The improved retriever combines:

- semantic similarity
- keyword matching
- exact phrase matching

The frozen evaluation benchmark contains 4,511 synthetic policy-retrieval cases.

### 2. Agent Orchestration

The agent uses LangGraph to coordinate:

- customer lookup
- transaction lookup
- related-transaction analysis
- policy retrieval
- structured decision generation
- action governance

### 3. Tool Use

The agent can access controlled tools for:

- customer information
- transaction information
- related transactions
- policy retrieval

### 4. QLoRA Fine-Tuning

Qwen2.5-3B-Instruct was fine-tuned using QLoRA for structured enterprise case decision-making.

Target output schema:

```json
{
  "action": "...",
  "reason": "...",
  "risk_level": "...",
  "requires_human": true,
  "customer_response": "..."
}
```

The training dataset contains synthetic financial-support scenarios covering:

- duplicate payments
- large transactions
- unusual locations
- failed-successful retries
- rapid transactions

Frozen evaluation examples were excluded from training.

### 5. Action Governance

Executable actions are separated from informational actions.

Supported executable action types include:

- refund
- transfer
- status change

The Action Guard checks:

1. whether the action is supported
2. whether customer identity is available
3. whether supporting evidence exists
4. whether human approval is required

The executor does not execute executable actions without explicit approval.

## Evaluation

### RAG Evaluation

| Metric | Result | Cases |
|---|---:|---:|
| Top-1 Accuracy | 100.00% | 4,511 |
| Top-3 Accuracy | 100.00% | 4,511 |
| MRR | 1.000 | 4,511 |

These results are from the frozen synthetic policy-retrieval benchmark.

### Base Model vs QLoRA

| Metric | Base Qwen2.5-3B | AgentGuard QLoRA |
|---|---:|---:|
| Held-out cases | 175 | 175 |
| Semantic action accuracy | 75.43% | 100.00% |
| Structured JSON compliance | 0% | 100.00% |
| Evidence usage | 100% | 100.00% |
| Policy compliance | 100% | 100.00% |
| Human-escalation accuracy | Not reliably measurable | 100.00% |

The base-model structured JSON score is not treated as a model capability score because the base model produced natural-language decisions rather than the required structured output format.

### QLoRA Evaluation

On 175 held-out synthetic cases:

| Metric | Result |
|---|---:|
| Structured JSON compliance | 100.00% |
| Action accuracy | 100.00% |
| Risk-level accuracy | 100.00% |
| Human-escalation accuracy | 100.00% |
| Evidence usage | 100.00% |
| Policy compliance | 100.00% |

These results apply specifically to the synthetic held-out benchmark.

## Security Evaluation

### Model-Level Red Team

The fine-tuned model was tested against 20 synthetic adversarial prompts covering:

- prompt injection
- system prompt extraction
- credential requests
- internal information requests
- unauthorized refunds
- unauthorized status changes
- transfer creation
- customer-data boundary violations
- cross-customer access
- policy bypass
- human-review bypass

**QLoRA red-team pass rate: 4 / 20 — 20%.**

This demonstrates that fine-tuning alone does not provide a sufficient security boundary.

### Governance-Level Security

The same adversarial model outputs were passed through:

```text
QLoRA Model
     |
     v
Action Guard
     |
     v
Action Executor
```

The system prevented unauthorized execution in:

**20 / 20 cases — 100%.**

The executor was tested without human approval.

## Security Design

AgentGuard follows a defense-in-depth approach.

```text
User
 |
 v
LLM
 |
 | potentially unsafe decision
 v
Action Guard
 |
 +---- unsupported action ----> BLOCK
 |
 +---- missing evidence ------> BLOCK
 |
 +---- executable action -----> HUMAN APPROVAL
 |
 v
Action Executor
 |
 v
Execution
```

The model therefore cannot directly authorize a financial or transaction-changing operation.

## Synthetic Data

The project uses synthetic data rather than real customer or financial information.

Dataset components include:

- 10,000 synthetic customers
- 100,800 synthetic transactions
- 1,700 scenario labels
- 5,000 synthetic support cases
- synthetic policy documents

## Technology Stack

### Machine Learning

- Python
- PyTorch
- Hugging Face Transformers
- PEFT
- QLoRA
- bitsandbytes
- sentence-transformers

### LLM / Agent

- Qwen2.5-3B-Instruct
- LangGraph
- Groq
- Pydantic

### Retrieval

- FAISS
- Sentence Transformers

### API / Backend

- FastAPI
- SQLAlchemy
- Pydantic

### Evaluation

- Pandas
- Python evaluation pipelines
- Synthetic benchmark datasets
- Red-team evaluation

### Training Hardware

QLoRA training was performed on a Google Colab NVIDIA L4 GPU.

## Project Structure

```text
Agentguard/
├── agent/
│   ├── actions/
│   ├── tools/
│   ├── prompts/
│   ├── tests/
│   ├── action_guard.py
│   ├── action_executor.py
│   ├── graph.py
│   └── llm_decision.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── policies/
│   └── fine_tuning/
│
├── evaluation/
│   ├── results/
│   ├── evaluator.py
│   ├── test_cases.py
│   ├── tool_evaluator.py
│   ├── security_evaluator.py
│   └── final_evaluation.py
│
├── rag/
│   ├── policy_retriever.py
│   ├── improved_retriever.py
│   ├── policy_metadata.py
│   └── index/
│
├── scripts/
│   ├── generate_data.py
│   ├── generate_transactions.py
│   ├── inject_scenarios.py
│   ├── validate_scenarios.py
│   ├── generate_support_cases.py
│   ├── evaluate_policy_rag.py
│   ├── analyze_rag_errors.py
│   └── evaluate_improved_rag.py
│
└── README.md
```

## Key Engineering Findings

### RAG

The improved retrieval approach achieved perfect retrieval metrics on the frozen synthetic benchmark.

### Fine-Tuning

QLoRA improved structured enterprise decision-making compared with the base model on the held-out benchmark.

### Security

The fine-tuned model remained vulnerable to adversarial prompts.

### Governance

A deterministic Action Guard separated model decisions from executable actions and prevented unauthorized execution across the tested adversarial cases.

This supports the architectural principle that LLM output should be treated as an untrusted decision proposal when it can lead to consequential actions.

## Limitations

The evaluation results are based on synthetic data and controlled benchmarks.

They should not be interpreted as evidence of production-level performance or security in a real financial institution.

The project does not use real customer information, confidential bank policies, or proprietary financial data.

The security benchmark is limited to the defined adversarial test cases and does not establish complete security coverage.

## Future Work

- FastAPI production interface
- Docker containerisation
- cloud deployment
- CI/CD evaluation pipeline
- experiment tracking
- agent tracing
- latency and cost monitoring
- larger adversarial benchmark
- automated regression testing
- human-in-the-loop approval UI
- model and policy versioning
- production observability

## Project Objective

AgentGuard demonstrates an end-to-end approach to building, evaluating and governing LLM-powered agents:

```text
Data
 ↓
RAG
 ↓
Agent
 ↓
Tool Use
 ↓
QLoRA
 ↓
Evaluation
 ↓
Red Teaming
 ↓
Governance
 ↓
Human Approval
 ↓
Execution
```