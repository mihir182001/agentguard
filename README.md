The system separates **decision-making** from **action execution**.

This allows the LLM to produce a structured decision while preventing the model from directly executing consequential operations.

---

## Core Components

### 1. Policy-Grounded RAG

AgentGuard retrieves relevant synthetic financial-services policies before making decisions.

The retrieval pipeline uses:

-  Sentence Transformers 
-  FAISS 
-  Semantic similarity 
-  Policy-specific metadata 
-  Keyword matching 
-  Exact phrase signals 

The improved retriever combines semantic and lexical evidence to rank policy passages.

### Retrieval Benchmark

| Metric         | Result      | Cases |
| -------------- | ----------- | ----- |
| Top-1 Accuracy | **100.00%** | 4,511 |
| Top-3 Accuracy | **100.00%** | 4,511 |
| MRR            | **1.00**    | 4,511 |

The results are from a controlled synthetic benchmark and should not be interpreted as production retrieval performance.

---

## 2. LangGraph Agent

The agent uses LangGraph to coordinate:

-  Customer lookup 
-  Transaction lookup 
-  Related transaction investigation 
-  Policy retrieval 
-  Structured decision generation 
-  Action governance 

The agent produces a structured decision containing:

```
```

```
action
reason
risk_level
requires_human
customer_response
```

The decision is treated as a proposal rather than an authorization to execute an action.

---

## 3. Tool Use

AgentGuard provides tools for customer lookup, transaction lookup, related transaction investigation, and policy retrieval.

Related transaction lookup is particularly important for duplicate payments, failed-payment retries, and rapid transaction scenarios.

---

## 4. QLoRA Fine-Tuning

AgentGuard fine-tunes `Qwen/Qwen2.5-3B-Instruct` using QLoRA.

Training was performed on a Google Colab NVIDIA L4 GPU using:

-  4-bit NF4 quantization 
-  LoRA adapters 
-  BF16 computation 
-  Gradient checkpointing 
-  8-bit paged AdamW 

The adapter trains approximately 29.9M parameters, or 0.96% of the base model.

### Dataset

The synthetic scenario dataset contains:

-  1,700 labelled investigation scenarios 
-  1,356 training examples 
-  169 validation examples 
-  175 held-out test examples 

The scenarios include duplicate payments, large transactions, unusual locations, failed-to-successful retries, and rapid transactions.

---

## 5. Base Model vs QLoRA

| Metric                     | Base Qwen2.5-3B         | AgentGuard QLoRA |
| -------------------------- | ----------------------- | ---------------- |
| Held-out cases             | 175                     | 175              |
| Structured JSON compliance | 0%                      | **100%**         |
| Semantic action accuracy   | 75.43%                  | **100%**         |
| Evidence usage             | 100%                    | **100%**         |
| Policy compliance          | 100%                    | **100%**         |
| Human-escalation accuracy  | Not reliably measurable | **100%**         |

The comparison focuses on structured enterprise decision behaviour rather than general language-model capability.

---

## 6. Action Governance

A core part of AgentGuard is the deterministic **Action Guard**.

The model cannot directly execute financial or transaction-changing actions.

```
```

```
LLM Decision
     |
     v
Action Normalization
     |
     v
Action Guard
     |
     +-----------------------------+
     |                             |
     v                             v
Non-executable                 Executable
     |                             |
     v                             v
Allowed                    Human Approval Required
                                   |
                                   v
                            Action Executor
```

Supported executable action interfaces include:

-  Refund 
-  Transfer 
-  Transaction status change 

These actions do not execute automatically.

The Action Guard independently verifies:

-  Supported action 
-  Customer identity 
-  Supporting evidence 
-  Human approval requirement 

This creates a separation between what the model recommends and what the system is permitted to execute.

---

## 7. Security and Red-Team Evaluation

AgentGuard includes adversarial evaluation covering:

-  Prompt injection 
-  System prompt extraction 
-  Developer instruction extraction 
-  Credential requests 
-  Policy bypass 
-  Unauthorized refunds 
-  Unauthorized transfers 
-  Transaction status changes 
-  Cross-customer data access 
-  Customer ID manipulation 
-  Human-review bypass 
-  Duplicate-payment policy bypass 
-  Rapid-transaction policy bypass 

### Model Red-Team Benchmark

| Metric                   | Result         |
| ------------------------ | -------------- |
| Adversarial cases        | 20             |
| QLoRA red-team pass rate | **20% (4/20)** |

The result demonstrates that the fine-tuned model can still produce unsafe behaviour under adversarial prompting.

This supports the design principle that model alignment alone is not sufficient as an action-security boundary.

---

## 8. End-to-End Governance Security

The same adversarial cases were passed through:

```
```

```
LLM
 ↓
Action Normalization
 ↓
Action Guard
 ↓
Action Executor
```

with execution approval disabled.

| Metric                         | Result      |
| ------------------------------ | ----------- |
| Adversarial cases              | 20          |
| Unauthorized actions prevented | **20 / 20** |
| Unauthorized-action prevention | **100%**    |
| Execution errors               | **0**       |

This benchmark measures the tested governance path, not overall system security.

---

## 9. Agent Evaluation

The AgentGuard evaluation framework measures:

-  Action acceptability 
-  Evidence usage 
-  Policy compliance 
-  Human escalation 
-  Safety 

| Metric               | Result   |
| -------------------- | -------- |
| Action acceptability | **100%** |
| Evidence usage       | **100%** |
| Policy compliance    | **100%** |
| Human escalation     | **100%** |
| Safety               | **100%** |

These results are based on the defined synthetic evaluation cases.

---

## 10. Training and Evaluation Separation

AgentGuard separates training data from evaluation data.

The evaluation pipeline separately measures:

```
```

```
Retrieval
   ↓
Agent Decision
   ↓
Tool Use
   ↓
Security
   ↓
Governance
```

This makes it possible to identify whether an error originates from retrieval, model decision-making, tool selection, or action governance.

---

## 11. API

AgentGuard includes a FastAPI inference interface.

Endpoints:

```
```

```
GET  /health
POST /case
```

The API:

1.  Loads the QLoRA adapter 
2.  Accepts a customer case 
3.  Generates a structured model decision 
4.  Normalizes the requested action 
5.  Passes the action through the Action Guard 
6.  Passes the result to the Action Executor 
7.  Returns the decision and governance result 

A live GPU API test successfully returned:

```
```

```
status: healthy
model_loaded: true
device: cuda:0
```

The API is designed as a portable inference prototype rather than a production financial-services API.

---

## 12. Docker

A GPU-oriented Docker configuration is included using:

-  NVIDIA CUDA 12.8 
-  Ubuntu 24.04 
-  Python 3 
-  FastAPI 
-  Uvicorn 
-  Transformers 
-  PEFT 
-  bitsandbytes 
-  PyTorch 

The Docker configuration is prepared for NVIDIA GPU environments.

The Docker image has not been presented as locally validated. Cloud deployment and production infrastructure remain future work.

---

## 13. Synthetic Data

The project uses entirely synthetic financial-services data.

The generated data includes:

-  Customers 
-  Transactions 
-  Support cases 
-  Scenario labels 
-  Synthetic policy documents 

Controlled scenarios include:

-  duplicate_payment 
-  large_transaction 
-  unusual_location 
-  failed_successful_retry 
-  rapid_transactions 

The project does not use real customer information, confidential bank policies, proprietary financial data, or real transaction records.

---

## 14. Project Structure

```
```

```
Agentguard/
|
+-- agent/
|   +-- actions/
|   +-- tools/
|   +-- tests/
|   +-- action_guard.py
|   +-- action_executor.py
|   +-- graph.py
|   +-- llm_decision.py
|
+-- data/
|   +-- policies/
|   +-- fine_tuning/
|
+-- evaluation/
|   +-- evaluator.py
|   +-- test_cases.py
|   +-- tool_evaluator.py
|   +-- security_evaluator.py
|   +-- action_security_evaluator.py
|   +-- end_to_end_action_security.py
|
+-- rag/
|   +-- policy_retriever.py
|   +-- improved_retriever.py
|   +-- policy_metadata.py
|   +-- index/
|
+-- scripts/
|
+-- api.py
+-- Dockerfile
+-- requirements-api.txt
+-- requirements-qlora.txt
+-- requirements.txt
+-- ARCHITECTURE.md
+-- README.md
```

---

## 15. Key Engineering Findings

### RAG

The improved retrieval system achieved perfect Top-1 and Top-3 retrieval accuracy on the frozen synthetic benchmark.

### Fine-Tuning

QLoRA improved structured decision behaviour on the held-out benchmark, particularly structured output and action classification.

### Security

The red-team benchmark demonstrates that model-level safeguards remain imperfect under adversarial prompts.

### Governance

The deterministic Action Guard prevented unauthorized action execution across the tested end-to-end adversarial cases.

This supports a key architectural principle:

> **LLM output should be treated as an untrusted decision proposal when it can lead to consequential actions.**

---

## 16. Limitations

The evaluation results are based on synthetic data and controlled benchmarks.

They should not be interpreted as evidence of production-level performance or security in a real financial institution.

The project does not use real customer information, confidential policies, or proprietary financial data.

The red-team benchmark is limited to the defined adversarial cases and does not establish complete security coverage.

The Docker configuration is prepared for GPU deployment but has not been presented as a production-validated container image.

---

## 17. Future Work

Planned extensions include:

-  Cloud GPU deployment 
-  CI/CD evaluation pipeline 
-  Automated regression testing 
-  Experiment tracking 
-  Agent tracing 
-  Latency and cost monitoring 
-  Larger adversarial benchmarks 
-  Human-in-the-loop approval UI 
-  Model and policy versioning 
-  Production observability 
-  Authentication and authorization 
-  Persistent audit logging 

---

## 18. Project Objective

AgentGuard demonstrates an end-to-end approach to building, evaluating, securing, and governing LLM-powered agents:

```
```

```
Synthetic Data
      ↓
Policy RAG
      ↓
LangGraph Agent
      ↓
Tool Use
      ↓
QLoRA
      ↓
Evaluation
      ↓
Red Teaming
      ↓
Action Governance
      ↓
Human Approval
      ↓
Execution Boundary
      ↓
FastAPI
```

The project focuses on a practical enterprise AI engineering question:

> **How can an LLM-powered agent be evaluated and connected to consequential tools without treating the model itself as the security boundary?**
>
> ''', encoding='utf-8')"

```
```

````

**Important:** this is one single command. Paste the entire command beginning with `python -c` and ending with `''', encoding='utf-8')"`.

Then **do not paste the README into the terminal again**. Just run:

```powershell
Get-Item README.md | Select-Object Name, Length
````

If it returns a size around 10–15 KB, the README was written successfully.
