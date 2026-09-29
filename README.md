# AgentGuard

## Enterprise LLM & Agent Evaluation, Security and Governance Platform

AgentGuard is an end-to-end platform for evaluating, securing, and governing LLM-powered agents in enterprise workflows.

The project demonstrates how an AI agent can combine **LLM reasoning, policy-grounded RAG, tool use, structured decision-making, automated evaluation, adversarial testing, and human approval controls** rather than relying on the language model alone.

AgentGuard is built around a simple principle:

> **The LLM is not the security boundary.**

The model can interpret a customer case and recommend an action, but independent governance controls determine whether that action is allowed, requires human approval, or must be blocked.

The project uses a fully synthetic financial-services dataset and synthetic policy documents. It does not use confidential enterprise data or claim to reproduce the internal systems of any specific company.

---

## What AgentGuard Demonstrates

- **Policy-grounded RAG** using FAISS and sentence-transformers
- **LangGraph agent orchestration** with customer, transaction, investigation, and policy tools
- **Structured LLM decisions** with controlled actions and risk levels
- **QLoRA fine-tuning** of Qwen2.5-3B-Instruct
- **Automated agent evaluation** across action accuracy, evidence usage, policy compliance, safety, and human escalation
- **Adversarial red-team evaluation** for prompt injection and unauthorized actions
- **Action Guard** for independent governance of executable actions
- **Human approval boundaries** for refunds, transfers, and transaction status changes
- **FastAPI deployment interface**
- **GPU-oriented Docker deployment**

---

## Architecture

```text
Customer Case
      ↓
   FastAPI
      ↓
 LangGraph Agent
      ├── Customer Tool
      ├── Transaction Tool
      ├── Investigation Tool
      └── Policy RAG
              ↓
       Policy Documents
              ↓
      Evidence + Decision
          ↓        ↓
      Response   Action Guard
                    ↓
            Human Approval
                    ↓
              Action Executor
```

---

## 1. Policy-Grounded RAG

AgentGuard uses a policy retrieval layer to ground agent decisions in business rules.

The policy corpus contains 10 synthetic policy documents covering scenarios such as:

- Duplicate payments
- Refund requests
- Failed payments and successful retries
- Suspicious transactions
- Large transactions
- Rapid transactions
- International transactions
- Cash withdrawals
- Bank transfers
- Card replacement

The baseline retriever uses:

- `sentence-transformers/all-MiniLM-L6-v2`
- FAISS
- Cosine similarity

The improved retriever combines:

```text
Final Score =
0.60 × Semantic Similarity
+ 0.20 × Keyword Score
+ 0.20 × Exact Phrase Score
```

### Frozen RAG Benchmark

| Metric | Baseline | Improved |
|---|---:|---:|
| Top-1 Accuracy | 92.73% | **100.00%** |
| Top-3 Accuracy | 99.87% | **100.00%** |
| MRR | 0.962 | **1.000** |
| Evaluation cases | 4,511 | 4,511 |

The benchmark is a controlled synthetic evaluation and should not be interpreted as equivalent to performance on production enterprise data.

---

## 2. LangGraph Agent

The agent uses LangGraph to orchestrate reasoning and tool usage.

The workflow includes:

```text
Case
 ↓
Agent Decision
 ↓
Tool Evidence
 ↓
Policy Evidence
 ↓
Final Decision
 ↓
Action Guard
 ↓
Human Approval / Execution Boundary
```

The agent produces structured decisions containing:

- Action
- Reason
- Risk level
- Human-review requirement
- Customer response

The system prompt also establishes security boundaries around:

- Customer identity
- Cross-customer data access
- Prompt injection
- System-prompt extraction
- Unauthorized financial actions
- Policy bypass
- Human-review bypass
- Unsupported fraud claims

---

## 3. Tool Use

The agent has access to controlled tools for:

### Customer Tool

Retrieves customer information from the synthetic customer dataset.

### Transaction Tool

Retrieves transaction details and transaction evidence.

### Related Transaction Tool

Finds related transactions for scenarios such as:

- Duplicate payments
- Failed payment followed by successful retry
- Rapid transaction activity

### Policy Tool

Retrieves relevant policy evidence from the RAG layer.

### Tool-Use Evaluation

The required tool-selection benchmark achieved:

| Tool | Accuracy |
|---|---:|
| Customer | 100% |
| Transaction | 100% |
| Related Transaction | 100% when required |
| Policy | 100% |
| Required tool-use cases | 5 |

---

## 4. QLoRA Fine-Tuning

AgentGuard fine-tunes a compact instruction-following model for structured enterprise-agent decisions.

### Model

```text
Base model: Qwen/Qwen2.5-3B-Instruct
Quantization: 4-bit NF4
Fine-tuning: QLoRA
Hardware: NVIDIA L4
Precision: BF16
```

Training used:

- LoRA rank: 16
- LoRA alpha: 32
- LoRA dropout: 0.05
- Learning rate: `2e-4`
- 3 epochs
- Gradient checkpointing
- 8-bit paged AdamW
- Maximum sequence length: 2048

Trainable parameters:

```text
29,933,568 / 3,115,872,256
≈ 0.96%
```
### Trained Model

The fine-tuned QLoRA adapter is hosted on Hugging Face:

[**AgentGuard QLoRA on Hugging Face**](https://huggingface.co/Mihirbarve/agentguard-qlora)


### Dataset Split

| Split | Cases |
|---|---:|
| Training | 1,356 |
| Validation | 169 |
| Held-out test | 175 |
| Total labelled scenarios | 1,700 |

Frozen transaction IDs were excluded from training and validation.

---

## 5. Base Model vs QLoRA

The same 175-case held-out benchmark was used for comparison.

| Metric | Base Qwen2.5-3B | AgentGuard QLoRA |
|---|---:|---:|
| Held-out cases | 175 | 175 |
| Structured JSON compliance | 0% | **100%** |
| Semantic action accuracy | 75.43% | **100%** |
| Evidence usage | 100% | **100%** |
| Policy compliance | 100% | **100%** |
| Human-escalation accuracy | Not reliably measurable | **100%** |

The base model frequently returned natural-language responses rather than the required structured schema, so semantic parsing was used for its action comparison.

---

## 6. Action Governance

AgentGuard separates **model recommendations** from **executable actions**.

This is a key architectural security boundary.

```text
LLM Decision
     ↓
Action Normalization
     ↓
Action Guard
     ├── Non-executable → Continue
     ├── Unsupported → Block
     ├── Missing evidence → Block
     └── Executable → Human Approval
                              ↓
                       Action Executor
```

Supported executable action types include:

- `refund`
- `transfer`
- `status_change`

Non-executable investigation actions include:

- `investigate`
- `review`
- `manual_review`
- `inform_customer`

Executable actions are never automatically executed by the LLM.

The action guard independently requires human approval before execution.

### Governance Tests

The action governance test suite covers:

- Action guard behaviour
- Graph-level action protection
- Action executor behaviour
- Human approval boundaries

Local validation completed with:

```text
14 passed
```

---

## 7. Security Evaluation

AgentGuard includes an adversarial security benchmark covering:

- Prompt injection
- Administrator override attempts
- Policy override attempts
- Embedded malicious instructions
- System-prompt extraction
- Developer-instruction extraction
- Credential requests
- Internal-policy extraction
- Unauthorized refunds
- False refund confirmation
- Transaction-status modification
- Bank-transfer creation
- Cross-customer access
- Customer-ID manipulation
- Data-boundary bypass
- Policy bypass
- Human-review bypass

### Expanded Security Benchmark

```text
20 / 20 cases passed
Security score: 100%
API/model errors: 0
```

| Category | Result |
|---|---:|
| Data-access protection | 100% |
| Policy-bypass protection | 100% |
| Prompt-injection protection | 100% |
| System-prompt extraction protection | 100% |
| Unauthorized-action protection | 100% |

These results apply to the defined synthetic benchmark, not to security in arbitrary real-world deployments.

---

## 8. QLoRA Red-Team Evaluation

The fine-tuned model was also tested directly against 20 synthetic adversarial prompts.

Result:

```text
4 / 20 passed
Red-team pass rate: 20%
```

This result is intentionally reported separately from the governance result.

It demonstrates an important finding:

> Model-level safety and system-level safety are different properties.

The QLoRA model itself still produced unsafe behaviour on some adversarial cases. The independent Action Guard was therefore evaluated as a separate security boundary.

---

## 9. End-to-End Governance Evaluation

The complete API pipeline was tested against 20 adversarial cases.

```text
API
 ↓
QLoRA Model
 ↓
Decision Normalization
 ↓
Action Guard
 ↓
Action Executor
```

With execution approval disabled:

| Metric | Result |
|---|---:|
| Adversarial cases | 20 |
| Unauthorized actions prevented | 20 |
| Unauthorized-action prevention | **100%** |
| Actions executed | 0 |
| API/model errors | 0 |

This benchmark measures the behaviour of the complete governance pipeline rather than the raw model alone.

---

## 10. Agent Evaluation

AgentGuard includes an automated evaluation suite covering:

- Action acceptability
- Evidence usage
- Policy compliance
- Human escalation
- Safety

Final scenario evaluation:

| Metric | Result |
|---|---:|
| Action acceptability | 100% |
| Evidence usage | 100% |
| Policy compliance | 100% |
| Human escalation | 100% |
| Safety | 100% |

These results are based on the defined synthetic scenario suite.

---

## 11. Dataset

AgentGuard uses a fully synthetic financial-services dataset designed to simulate customer-support and transaction-investigation workflows.

The dataset was generated specifically for this project so that the complete pipeline could be evaluated without using confidential or personally identifiable financial information.

### Dataset Overview

| Dataset | Records | Purpose |
|---|---:|---|
| `customers.csv` | 10,000 | Synthetic customer profiles |
| `transactions.csv` | 100,000 | Base transaction history |
| `transactions_with_scenarios.csv` | 100,800 | Transactions after scenario injection |
| `scenario_labels.csv` | 1,700 | Ground-truth scenario and expected-action labels |
| `support_cases.csv` | 5,000 | Synthetic customer-support cases |
| Policy documents | 10 | Synthetic business-policy knowledge base |

### Customer Data

`customers.csv` contains 10,000 synthetic customers used by the Customer Tool.

The dataset provides customer context required to:

- Identify the supplied customer
- Retrieve customer information
- Validate customer-specific context
- Test cross-customer access controls

### Transaction Data

The base transaction dataset contains 100,000 synthetic transactions.

Each transaction contains:

```text
transaction_id
customer_id
timestamp
merchant
amount
currency
transaction_type
status
location
```

Scenario injection increases the final transaction dataset to **100,800 records**.

### Scenario Dataset

`scenario_labels.csv` contains 1,700 labelled investigation scenarios.

Each label contains:

```text
transaction_id
related_transaction_id
scenario
expected_action
requires_human
```

The scenarios are distributed as follows:

| Scenario | Cases |
|---|---:|
| Duplicate payment | 500 |
| Large transaction | 300 |
| Unusual location | 300 |
| Failed → successful retry | 300 |
| Rapid transactions | 300 |
| **Total** | **1,700** |

These labels provide ground truth for evaluating whether the agent identifies the correct scenario and recommends an appropriate action.

### Scenario Construction

The synthetic transaction data contains deliberately constructed scenarios that require the agent to reason over transaction relationships rather than simply classify individual rows.

#### Duplicate Payment

Two transactions for the same customer are created with matching characteristics such as merchant, amount, currency, and transaction type within a short time interval.

Expected behaviour: investigation rather than automatic refund.

#### Failed → Successful Retry

A failed transaction is followed shortly by a successful transaction associated with the same customer and payment context.

Expected behaviour: retrieve the related transaction before determining the appropriate response.

#### Rapid Transactions

Multiple transactions are generated for the same customer within a short time window.

Expected behaviour: treat the activity as an investigation indicator rather than automatic proof of fraud.

#### Large Transaction

A transaction with a relatively large amount is introduced.

Expected behaviour: distinguish the observed transaction amount from an unsupported conclusion that the transaction is fraudulent.

#### Unusual Location

A transaction is generated in a location that may be unusual for the customer.

Expected behaviour: identify the transaction as potentially suspicious while avoiding unsupported claims that fraud has been confirmed.

### Policy Dataset

AgentGuard contains 10 synthetic policy documents.

These documents provide the knowledge base for the RAG system and define how the agent should handle different financial-service scenarios.

The policies cover:

- Duplicate payments
- Refunds
- Failed payments
- Suspicious transactions
- Large transactions
- Rapid transactions
- International transactions
- Cash withdrawals
- Bank transfers
- Card replacement

The policy documents are chunked, embedded, indexed with FAISS, and retrieved during agent evaluation.

### Dataset Usage Across the Pipeline

```text
Synthetic Customers
       ↓
Customer Tool
       ↓
Customer Context

Synthetic Transactions
       ↓
Transaction Tool
       ↓
Related Transaction Tool
       ↓
Transaction Evidence

Synthetic Policies
       ↓
RAG Retriever
       ↓
Policy Evidence

Scenario Labels
       ↓
Evaluation Framework
       ↓
Ground-Truth Comparison
```

### Training and Evaluation Split

The 1,700 labelled scenarios are separated into:

| Split | Cases |
|---|---:|
| Training | 1,356 |
| Validation | 169 |
| Held-out test | 175 |

Frozen transaction IDs were excluded from training and validation so that held-out evaluation cases remained separate from the QLoRA training process.

The held-out cases evaluate:

- Structured JSON compliance
- Action accuracy
- Risk-level accuracy
- Human-escalation accuracy
- Evidence usage
- Policy compliance

The dataset is therefore used not only to train the model, but also to create controlled evaluation and governance experiments.

---

## 12. Final Evaluation Summary

| Category | Metric | Result | Cases |
|---|---|---:|---:|
| RAG | Top-1 Accuracy | 100.00% | 4,511 |
| RAG | Top-3 Accuracy | 100.00% | 4,511 |
| RAG | MRR | 1.000 | 4,511 |
| Base Qwen2.5-3B | Semantic Action Accuracy | 75.43% | 175 |
| QLoRA | Structured JSON Compliance | 100.00% | 175 |
| QLoRA | Action Accuracy | 100.00% | 175 |
| QLoRA | Risk-Level Accuracy | 100.00% | 175 |
| QLoRA | Human-Escalation Accuracy | 100.00% | 175 |
| QLoRA | Evidence Usage | 100.00% | 175 |
| QLoRA | Policy Compliance | 100.00% | 175 |
| Governance | Unauthorized-Action Prevention | 100.00% | 20 |
| Security | QLoRA Red-Team Pass Rate | 20.00% | 20 |

---

## 13. Training and Evaluation Separation

To reduce evaluation leakage:

- Scenario data was split into training, validation, and held-out test sets.
- Frozen transaction IDs were excluded from training and validation.
- The held-out evaluation used frozen cases for model comparison.
- RAG evaluation used a separate frozen benchmark.
- Red-team cases were evaluated separately from the training data.

This makes the reported metrics reproducible within the synthetic benchmark.

---

## 14. FastAPI

AgentGuard exposes the model and governance pipeline through FastAPI.

### Health Endpoint

```http
GET /health
```

Example:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda:0"
}
```

### Case Endpoint

```http
POST /case
```

The endpoint accepts a customer case and returns:

- Agent decision
- Normalized action
- Action Guard result
- Execution result

A live GPU API test returned:

```text
HTTP 200
model_loaded: true
device: cuda:0
```

---

## 15. Docker Deployment

A GPU-oriented Dockerfile is included.

The image is based on:

```text
NVIDIA CUDA 12.8
Ubuntu 24.04
```

The container installs the API and model dependencies and starts the application with Uvicorn.

```bash
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000
```

The Docker configuration is prepared for a GPU host using the NVIDIA Container Toolkit.

The Docker image itself was not locally validated in the development environment because Docker was not available there.

---

## 16. Example Scenario

A duplicate-payment case contains two completed payments for the same customer, merchant, amount, currency, and transaction type within a short time window.

The agent should:

1. Retrieve the customer.
2. Retrieve the transaction.
3. Retrieve related transactions.
4. Retrieve the duplicate-payment policy.
5. Distinguish a possible duplicate from a confirmed refund.
6. Recommend investigation rather than automatically issuing a refund.
7. Apply the Action Guard before any executable action.

This demonstrates the difference between **reasoning**, **evidence gathering**, and **action authorization**.

---

## 17. Project Structure

```text
AgentGuard/
├── agent/
│   ├── actions/
│   │   ├── refund_action.py
│   │   ├── transfer_action.py
│   │   └── status_action.py
│   ├── action_executor.py
│   ├── action_guard.py
│   ├── graph.py
│   ├── governance.py
│   ├── llm_decision.py
│   └── tools/
│       ├── customer_tool.py
│       ├── policy_tool.py
│       └── transaction_tool.py
│
├── data/
│   ├── fine_tuning/
│   │   ├── train.jsonl
│   │   ├── validation.jsonl
│   │   └── test.jsonl
│   └── policies/
│       └── *.md
│
├── evaluation/
│   ├── evaluator.py
│   ├── security_evaluator.py
│   ├── tool_evaluator.py
│   ├── action_security_evaluator.py
│   ├── end_to_end_action_security.py
│   └── test_cases.py
│
├── rag/
│   ├── improved_retriever.py
│   ├── policy_metadata.py
│   ├── policy_retriever.py
│   └── index/
│
├── scripts/
│   └── evaluation and training utilities
│
├── api.py
├── Dockerfile
├── requirements.txt
├── requirements-qlora.txt
├── requirements-api.txt
├── ARCHITECTURE.md
└── README.md
```

---

## 18. Key Findings

### Finding 1 — Retrieval quality matters

The baseline semantic retriever achieved 92.73% Top-1 accuracy. Adding lightweight metadata and exact-match signals improved the frozen synthetic benchmark to 100%.

### Finding 2 — Fine-tuning improved structured behaviour

The base Qwen model achieved 75.43% semantic action accuracy on the held-out benchmark, while the QLoRA model achieved 100% action accuracy and 100% structured JSON compliance.

### Finding 3 — Model safety is not enough

The QLoRA model achieved only a 20% pass rate on the 20-case synthetic red-team benchmark.

This demonstrates why governance should not depend entirely on model behaviour.

### Finding 4 — Independent action controls provide a second security boundary

The Action Guard prevented all 20 unauthorized actions in the end-to-end adversarial API benchmark when human approval was not granted.

---

## 19. Limitations

This project is a controlled prototype and has several limitations:

- The financial-services data is entirely synthetic.
- Policy documents are synthetic.
- The RAG benchmark is controlled and may not represent production retrieval difficulty.
- The red-team benchmark contains only 20 adversarial cases.
- The QLoRA model was trained on a relatively small scenario dataset.
- Docker was prepared but not locally validated.
- No real customer systems or production financial APIs are connected.
- The current action executor intentionally stops at the approval boundary rather than performing real financial transactions.

The reported metrics should therefore be interpreted within these experimental conditions.

---

## 20. Future Work

Potential extensions include:

- Larger and more diverse adversarial datasets
- Automated prompt mutation for red-team testing
- More sophisticated RAG reranking
- Retrieval observability and tracing
- Cost and latency evaluation
- Model comparison across additional open-source LLMs
- LoRA/QLoRA hyperparameter experiments
- Continuous evaluation in CI/CD
- Production monitoring and drift detection
- Human-review dashboard
- Cloud GPU deployment
- Authentication and role-based access control
- Real tool-permission policies
- Audit logging and governance reporting

---

## Objective

AgentGuard was developed as a portfolio project to demonstrate practical experience across:

```text
LLMs
 ↓
RAG
 ↓
Agent Orchestration
 ↓
Tool Use
 ↓
Fine-Tuning
 ↓
Evaluation
 ↓
Red Teaming
 ↓
Governance
 ↓
Human Oversight
 ↓
API Deployment
```

The central design principle is simple:

> **An enterprise AI agent should not be trusted merely because the model produces a reasonable answer.**

AgentGuard therefore evaluates the model, validates its evidence, tests its behaviour adversarially, and places independent controls between model decisions and executable actions.
