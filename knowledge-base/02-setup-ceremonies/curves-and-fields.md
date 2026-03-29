# Elliptic Curves and Field Selection

## Overview

The choice of elliptic curve at Layer 1 determines the security margin, quantum vulnerability, proof system compatibility, and migration path for the entire zero-knowledge stack. This choice propagates forward through years or decades of deployment — the curve that was state-of-the-art in 2018 shows its age by 2026.

## The Quantum Shelf Life

Every pairing-based proof system — Groth16, PLONK, Marlin, Sonic, KZG — rests on the hardness of the **discrete logarithm problem** on elliptic curves. Shor's algorithm, running on a sufficiently powerful quantum computer, solves the discrete logarithm problem in polynomial time.

This is not "might break." This is **"does break, given sufficient hardware."** The question is when, not whether.

### Implications for Trusted Setups

A quantum computer would not need to compromise any ceremony participant. It would not need to break into anyone's hardware or bribe anyone. It would simply take the *public SRS* — the list of elliptic curve points that everyone can see — and extract the original trapdoor from it. Mathematically, irreversibly, without detection.

Once the trapdoor is extracted, every proof ever generated under that SRS becomes suspect. The attacker can forge proofs of false statements indistinguishable from legitimate ones.

### Timeline Estimates

- **Conservative estimates** place cryptographically relevant quantum computers (capable of breaking 256-bit elliptic curve cryptography) in the **2032–2035** timeframe
- **NIST** finalized its first post-quantum cryptography standards (FIPS 203, 204, 205) in August 2024
- **NIST IR 8547** is a deprecation roadmap targeting **2035** for the retirement of pre-quantum cryptographic algorithms

### The Quantum Shelf Life Concept

A KZG ceremony conducted in 2023 produces an SRS that is secure against classical computers indefinitely but has a **finite lifespan** against quantum adversaries. If that SRS secures a blockchain expected to operate for 20 years, the setup's shelf life may expire before the system's intended lifetime ends.

**STARKs**, by contrast, rely on collision-resistant hash functions, which are believed to resist quantum computers. Grover's algorithm provides a quadratic speedup for hash preimage search (128-bit classical security becomes 64-bit quantum security), but this is a quantitative adjustment, not a qualitative break. A transparent STARK-based setup has no quantum shelf life problem because there is no trapdoor to extract.

## BN254's Eroding Security Margin

BN254 (also called alt_bn128 or BN128) is the curve hardcoded into Ethereum's elliptic curve precompile opcodes. Every Groth16 proof verified on Ethereum's base layer uses BN254.

### The Problem

The **Tower Number Field Sieve** (Tower NFS) — a family of discrete log algorithms exploiting the tower structure of extension fields — has reduced BN254's estimated security from **128 bits to approximately 100 bits** (Kim, Barbulescu, 2016; Menezes, Sarkar, Singh, 2016).

100 bits of security is not broken, but it sits **below the 128-bit threshold** that NIST mandates for new cryptographic deployments.

### Migration Status

The ZK ecosystem has been slowly migrating from BN254 to **BLS12-381**, which provides a comfortable 128-bit security margin even under Tower NFS analysis. Migration is slow because:

- Existing smart contracts reference the BN254 precompile directly
- Changing the curve means changing the verification logic
- Every contract that verifies proofs must be upgraded

## BLS12-381

BLS12-381 is the current standard pairing-friendly curve, offering approximately **128-bit classical security**. It provides:

- Comfortable security margin under Tower NFS analysis
- Wide ecosystem compatibility and tooling support
- Faster proof generation than alternative curves

However, BLS12-381 offers **zero post-quantum security**. Every component built on it — SRS, polynomial commitments, proof verification — rests on assumptions that quantum computers break.

### Midnight's BLS12-381 Choice

Midnight, the privacy-focused blockchain built on the Cardano ecosystem, illustrates the BLS12-381 tradeoff concretely:

- **Architecture:** PLONK-family proof system (Halo2 variant) with universal SRS on BLS12-381
- **The Pluto-Eris detour:** Midnight originally adopted Pluto-Eris curves (enabling recursive proof composition via KZG on Pluto, IPA on Eris) but switched back to BLS12-381 in April 2025 for faster proof generation, better tooling, and higher transaction volumes
- **Quantum exposure:** Every ZK proof in Midnight — state transitions, shielded transfers, Zswap privacy operations — becomes forgeable if a quantum computer extracts the trapdoor from the SRS

The switch was a deliberate choice to optimize for present-day deployment at the cost of future quantum vulnerability. Theoretical optimality yielded to engineering pragmatism — a pattern that recurs throughout the ZK ecosystem.

## Universal vs. Circuit-Specific Setups

### Circuit-Specific (Groth16)

Groth16 produces the most compact proofs ever constructed: exactly **192 bytes** (three group elements), verified with three pairing operations. No other system comes close.

But Groth16's setup is circuit-specific: the SRS encodes the structure of a particular circuit. Change the circuit — add a feature, fix a bug, upgrade the protocol — and you need a **new ceremony**. At $2–5 million per ceremony, this is unsustainable for evolving systems.

### Universal (PLONK, Marlin)

PLONK (Gabizon, Williamson, Ciobotaru, 2019) and Marlin (Chiesa et al., 2019) made the SRS **universal**: it encodes a generic mathematical structure (powers of a secret value on an elliptic curve). Any circuit up to a maximum size can use the same SRS.

The per-circuit setup — selecting the evaluation domain, computing selector polynomials, generating proving and verification keys — is entirely **deterministic and public**. No new secrets, no new ceremony, no new toxic waste.

### Midnight's Universal Setup in Practice

Midnight's architecture demonstrates the universal model:

- `midnight-trusted-setup` — the ceremony, producing the universal SRS
- `midnight-zk` — the proof system (PLONK / Halo2 / BLS12-381), consuming the SRS
- `compactc compile` — the compiler, deriving per-circuit keys deterministically

Each compiled contract produces:
- TypeScript bindings for the dApp frontend
- ZKIR circuit files for the proof server
- Proving/verification key pairs derived from the universal SRS

**Example sizes:** A simple counter contract produces a 13.7 KB proving key and a 1.3 KB verification key. These keys inherit security from the original ceremony — no additional trust assumptions enter during compilation.

## Lattice-Based Alternatives

Systems like **Neo** (Nguyen, Setty, 2025) use lattice-based cryptography (Module-SIS and Module-LWE assumptions) conjectured to resist quantum computers.

**Tradeoffs:**
- Larger proofs and more expensive verification
- Transparent setup requiring no ceremony
- Trust assumption shrinks from "1-of-N ceremony participants were honest" to "the lattice problem is hard" — a purely mathematical assumption with no sociological component

Neither pairing-based nor lattice-based approaches are unambiguously correct. They represent different bets:
- **Pairing-based** (Midnight, etc.) bets that classical cryptography remains secure long enough to establish and migrate later
- **Lattice-based** bets that the quantum threat justifies paying the performance cost now

## Key Takeaways

- Every pairing-based proof system breaks under Shor's algorithm — the question is when (estimated 2032–2035), not whether
- BN254's security has eroded from 128 bits to ~100 bits due to Tower NFS, below NIST's 128-bit mandate for new deployments
- BLS12-381 provides 128-bit classical security but zero post-quantum security
- The quantum shelf life concept means a 2023 KZG ceremony's SRS may expire before a 20-year blockchain's intended lifetime ends
- Universal setups (PLONK, Marlin) solved the per-circuit ceremony problem — one ceremony serves all circuits up to a maximum size
- Circuit-specific Groth16 produces the smallest proofs (192 bytes) but requires a new $2–5M ceremony for every circuit change
- The setup layer casts a long shadow: curve choices made at Layer 1 propagate through years or decades of deployment

## Related Topics

- [Trusted Setup Ceremonies](trusted-setup.md) — how the SRS is generated and toxic waste destroyed
- [Transparent Setup](transparent-setup.md) — the hash-based alternative with no quantum shelf life
- [The ADOPT Framework](adopt-framework.md) — systematic evaluation of setup decisions
