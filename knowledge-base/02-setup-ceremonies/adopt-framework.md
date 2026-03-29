# The ADOPT Framework for Setup Decisions

## Overview

The ADOPT framework, introduced in the most comprehensive survey of trusted setup ceremonies (the SoK paper by Wang, Cohney, and Bonneau, 2025), evaluates ceremonies against five properties. The survey catalogs over forty real-world ceremonies and finds that **no existing ceremony satisfies all five properties**.

## The Five ADOPT Properties

| Property | Definition | Key Question |
|----------|-----------|--------------|
| **A**vailable | Can anyone access and verify the SRS? | Is the resulting SRS publicly accessible for verification? |
| **D**ecentralized | Is there a single coordinator who could manipulate the ceremony? | Could a central entity influence or compromise the process? |
| **O**pen | Can anyone participate without permission? | Are there barriers to entry for contributors? |
| **P**ersistent | Will the ceremony data survive long-term for auditing? | Can future auditors verify the ceremony's integrity? |
| **T**ransparent | Is every step of the ceremony publicly observable? | Can observers verify the ceremony in real time? |

## Real-World Assessment

### Ethereum KZG Ceremony

The Ethereum KZG ceremony (141,416 participants, 2023) scores well on **openness** and **availability** but still relied on a coordinating entity (the Ethereum Foundation) — falling short on full decentralization.

### Older Ceremonies

Many older ceremonies fail on **persistence**. The intermediate transcript data for projects like Hermez has already become unrecoverable just a few years later. This is not a failure of any specific project — it is a structural limitation of the ceremony model.

### Structural Limitations

Ceremonies are social events, and social events are messy. The gap between the abstract "1-of-N honest participant" security model and the operational reality of running a ceremony with hundreds of thousands of participants — each using different hardware, software, randomness sources, across different jurisdictions — is wide. The protocol can be mathematically perfect. The ceremony is always imperfect.

## The Transparent Alternative

The transparent approach (STARKs, hash-based commitments) avoids the entire ADOPT problem class. There is no ceremony to evaluate, no transcript to preserve, no coordinator to trust. The cost is measured in proof size and verification time, not in coordination complexity and social trust.

## Option-Value Analysis

A concept from financial options theory that the ZK ecosystem has not yet fully internalized: **option value**.

### Trusted Setup on BLS12-381

A trusted setup on BLS12-381 buys performance today but forecloses certain futures:

- When post-quantum migration becomes necessary, every system on BLS12-381 will need a **new setup** — new ceremony, new coordination, new toxic waste
- If the system has accumulated 10 years of state and 10 million users, the migration cost is not just the $2–5 million ceremony — it is the coordination cost of upgrading every node, every contract, every verifier key

### Transparent Setup on Hash-Based Primitives

A transparent setup costs more per proof today but preserves the option to migrate without re-ceremony:

- The hash function can be swapped
- Security parameters can be adjusted
- No toxic waste needs to be re-destroyed because none was ever created

### Valuing the Option

The option's value depends on your estimate of the quantum timeline:

| Quantum Timeline Belief | Option Value | Recommended Approach |
|------------------------|-------------|---------------------|
| 20+ years away | Low — pairing-based performance advantage dominates | Trusted setup acceptable |
| 10–15 years (NIST 2035 target) | Substantial | Seriously consider transparent or hybrid |
| "Harvest Now, Decrypt Later" applies | Critical — even for systems launched tomorrow | Transparent or post-quantum primitives |

The **Federal Reserve's FEDS 2025-093** working paper on quantum threats to financial infrastructure uses exactly this option-value framework. Their conclusion: systems with **10+ year operational lifespans** should use post-quantum or post-quantum-ready primitives. Transparent setups satisfy this criterion by default. Trusted setups on pairing-friendly curves do not.

## The Setup Tradeoff

Layer 1 is where the trust story begins. The choice between trusted and transparent setups is not a philosophical preference — it is an **economic, operational, and temporal decision** with consequences that persist for the lifetime of the system.

### Summary of Tradeoffs

| Dimension | Trusted Setup | Transparent Setup | Hybrid Approach |
|-----------|--------------|-------------------|-----------------|
| Proof size | Small (192 bytes for Groth16) | Large (~100 KB for STARKs) | Small outer proof |
| Verification cost | Cheap (200K–300K gas) | Expensive (2–5M gas) | Cheap (outer verification) |
| Ceremony required | Yes | No | Yes (outer wrapper only) |
| Toxic waste | Yes — must be destroyed | None | Yes (outer wrapper) |
| Quantum shelf life | Finite (estimated 2032–2035) | None (no trapdoor) | Finite (outer wrapper) |
| Post-quantum migration | New ceremony required | Hash function swap | New outer ceremony |
| ADOPT compliance | Partial (no ceremony achieves all 5) | N/A (no ceremony) | Partial |
| Production dominance (2026) | Legacy systems | Inner proof layer | **Dominant pattern** |

### Key Conclusions from Chapter 2

1. The **1-of-N trust model** is a genuine advance over trusting a single entity, but it is trust-minimized, not trustless
2. The **BCTV14 bug** proves that ceremony integrity alone is insufficient — the construction must be independently correct
3. The **quantum shelf life** means no pairing-based setup is permanent
4. The **ADOPT framework** reveals that no ceremony to date achieves the ideal of full availability, decentralization, openness, persistence, and transparency
5. The **hybrid approach** (transparent inner proof, trusted outer wrapper) dominates production because it captures most benefits of both at the price of added complexity

## Key Takeaways

- The ADOPT framework evaluates ceremonies on five properties: Available, Decentralized, Open, Persistent, Transparent — no existing ceremony satisfies all five
- Option-value analysis from financial theory applies directly to setup decisions: trusted setups foreclose post-quantum migration flexibility
- The Federal Reserve (FEDS 2025-093) recommends post-quantum-ready primitives for systems with 10+ year lifespans
- Ceremony persistence is a real failure mode — transcript data for projects like Hermez has already become unrecoverable
- The setup choice is a bet on the future: optimize for today's performance (trusted) or preserve tomorrow's migration flexibility (transparent)
- The hybrid approach (transparent STARK inner proof + trusted SNARK outer wrapper) is the dominant production pattern in 2026

## Related Topics

- [Trusted Setup Ceremonies](trusted-setup.md) — the ceremony model, 1-of-N trust, and evolution from Sprout to KZG
- [Transparent Setup](transparent-setup.md) — the ceremony-free alternative and capex/opex economics
- [Elliptic Curves and Field Selection](curves-and-fields.md) — quantum shelf life and curve security margins
