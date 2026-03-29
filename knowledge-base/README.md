# Sevenlayer Knowledge Base for AI Coding Agents

This knowledge base converts the book-length manuscript into navigable, topic-oriented reference files for AI coding agents, engineers, and researchers working on zero-knowledge systems.

## Start Here if You Are an AI Coding Agent

- [AI Coding Agent Quickstart](agent-quickstart.md) — task-oriented entrypoint for finding the right reference file quickly
- [Glossary](glossary.md) — fast terminology lookup
- [The Seven-Layer Model](01-foundations/seven-layer-model.md) — the repository's core trust-decomposition framework

## How to Use This Knowledge Base

- Start with the foundations if you are new to the repository or to zero-knowledge systems.
- Jump directly to a layer-specific document when working on a narrow architectural or implementation question.
- Use the glossary for fast terminology lookup.
- Use the bibliography when you need to trace a claim back to cited literature.
- Run `python build_pdf.py validate` from the repository root after editing links or navigation so broken local references are caught early.

## Recommended Reading Paths

### Fast orientation
- [What Are Zero-Knowledge Proofs?](01-foundations/what-are-zk-proofs.md)
- [The Seven-Layer Model](01-foundations/seven-layer-model.md)
- [Trusted Setup Ceremonies](02-setup-ceremonies/trusted-setup.md)
- [Verification, Governance, and Data Availability](08-verification/verification-governance-and-data-availability.md)

### Engineering path
- [ZK Languages and Compiler Design](03-languages-and-compilers/languages-and-compiler-design.md)
- [Under-Constrained Circuits and Disclosure Boundaries](03-languages-and-compilers/under-constrained-circuits-and-disclosure-boundaries.md)
- [Witness Generation and Execution Traces](04-witness-generation/witness-generation-and-execution-traces.md)
- [Arithmetization and Constraint Systems](05-arithmetization/arithmetization-and-constraint-systems.md)
- [Proof Systems, Recursion, and Folding](06-proof-systems/proof-systems-recursion-and-folding.md)

### Architecture and ecosystem path
- [Trust Decomposition and System Architecture](10-architecture/trust-decomposition-and-system-architecture.md)
- [zkVM Landscape](11-zkvms/zkvm-landscape.md)
- [Midnight Case Study](12-midnight/midnight-case-study.md)
- [ZK Market Landscape](13-market/zk-market-landscape.md)
- [Open Questions and Research Frontiers](14-open-questions/open-questions-and-research-frontiers.md)

## Directory Index

### Foundations
- [Glossary](glossary.md)
- [What Are Zero-Knowledge Proofs?](01-foundations/what-are-zk-proofs.md)
- [The Seven-Layer Model](01-foundations/seven-layer-model.md)

### Layer 1 — Setup Ceremonies
- [Trusted Setup Ceremonies](02-setup-ceremonies/trusted-setup.md)
- [Transparent Setup](02-setup-ceremonies/transparent-setup.md)
- [Elliptic Curves and Field Selection](02-setup-ceremonies/curves-and-fields.md)
- [The ADOPT Framework for Setup Decisions](02-setup-ceremonies/adopt-framework.md)

### Layer 2 — Languages and Compilers
- [ZK Languages and Compiler Design](03-languages-and-compilers/languages-and-compiler-design.md)
- [Under-Constrained Circuits and Disclosure Boundaries](03-languages-and-compilers/under-constrained-circuits-and-disclosure-boundaries.md)

### Layer 3 — Witness Generation
- [Witness Generation and Execution Traces](04-witness-generation/witness-generation-and-execution-traces.md)

### Layer 4 — Arithmetization
- [Arithmetization and Constraint Systems](05-arithmetization/arithmetization-and-constraint-systems.md)

### Layer 5 — Proof Systems
- [Proof Systems, Recursion, and Folding](06-proof-systems/proof-systems-recursion-and-folding.md)

### Layer 6 — Cryptographic Primitives
- [Cryptographic Primitives and Hardness Assumptions](07-cryptographic-primitives/cryptographic-primitives-and-hardness-assumptions.md)

### Layer 7 — Verification
- [Verification, Governance, and Data Availability](08-verification/verification-governance-and-data-availability.md)

### Cross-Cutting Topics
- [Privacy-Enhancing Technologies](09-privacy-technologies/privacy-enhancing-technologies.md)
- [Trust Decomposition and System Architecture](10-architecture/trust-decomposition-and-system-architecture.md)
- [zkVM Landscape](11-zkvms/zkvm-landscape.md)
- [Midnight Case Study](12-midnight/midnight-case-study.md)
- [ZK Market Landscape](13-market/zk-market-landscape.md)
- [Open Questions and Research Frontiers](14-open-questions/open-questions-and-research-frontiers.md)

### Reference
- [Bibliography and Sources](reference/bibliography.md)
