# The Seven-Layer Model

## Thesis

Zero-knowledge proofs do not eliminate trust. They *decompose* it. They take one monolithic act of faith — trust the bank, trust the platform, trust the government — and shatter it into seven independent, weaker assumptions. Each one is testable. Each one is replaceable. What remains after the mathematics has done its work is not zero trust but *less* trust, distributed across more points of failure, each auditable on its own terms.

The word "trustless" is marketing. The accurate word is "trust-minimized."

## Seven Layers at a Glance

Every zero-knowledge system, from the simplest proof to the most complex rollup, decomposes into seven layers. These are not independent floors in a building. They are organs in a body — deeply interdependent, each shaping what the others can do.

| Layer | Name | One-Sentence Description | Trust Assumption |
|-------|------|--------------------------|------------------|
| 1 | **The Setup** | Before the magician can perform, someone must construct the mathematical parameters that make proving and verifying possible. | The setup ceremony was conducted honestly, or a transparent setup eliminates the need for trust. |
| 2 | **The Language** | The magician needs a script: a programming language to express the computation she wants to prove. | The program was written correctly — 67% of real-world ZK vulnerabilities are under-constrained circuits. |
| 3 | **The Witness** | The magician goes backstage to run the computation with private data, recording every step in an execution trace no one else will ever see. | The hardware generating the witness does not leak secrets through side channels. |
| 4 | **The Arithmetization** | The backstage recording is transformed into a system of polynomial equations checkable in seconds, even though solving it took hours. | The arithmetization faithfully encodes the computation. |
| 5 | **The Proof System** | The magician compresses the entire puzzle into a compact, tamper-proof certificate guaranteeing soundness and zero-knowledge simultaneously. | The proof system's security reduction is tight. |
| 6 | **The Primitives** | Beneath the proof system lie fundamental cryptographic building blocks: elliptic curves, hash functions, and polynomial commitment schemes. | The underlying mathematical problems (discrete logarithms, hash collision resistance) are genuinely hard. |
| 7 | **The Verification** | The audience checks the proof on a public stage — a blockchain, a smart contract, a verifier endpoint. | The governance of the verification layer is sound — most ZK rollups today rely on multisig committees. |

## Layer Summary Table

| Layer | Key Risk | Real-World Example |
|-------|----------|-------------------|
| 1 — Setup | Compromised ceremony | Zcash ceremony (6 participants) → Ethereum KZG (141,416 participants) |
| 2 — Language | Under-constrained circuits | A single `=` where `<==` was needed broke Tornado Cash soundness |
| 3 — Witness | Side-channel leakage | Client-side proving demands hardware most people cannot afford |
| 4 — Arithmetization | Encoding overhead | 10,000×–50,000× over native execution (falling to 1,000×–5,000×) |
| 5 — Proof System | Security reduction gaps | Groth16: 192-byte proof; STARKs: 50–200 KB, no trusted setup |
| 6 — Primitives | Mathematical hardness erosion | BN254 security eroded from 128 bits to ~100; NIST targets 2035 for retiring pre-quantum algorithms |
| 7 — Verification | Governance capture | Beanstalk lost $182M in 13 seconds via flash-loan governance attack |

## Deep Symmetry

Layer 1 (setup) and Layer 7 (verification) are both *social* trust — human decisions about who to trust with power. The mathematical layers (2 through 6) are sandwiched between them. The system converts social trust into mathematical certainty and then converts mathematical certainty back into social trust. The cryptography is a bridge between two shores of human judgment.

## Layer Interdependencies

The layers are presented in order from 1 to 7, but the dependencies do not share this linearity:

- The choice of cryptographic primitive (Layer 6) determines which proof systems are available (Layer 5).
- That determines which arithmetizations work (Layer 4).
- That shapes which languages are efficient (Layer 2).
- That constrains the setup (Layer 1).
- A single decision — say, choosing the Goldilocks field over BLS12-381 — can cascade through all seven layers and reshape the entire architecture.

In practice, some layers fuse. Jolt merges witness generation and arithmetization into a single lookup step. Cairo co-designs its language around its constraint system. The proof core — Layers 4, 5, and 6 — behaves as one inseparable design unit in every production system. By a complete analysis, the model resolves into a directed acyclic graph with fourteen causal edges, not seven tidy floors.

## How to Read the Knowledge Base

This knowledge base has content organized for three audiences:

- **Executive Path:** Start with [What Are ZK Proofs?](what-are-zk-proofs.md), then read the Setup and Verification layer overviews, and the landscape comparison.
- **Engineer Path:** Read the foundations in full, then work through Layers 1–5 focusing on core sections, followed by Primitives and Verification.
- **Researcher Path:** Read everything. The active research fronts are folding schemes (Layer 5), the lattice revolution (Layer 6), CCS unification (Layer 4), and the proof core triad.

**Regardless of path:** do not skip the Setup layer or the trust decomposition. The first is where the deepest trust decisions live. The second is the thesis in its most complete form.

## Three Sequential Frontiers

The field is crossing three frontiers in sequence:

1. **Performance (2023–2025)** — largely crossed: real-time proving achieved, costs sub-cent.
2. **Security (2026–2028)** — the current frontier: formal verification, 128-bit provable security, post-quantum readiness.
3. **Privacy (2027+)** — approaching: compiler-enforced disclosure boundaries, constant-time implementations, metadata protection.

## Related Topics

- [What Are ZK Proofs?](what-are-zk-proofs.md) — foundational concepts, history, and the three properties
- [Layer 1: The Setup](../02-setup/README.md) — trusted vs. transparent setup ceremonies
- [Layer 2: The Language](../03-language/README.md) — DSLs, circuit programming, and under-constrained bugs
- [Layer 3: The Witness](../04-witness/README.md) — execution traces and side-channel risks
- [Layer 4: The Arithmetization](../05-arithmetization/README.md) — polynomial encoding of computation
- [Layer 5: The Proof System](../06-proof-system/README.md) — SNARKs, STARKs, and folding schemes
- [Layer 6: The Primitives](../07-primitives/README.md) — elliptic curves, hash functions, and commitment schemes
- [Layer 7: The Verification](../08-verification/README.md) — on-chain verification and governance
