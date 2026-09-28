# AgentGuard Architecture

## High-Level Architecture

```text
Customer Case
     |
     v
   FastAPI
     |
     v
 LangGraph Agent
     |
     +-------------------+
     |                   |
     v                   v
  Tools                Policy RAG
     |                   |
     v                   v
Customer DB        Policy Documents
Transaction DB
     |
     v
Evidence
     |
     v
QLoRA Decision Model
     |
     v
Structured Decision
     |
     v
Action Guard
     |
     +-----------------------+
     |                       |
     v                       v
   Blocked              Human Approval
                             |
                             v
                       Action Executor
```

## Trust Boundaries

### Boundary 1 — User to Model

Customer-provided instructions are treated as untrusted input.

The model must not allow customer instructions to override system or policy constraints.

### Boundary 2 — Model to Governance

The model produces a decision proposal.

The model does not directly execute financial or transaction-changing actions.

### Boundary 3 — Governance to Execution

The Action Guard determines whether an action is:

- non-executable
- unsupported
- blocked
- subject to human approval

Executable actions require approval before execution.

## Action Types

### Non-executable

Examples:

- investigate
- review
- manual_review
- inform_customer

These do not directly change financial or transaction state.

### Executable

Examples:

- refund
- transfer
- status_change

These require governance and human approval.

## Evaluation Layers

AgentGuard evaluates the system at multiple levels:

```text
Retrieval
   |
Agent reasoning
   |
Tool use
   |
Fine-tuned model
   |
Model security
   |
Action governance
   |
End-to-end execution
```

This allows failures to be attributed to a specific layer rather than treating the entire agent as a single black box.

## Security Principle

The primary security principle is:

> The LLM is not the security boundary.

Even when the model produces an unsafe action, the governance layer must prevent that action from reaching an executable system without the required approval.