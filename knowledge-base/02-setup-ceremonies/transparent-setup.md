# Transparent Setup

## Overview

A transparent setup requires no trusted ceremony, no secret randomness, and no toxic waste. The only "setup" is agreeing on publicly known mathematical primitives — typically a hash function like SHA-256 or BLAKE3. There is nothing to destroy because nothing dangerous was ever created.

## STARKs: The Transparent Alternative

STARKs — Scalable Transparent ARguments of Knowledge — were introduced by Ben-Sasson, Bentov, Horesh, and Riabzev in 2018. The word "transparent" is the operative one.

The security of a STARK rests on **collision resistance** of the hash function: it must be computationally infeasible to find two inputs that produce the same output. This is a weaker trust assumption than the discrete logarithm problem underlying KZG, and it has a critical property: collision-resistant hash functions are believed to resist quantum computers.

### Bulletproofs

A third family deserves mention: Bulletproofs (Bünz et al., 2017). Bulletproofs are transparent (no ceremony needed) and produce logarithmic-size proofs, but require linear verification time. Monero adopted Bulletproofs for confidential transactions. The Inner Product Argument (IPA) at the core of Bulletproofs inspired the Halo approach to recursion without pairings.

However, Bulletproofs' linear verification cost makes them unsuitable for on-chain verification of large circuits, and they rely on the discrete logarithm assumption — they are *not* quantum-resistant.

## Comparison with Trusted Setups

| Setup Type | Trust Assumption | Example | Proof Size | PQ Secure? |
|---|---|---|---|---|
| Circuit-specific trusted | 1-of-N honest in ceremony | Groth16 | 192 bytes | No |
| Universal trusted | 1-of-N honest in ceremony | PLONK, Marlin | ~880 bytes | No |
| Transparent (DL-based) | Discrete log hard | Bulletproofs | ~700 bytes | No |
| Transparent (hash-based) | Collision resistance | STARKs | ~100 KB | Yes |

**The pattern:** As you move from trusted to transparent, trust decreases but proof size increases. No known construction breaks this tradeoff. The SoK paper on trusted setups (Wang, Cohney, Bonneau, 2025) identifies the "ideal polynomial commitment scheme" — transparent setup, constant-size proofs, constant-time verification — as the central open problem in the field. Nobody has built it. Nobody has proved it impossible.

## The Capex/Opex Framework

The most useful lens for understanding setup economics is the **capital expenditure / operating expenditure** distinction.

### Ceremony Costs Are Capex

The Ethereum KZG ceremony required approximately **$2–5 million** in coordination, engineering, and security auditing. This is a one-time cost. Because the resulting SRS is universal, every system that uses it amortizes that cost. With 50+ rollups sharing the same SRS, the per-rollup cost converges to approximately **$60,000** — trivial relative to the annual operating budget of any serious blockchain project.

### Per-Proof Costs Are Opex

Once the stage is built, the cost that matters is the cost of each proof:

| System | On-chain Gas | Cost (typical) | Proof Size |
|--------|-------------|----------------|------------|
| Groth16 verification | 200,000–300,000 gas | $0.50–$1.00 | 192 bytes (3 group elements) |
| Raw STARK verification | 2–5 million gas | $5–$25 | ~100 KB (~500× larger than Groth16) |

These numbers explain why trusted setups persist despite their trust assumptions. The argument is not philosophical — it is economic.

### The Hybrid Approach

The dominant production pattern in 2026 is neither pure trusted nor pure transparent, but **hybrid**: use a transparent STARK as the inner proof (no ceremony required, post-quantum security for the computation), then wrap it in a Groth16 or KZG-based outer proof for cheap on-chain verification.

**Benefits:**
- Transparency of STARKs for the computation
- Economics of SNARKs for on-chain verification

**Costs:**
- Complexity of maintaining two proof systems
- The outer wrapper still requires a trusted setup

### Universal Setup and Marginal Cost

The universal setup model (PLONK, Marlin) has a consequence easy to miss: the capital expenditure of the ceremony is paid once and amortized indefinitely. Every new contract, every new circuit, every upgrade deploys under the same SRS. The marginal cost of adding a new application converges to the cost of compilation — effectively zero.

For example, in Midnight's architecture:
- A simple counter contract produces a **13.7 KB** proving key and a **1.3 KB** verification key
- Per-circuit key derivation is deterministic: same source code + same compiler = same keys
- No new trust assumption enters during compilation

## Transparent Setup Advantages

1. **No ceremony coordination** — No $2–5 million ceremony cost, no coordinator, no transcript preservation
2. **No toxic waste** — Nothing dangerous is created, so nothing needs to be destroyed
3. **Post-quantum ready** — Hash-based transparent setups (STARKs) are believed to resist quantum computers
4. **No quantum shelf life** — No trapdoor means no trapdoor to extract
5. **Option preservation** — Hash functions can be swapped, security parameters adjusted, without re-ceremony

## Transparent Setup Costs

1. **Larger proofs** — ~100 KB for STARKs vs. 192 bytes for Groth16 (~500× larger)
2. **More expensive verification** — 2–5 million gas vs. 200,000–300,000 gas (up to 25× more expensive)
3. **Performance tradeoffs** — Prover time and memory requirements can be higher

## The ADOPT Framework Assessment

The transparent alternative avoids the entire problem class that the ADOPT framework evaluates. There is no ceremony to evaluate, no transcript to preserve, no coordinator to trust. The cost is measured in proof size and verification time, not in coordination complexity and social trust.

## Key Takeaways

- Transparent setups (STARKs) require no ceremony, no toxic waste, and no trust beyond the collision resistance of hash functions
- The trust-size tradeoff is fundamental: as trust requirements decrease, proof size increases — no known construction breaks this pattern
- The hybrid approach (transparent inner proof + trusted outer wrapper) dominates production because it captures most benefits of both
- Ceremony costs are capex ($2–5M one-time); per-proof costs are opex ($0.50–$1.00 for Groth16 vs. $5–$25 for raw STARKs)
- Transparent setups preserve post-quantum migration flexibility — a critical option value for systems with 10+ year lifespans
- The "ideal polynomial commitment scheme" (transparent, constant-size, constant-time) remains the central open problem in the field

## Related Topics

- [Trusted Setup Ceremonies](trusted-setup.md) — the ceremony-based alternative and the 1-of-N model
- [Elliptic Curves and Field Selection](curves-and-fields.md) — why curve choice determines quantum shelf life
- [The ADOPT Framework](adopt-framework.md) — evaluating setup decisions systematically
