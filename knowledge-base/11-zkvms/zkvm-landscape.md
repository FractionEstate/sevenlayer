# zkVM Landscape

This document summarizes the zkVM landscape, compares major systems across the stack, and explains how zkVM design choices map onto the seven-layer model.

## zkVMs Across the Stack

We need to talk about the thing that changed everything.

The zkVM is not a Layer 2 phenomenon. It is a technology that reaches into every layer of the stack -- from the field choice at Layer 6, through the arithmetization at Layer 4, to the verification economics at Layer 7. If the seven-layer model is the map, the zkVM is the earthquake that reshaped the terrain.

Before zkVMs, every zero-knowledge application required building a custom stage: hand-crafting constraint systems, choosing a field, designing a witness format, writing a custom verifier. Each application was a bespoke production -- a one-night show with its own scenery, its own props, its own choreography. The zkVM changed this by providing a **universal stage** that can host any trick. A developer writes ordinary Rust, compiles it to RISC-V, and the zkVM handles everything else: witness generation, arithmetization, proving, compression, and verification. The stage is universal; the performances are infinite.

The preceding layer-by-layer analysis reveals why this matters so deeply. The most urgent findings at nearly every layer are not isolated gaps but consequences of the same underlying shift. Polygon zkEVM's shutdown at Layer 2, the Witness Gap's amplification at Layer 3, CCS and LogUp's emergence at Layer 4, folding's rise and the hybrid pipeline's dominance at Layer 5, the small-field revolution at Layer 6, STARK-to-SNARK wrapping at Layer 7 -- these are the seismic effects of a single tectonic event: the zero-knowledge virtual machine reorganized the entire stack around itself.

## The Landscape Table (March 2026)

The numbers tell the story concisely. Eight of ten major zkVMs now target RISC-V. Only Stwo (Cairo) and zkWASM (WebAssembly) hold out -- and even StarkWare's ecosystem hedges via Kakarot's EVM-on-Stwo path. The Ethereum Foundation declared the speed race "effectively won" in December 2025 and pivoted to 128-bit provable security by end of 2026.

| | SP1 Hypercube | RISC Zero | Jolt | Stwo | Airbender | ZisK | Pico Prism |
|---|---|---|---|---|---|---|---|
| **Org** | Succinct | RISC Zero | a16z | StarkWare | Matter Labs | SilentSig | Brevis |
| **ISA** | RISC-V (RV32IM) | RISC-V (RV32IM) | RISC-V (RV32I) | Cairo (custom) | RISC-V (RV32IM) | RISC-V 64 | RISC-V (RV32IM) |
| **Arithmetization** | Multilinear AIR + LogUp-GKR | AIR (DEEP-ALI) | R1CS + Lasso lookups | Circle AIR + LogUp | AIR (degree-2) | AIR / PIL | AIR (Plonky3) |
| **Proof system** | Multilinear STARK | FRI STARK | Spartan sumcheck | Circle STARK | DEEP STARK | STARK (recursive) | STARK (Plonky3) |
| **Field** | BabyBear (31-bit) | BabyBear (31-bit) | BN254 (256-bit) | M31 (31-bit) | M31 (31-bit) | Goldilocks (64-bit) | BabyBear / M31 |
| **SNARK wrap** | Groth16 | Groth16 | Planned | None (native) | Groth16 | Groth16 | Groth16 |
| **Eth block** | 6.9 s / 16 GPU | 44 s / cluster | N/A | N/A (Cairo) | 35 s / 1 GPU | 6.6 s / 24 GPU | 6.9 s / 16 GPU |
| **Maturity** | Production | Production | Beta | Production | Production | Adv. testnet | Production |

**Glossary.** *ISA* = instruction set architecture, the fundamental language a processor understands. *Arithmetization* = the method of translating computation into mathematical equations. *AIR* = Algebraic Intermediate Representation, encoding computation as polynomial constraints over an execution trace. *LogUp-GKR* = a sumcheck-based lookup argument. *Circle STARK* = a STARK adapted to work over the circle group of a Mersenne prime. *SNARK wrap* = compressing a large transparent proof into a small proof for cheap on-chain verification. *Field* = a set of numbers with special arithmetic properties; "31-bit" and "64-bit" refer to element size, with smaller fields enabling faster operations on modern hardware.

Three systems dropped from this table deserve brief mention. Nexus 3.0 abandoned Nova-based folding for a Stwo backend after observing a 1000x speed penalty from classical folding -- a telling result for the practical viability of folding in production zkVMs. Valida uses a custom stack-based ISA designed from scratch for ZK proving, with no independent large-scale benchmarks. zkWASM is the only remaining PLONKish/KZG outlier, targeting WebAssembly rather than RISC-V.

For architects choosing a zkVM, the landscape table above describes *what exists*. The rubric below describes *how to choose*:

| Goal | Recommended | Rationale |
|------|-------------|-----------|
| General-purpose execution | SP1 Hypercube, RISC Zero | RISC-V, mature tooling, broadest Rust ecosystem support |
| Maximum throughput | SP1 Hypercube, Airbender | Best Ethereum block proving benchmarks (6.9s, 21.8M cycles/sec) |
| ZK-native efficiency | Stwo (Cairo) | Purpose-built ISA eliminates translation overhead; Starknet-native |
| Post-quantum trajectory | Neo/SuperNeo (watch) | Lattice-based, CCS-native, 127-bit PQ security; 3-5 year horizon |
| Lookup-heavy design | Jolt | Lasso decomposable lookups; sumcheck-native; avoids NTT bottleneck |
| Minimum trusted setup | Stwo, Pico Prism | Fully transparent (hash-based FRI); no ceremony required |
| Formal verification | SP1 | 62 RISC-V opcodes verified against Sail spec; strongest correctness guarantees |

## Three zkVMs Through Seven Layers

The best way to understand why the seven-layer model bends under zkVM pressure is to trace three representative systems through all seven layers. Watch how they cross the same territory by different routes.

### SP1 Hypercube: The General-Purpose Champion

**Layer 1 (Setup).** Hybrid -- transparent inner loop (hash-based Poseidon2 over BabyBear), trusted outer wrap (Groth16 over BN254). The KZG ceremony is for the wrapper only. This demonstrates that the trusted-or-transparent choice is actually "both."

**Layer 2 (ISA).** RISC-V (RV32IM). Developers write ordinary Rust; the compiler handles the rest. SP1 implements 39+ RISC-V instructions, with all 62 core opcodes formally verified against the official RISC-V Sail specification.

**Layer 3 (Witness).** Shard-based execution traces with continuations. Each shard is an independent proving unit; "shared challenges" enforce consistency at shard boundaries. This is where the Witness Gap lives -- SP1's witness generation is CPU-bound while its proving is GPU-accelerated, meaning witness generation consumes an estimated 60-70% of total proving time.

**Layer 4 (Arithmetization).** Multi-table AIR with LogUp-GKR cross-table lookups over multilinear polynomials. Each RISC-V instruction type has its own constraint table ("chip"). Precompiles (SHA-256, Keccak, secp256k1) are independent STARK tables connected via LogUp.

**Layer 5 (Proof).** Four-stage pipeline: core STARK proof per shard, recursive compression, shrink (field transition), Groth16 wrap. Proves 99.7% of Ethereum L1 blocks in under 12 seconds on 16 RTX 5090 GPUs.

**Layer 6 (Primitives).** BabyBear field (31-bit), Poseidon2 hash, Jagged PCS (commits only to occupied trace rows, eliminating padding waste), FRI-based commitment.

**Layer 7 (Verifier).** Groth16 on-chain verification at approximately 250-300K gas on any EVM chain. Live on Ethereum mainnet via the Succinct Prover Network.

**What makes SP1 architecturally distinctive.** SP1 Hypercube is an exercise in *factoring a monolithic problem into independent pieces and then reassembling them under a single algebraic umbrella*. The system's defining architectural idea is not any single layer but the interaction between three design choices that reinforce each other. First, the multi-table AIR architecture assigns each RISC-V opcode its own constraint table -- a "chip" -- so that the constraint degree and column count for a SHA-256 precompile need not compromise the constraint shape for a simple register-to-register add. Second, LogUp-GKR cross-table lookups bind these independent chips together using sumcheck over multilinear extensions, which avoids the quadratic blowup that a naive permutation argument would impose as chip count grows. Third, sharding with continuation challenges means that execution traces of arbitrary length can be sliced into fixed-size proving units, each provable in parallel on a separate GPU, with algebraic consistency enforced by shared random challenges drawn after the shards are committed.

The result is a system that scales *horizontally* in two independent dimensions: more instruction types (more chips) and longer executions (more shards). Adding a new precompile -- say, a BLS12-381 pairing for Ethereum validator operations -- requires only a new chip table and new LogUp entries; existing chips and the recursive compression pipeline remain unchanged. This modular extensibility explains why SP1 has accumulated over 39 instruction types and counting, whereas architectures with monolithic trace layouts face painful refactoring when adding even one new opcode.

The Jagged PCS matters just as much. Standard polynomial commitment schemes commit to a fixed-size domain, which means that a chip with 10,000 occupied rows in a shard of capacity $2^{20}$ wastes commitment work on a million empty rows. Jagged PCS commits only to the non-trivial portion, eliminating padding overhead. In practice, most shards have a few "hot" chips (ALU, memory) and many "cold" chips (uncommon opcodes). Without Jagged PCS, the cold chips would dominate commitment cost despite contributing almost nothing to the computation. With it, proving cost tracks actual computation, not worst-case table size.

SP1's four-stage pipeline -- core STARK per shard, recursive compression, field-transition shrink, Groth16 wrap -- is also a study in staged trust assumptions. The inner stages are fully transparent, hash-based, and post-quantum resilient. Only the final wrap introduces a trusted setup and classical-security assumption. If and when a post-quantum on-chain verifier becomes practical, SP1 can drop the Groth16 stage and expose the transparent inner proof directly. The architecture is built to survive the quantum transition, not merely to endure it.

### Stwo/Cairo: The ZK-Native ISA Champion

**Layer 1.** Fully transparent (hash-based). For Ethereum L1 settlement, a Groth16 wrapper exists via Herodotus, but the primary pipeline remains STARK-native.

**Layer 2.** Cairo -- a custom ISA designed to minimize arithmetization cost. Here the model's top-down flow inverts. The ISA *is* the constraint system, by design. Layer 4 requirements shaped Layer 2. The choreography was written to serve the stage machinery, not the other way around.

**Layer 3.** Cairo VM execution producing columnar M31 traces. The field choice is baked into the VM itself, not merely the proving step -- a deeper coupling than in RISC-V zkVMs.

**Layer 4.** Flat AIR with one component per instruction, LogUp cross-component lookups, mixed-degree constraints. Circle STARKs use the circle group over M31 (where $p+1 = 2^{31}$ is a power of two) to enable FFTs over a field that lacks large multiplicative subgroups.

**Layer 5.** Circle STARK with SHARP aggregation. Approximately 100x faster than its predecessor Stone. Live on Starknet mainnet since November 2025.

**Layer 6.** M31 field (31-bit). M31 arithmetic is approximately 125x faster than the 252-bit Stark field used by Stone. The field choice *created* the need for Circle STARKs -- the strongest example of Layer 6 forcing a Layer 5 invention.

**Layer 7.** Native STARK verification on Starknet (no wrapping needed). For Ethereum L1: SHARP-aggregated Groth16.

**What makes Stwo architecturally distinctive.** Stwo is what happens when you design the entire stack backward from a single mathematical insight: *the group of points on the circle $x^2 + y^2 = 1$ over a Mersenne prime has order $p+1$, and when $p = 2^{31} - 1$, that order is exactly $2^{31}$ -- a power of two*. This accident of number theory is the seed from which the entire Stwo architecture grows.

Conventional STARKs require a field with large multiplicative subgroups for FFT-based polynomial evaluation. The Mersenne prime $M31 = 2^{31} - 1$ has no such subgroups -- its multiplicative group has order $2^{31} - 2$, which factors badly. A naive approach would disqualify M31 from STARK construction entirely. Circle STARKs solve this by abandoning the multiplicative group in favor of the circle group, where the "FFT" becomes a circle-group analog (the Circle Number Theoretic Transform). The evaluation domain is the set of points on the unit circle over $\mathbb{F}_{M31}$, not the powers of a generator in $\mathbb{F}_{M31}^*$. This is not a minor algebraic substitution; it requires rethinking polynomial commitments, coset structures, and FRI queries from the ground up.

The payoff is a 125x speedup. M31 arithmetic -- 31-bit integer addition and multiplication with a single modular reduction -- maps directly onto 32-bit CPU and GPU instructions with no multi-precision overhead. A single SIMD lane processes one field element. Compare this with the 252-bit Stark field used by Stone, where each field multiplication requires multiple 64-bit limb operations and carry propagation. The measured 125x speedup over Stone is not a software optimization; it is a consequence of matching the algebraic structure to the hardware word size.

Cairo's role is just as distinctive. Where RISC-V zkVMs treat the ISA and the constraint system as separate concerns -- the ISA defines computation, the arithmetization encodes it -- Cairo *collapses the two*. A Cairo instruction is simultaneously a machine operation and a set of polynomial constraints. The compiler does not translate programs into constraints; it emits programs that *are* constraints. This eliminates the "arithmetization tax" that RISC-V zkVMs pay: the overhead of encoding a general-purpose instruction (designed for silicon hardware) into an algebraic form (designed for polynomial provers). Gassmann et al.'s finding that standard LLVM optimizations yield 40% improvement on RISC-V zkVMs -- because LLVM optimizes for caches and branch predictors that do not exist in ZK execution -- quantifies exactly the tax that Cairo avoids.

The SHARP (Shared Prover) aggregation layer adds a dimension absent from SP1 and Jolt: *amortization across applications*. SHARP batches proofs from multiple independent Starknet applications into a single recursive proof, so that the fixed cost of Ethereum L1 verification is shared among all applications that submit proofs in the same batch window. This is economic aggregation, not just cryptographic recursion. A small contract with ten transactions per hour pays a fraction of the L1 verification cost that it would bear alone. The theater shares its rent among all the acts on stage.

The trade-off is ecosystem lock-in. Cairo is not Rust, not C, not any language with a pre-existing developer community of millions. Every Cairo developer is a developer that StarkWare's ecosystem must recruit and train. The Kakarot project -- an EVM interpreter written in Cairo, running on Stwo -- is the architectural hedge: it lets Ethereum developers write Solidity while Cairo and Stwo handle the proving underneath. Whether this bridge is sturdy enough to carry mainstream adoption is the open strategic question.

### Jolt: The Lookup Singularity Pioneer

**Layer 1.** Trusted (Hyrax/Pedersen commitments), with transparent alternatives planned (Basefold in Jolt-b).

**Layer 2.** RISC-V (RV32I). Same as SP1, but the divergence begins at Layer 4.

**Layer 3.** Every instruction is decomposed into lookups on small subtables. Witness generation *is* the arithmetization -- no meaningful boundary exists between Layers 3 and 4. This is the first crack in the seven-layer model. The backstage preparation and the encoding of the trick are the same act.

**Layer 4.** Lookup-based arithmetization via Lasso. Instead of encoding each operation as constraints, the system verifies every step against pre-approved entries in a comprehensive reference table. A thin R1CS wrapper (~60 constraints per cycle) handles control flow via Spartan. This is a genuinely distinct paradigm from AIR, PLONKish, or CCS.

**Layer 5.** Sumcheck-based proving. No recursion in production; no STARK-to-SNARK wrapping pipeline. Approximately 6x faster than RISC Zero on initial benchmarks, but the gap has narrowed with GPU acceleration.

**Layer 6.** BN254 scalar field (256-bit). 256-bit field operations are approximately 100x more expensive per operation than 31-bit, but Jolt compensates by performing far fewer operations per CPU step.

**Layer 7.** No production on-chain verifier. This is Jolt's most significant gap relative to SP1 and Stwo. The trick is performed brilliantly, but the theater has no box office.

**What makes Jolt architecturally distinctive.** Jolt is the most radical of the three systems, because it asks a question that the other two never consider: *what if we stopped writing constraints entirely?* SP1 and Stwo both encode computation as polynomial constraints -- they differ in how they organize and evaluate those constraints, but both accept the premise that proving a computation means constraining it. Jolt rejects this premise. In Jolt, proving a computation means *looking it up*.

The core insight, which Jolt inherits from the Lasso lookup argument, is that any function on small inputs can be represented as a table. A 32-bit addition is a function from two 16-bit operands to a 17-bit result -- a table with $2^{32}$ entries. Proving that "a + b = c" does not require writing a constraint that the prover satisfies; it requires showing that the triple (a, b, c) appears in the addition table. The prover's obligation shifts from "solve this system of equations" to "demonstrate membership in this pre-computed set." This is not a small change in formalism. It is a different epistemology of computation.

The practical problem is that $2^{32}$-entry tables are too large to materialize. Lasso solves this by decomposing large lookups into combinations of small subtable lookups, using the algebraic structure of the operations themselves. Addition decomposes by limbs; bitwise operations decompose by individual bits; shifts decompose by position. Each subtable is small enough to commit to directly -- typically $2^{16}$ entries or fewer. The Lasso sumcheck protocol then proves that the decomposed lookups are consistent with the original instruction. The result is a system where the per-instruction proving cost scales with the *decomposability* of the instruction, not with the number of constraints needed to describe it.

This decomposition is why Jolt's Layer 3 and Layer 4 merge into a single act. In SP1, the witness (Layer 3) is an execution trace -- a table of register states and memory values at each cycle -- and the arithmetization (Layer 4) is a set of polynomial constraints that the trace must satisfy. These are conceptually and computationally distinct stages. In Jolt, the "witness" for each instruction *is* the lookup decomposition: the set of subtable indices and values that reconstruct the instruction's behavior. Generating the witness and performing the arithmetization are the same computation, executed in a single pass. There is no moment where "the trace is ready and now we constrain it." The trace is the constraint.

The choice of BN254 as the base field is worth examining. SP1 and Stwo chose 31-bit fields for raw throughput, accepting hash-based commitments and transparent proofs. Jolt chose a 256-bit elliptic-curve field, accepting 100x slower per-operation arithmetic, because BN254 enables Hyrax commitments -- a multi-scalar-multiplication-based polynomial commitment scheme with *no trusted setup* and *logarithmic* verification time. Hyrax commitments over BN254 are the reason Jolt avoids both a ceremony (unlike Groth16 wrappers) and hash-chain verification (unlike FRI). The field choice is not a performance concession; it is a commitment-scheme selection that happens to be expensive.

Jolt's current absence of a production on-chain verifier is not merely an engineering gap waiting to be filled. It reflects a deeper tension: the sumcheck-based proving paradigm produces proofs whose verification cost does not compress as neatly into the constant-size Groth16 format that Ethereum L1 expects. The planned Jolt-b variant, which replaces Hyrax with Basefold (a hash-based, transparent commitment scheme), would enable a more conventional STARK-to-SNARK wrapping pipeline. But this replacement changes Jolt's security model -- from discrete-log hardness to hash collision resistance -- and alters the system's identity. Whether Jolt can ship a verifier without becoming a different system is the question that will determine whether the lookup singularity remains a research landmark or becomes a production architecture.

## The "Proof Core" Triad

The comparative analysis reveals a pattern that the seven-layer model obscures: Layers 4, 5, and 6 form a tightly coupled triad -- the **proof core** -- in every production zkVM. These three layers are not three choices. They are one choice with three manifestations.

In Stwo: M31 (Layer 6) forces Circle groups (Layer 5) forces Circle AIR (Layer 4).

In SP1: BabyBear (Layer 6) enables multilinear PCS (Layer 6) enables LogUp-GKR (Layer 4/5) enables Jagged multi-table AIR (Layer 4).

In Jolt: BN254 (Layer 6) enables Hyrax commitment (Layer 6) makes sumcheck natural (Layer 5) makes Lasso lookups natural (Layer 4).

In each case, the field choice *determines* the commitment scheme, which *determines* the polynomial representation, which *determines* the arithmetization. The proof core is the inseparable nucleus of {field, commitment scheme, polynomial representation} that straddles Layers 4, 5, and 6. Acknowledging this concept does not require restructuring the seven-layer model, but it does require acknowledging that the model's clean layer boundaries are pedagogical simplifications, not architectural truths.

To see why this coupling is not merely incidental but structurally inevitable, consider what happens when you try to swap one element of the triad while holding the others fixed. Suppose you wanted to keep M31 arithmetic (for speed) but use Hyrax commitments (for transparent elliptic-curve proofs without a trusted setup). Hyrax requires multi-scalar multiplication over an elliptic curve whose scalar field matches the proving field. No standard curve has a 31-bit scalar field -- the smallest curves used in practice have 254-bit or 256-bit scalar fields. You would need to embed M31 elements into a vastly larger field for every commitment operation, destroying the throughput advantage that motivated the M31 choice. The triad resists substitution because its elements are not independent components connected by interfaces; they are facets of a single algebraic structure viewed from different angles.

The same rigidity appears in the other direction. Suppose you wanted to keep BN254 (for Hyrax compatibility) but switch to AIR-based arithmetization (for the modular chip architecture that makes SP1 extensible). AIR evaluation requires FFTs over the proving field, and BN254's scalar field has a multiplicative subgroup of order $2^{28}$ -- adequate but not generous. More critically, BN254 field operations are 100x slower than BabyBear operations, so the FFT-intensive AIR evaluation that runs in milliseconds over BabyBear would take seconds over BN254. The AIR paradigm's viability depends on cheap field arithmetic; cheap field arithmetic depends on small fields; small fields depend on hash-based commitments. Pull one thread and the entire fabric moves.

This structural coupling explains an otherwise puzzling empirical observation: despite the enormous design space of possible {field, commitment, arithmetization} combinations, production systems cluster around a small number of triads. The March 2026 landscape shows essentially three: {small field, hash-based FRI, AIR} (SP1, Stwo, Airbender, RISC Zero, Pico Prism), {small field, hash-based FRI, AIR + lookup} (ZisK, OpenVM), and {large field, MSM-based, sumcheck + lookup} (Jolt). The clustering is not a failure of imagination. It is the proof core exerting its gravitational pull: only certain combinations are self-consistent, and the self-consistent combinations are few.

**The decisive fork is at Layer 6 (field choice).** SP1 and Stwo both chose small fields (31-bit) optimized for hardware throughput, accepting extension fields and hash-based commitments. Jolt chose a 256-bit field, accepting higher per-operation cost for native elliptic curve compatibility. This single parameter cascades through every other layer. The choice is not primarily about arithmetic speed -- it is about which mathematical universe the entire proof system will inhabit. A 31-bit field lives in the universe of hash trees, Merkle commitments, and transparent proofs. A 256-bit elliptic-curve field lives in the universe of pairings, discrete logarithms, and structured reference strings. These universes have different physics, and a system that enters one cannot easily visit the other.

**The second fork is at Layer 4 (arithmetization).** SP1 and Stwo both use AIR-based constraint systems. Jolt abandons AIR entirely in favor of lookup-based arithmetization. AIR systems *describe* computation as polynomial constraints; Jolt *tabulates* computation as lookup entries. The distinction is deeper than syntax. In an AIR system, the prover must *solve* the constraint system -- find a witness that satisfies all polynomial equations simultaneously. The constraint system is a specification that the witness must match. In a lookup system, the prover must *demonstrate membership* -- show that each instruction's input-output behavior appears in a pre-computed table. The table is not a specification to be satisfied but a reference to be consulted. One paradigm asks "does this answer satisfy the question?" The other asks "is this answer in the book?"

The practical consequence is that AIR systems scale with constraint complexity (more constraints per instruction means more work per step), while lookup systems scale with table size and decomposition depth (more subtables means more sumcheck rounds). For simple arithmetic -- adds, multiplies, shifts -- the lookup approach can be dramatically cheaper, because the subtables are small and the decomposition is clean. For complex operations -- hash functions, elliptic-curve arithmetic -- the lookup approach faces a combinatorial explosion in table size, which is why even Jolt uses a thin R1CS layer for control flow rather than attempting to tabulate branching logic.

**Where the model breaks.** Cairo shows Layer 4 shaping Layer 2 (bidirectional dependency). Jolt shows Layers 3 and 4 collapsing into one. The STARK-to-SNARK wrapping pipeline is not a Layer 5 choice; it pierces Layers 5, 6, and 7 as a single vertical shaft. The seven layers are better understood as seven *aspects* of a single integrated system, not seven *modules* with clean interfaces. The proof core triad is the strongest evidence for this view: three layers that the model presents as independent choices are in fact a single crystalline structure, as rigid and as beautiful as any lattice in mathematics. Change one axis and the crystal shatters. The map is useful. The territory is more interesting.

## Performance: The Cost Collapse

The performance trajectory of zkVMs over the past 24 months is one of the steepest cost collapses in applied cryptography. It deserves to be stated plainly.

**Real-time Ethereum proving is solved.** Four independent teams proved over 99% of mainnet blocks within the 12-second slot time by late 2025:

| System | Hardware | Avg Block Time | % Blocks < 12s |
|--------|----------|---------------|-----------------|
| SP1 Hypercube | 16x RTX 5090 | 6.9 s | 99.7% |
| ZisK | 24x RTX 5090 | 6.6 s | 99.7% |
| Pico Prism | 16x RTX 5090 | 6.9 s | 99%+ |
| OpenVM 2.0 | 16x RTX 5090 | < 12 s (p99) | ~99%+ |

Airbender proves a block in 35 seconds on a *single* H100 GPU -- the fastest single-GPU result, at 21.8 million cycles per second at the base STARK layer.

**Cost trajectory.** The 2,000-fold cost collapse described in Chapter 6 continued to accelerate: within 2025 alone, a further 45x reduction (from $1.69 to four cents per block). Roughly 10x per year, driven by algorithmic improvements, GPU optimization, and competition. A real-time proving cluster runs $60,000-$100,000: sixteen RTX 5090 GPUs (~$32K), dual-socket server, 512 GB RAM. For less than the price of a suburban house, you can prove every Ethereum block in real time.

**The Witness Gap grows with acceleration.** As GPU provers drove cryptographic proving time down 10-50x, witness generation -- still CPU-bound -- became the dominant bottleneck. The proportional shift described in Chapter 4 is now the defining structural constraint of zkVM performance: witness generation in a zkVM equals full VM emulation, which resists the parallelism that NTT and MSM exploit so effectively. The magician's backstage preparation now takes longer than sealing the proof.

Active optimization research is attacking this gap from multiple directions. ZKPOG achieved up to 52x speedup by moving witness generation onto GPUs. OpenVM 2.0's SWIRL prover includes an ahead-of-time compiler executing at 3.8 GHz, eliminating JIT overhead. Nexus 3.0 runs the program twice -- first to gather memory statistics, then to produce an optimized trace.

**The EF security pivot (December 2025).** The Ethereum Foundation declared the speed race won and shifted focus:
- May 2026 target: 100-bit provable security across all zkEVM teams
- December 2026 target: 128-bit provable security, sub-300 KB proofs
- New primary metric: energy per proof (kWh), replacing raw speed
- The EF rejects unproven conjectures (proximity gap assumptions) for production soundness

This pivot validates systems with strong formal security guarantees. It also shifts the competitive axis from "who can prove fastest" to "who can prove most securely" -- precisely where lattice-based and tensor-code approaches hold structural advantages. The race for speed is over. The race for rigor has begun.

## RISC-V Convergence

The numbers are unambiguous: eight of ten major zkVMs target RISC-V. The original three-philosophy taxonomy -- EVM-Compatible, ZK-Native ISA, General-Purpose ISA -- is accurate as a historical classification, but the market has rendered its verdict. RISC-V won the general-purpose category decisively. Even EVM-focused projects now build RISC-V backends and layer EVM compatibility on top.

Why RISC-V? Three reasons converge.

First, RISC-V's register-transfer architecture maps cleanly onto tabular execution traces, which are the native input format for AIR and lookup-based arithmetization. A RISC-V instruction reads source registers, performs an operation, and writes a destination register -- exactly one row in a trace table.

Second, RISC-V's compiler ecosystem is decades deep. Any Rust, C, or C++ program can be compiled to RISC-V using standard LLVM toolchains. This means millions of existing programs become provable without modification. The universal stage accepts any act, because any act can be translated into its language.

Third, RISC-V is open and royalty-free. Unlike ARM (proprietary) or x86 (legacy-encumbered), RISC-V has no licensing costs and no vendor lock-in. For an open-source ecosystem, this matters.

The holdouts are instructive. Cairo (Stwo) is a ZK-native ISA designed to minimize arithmetization cost -- the ISA *is* the constraint system. This gives Cairo a structural efficiency advantage: the compiler optimization study (Gassmann et al., 2025) found that standard LLVM optimizations yield over 40% improvement on RISC-V zkVMs because they target hardware features (caches, branch predictors) absent in ZK contexts. Cairo avoids this overhead by design. Whether that advantage justifies a smaller developer ecosystem is the strategic question StarkWare has answered with "yes" for Starknet and "maybe not" for broader adoption (hence Kakarot's EVM-on-Stwo path).

zkWASM (Delphinus Lab) targets WebAssembly, offering the broadest language support of any zkVM (any language that compiles to WASM). Its PLONKish/KZG architecture is a generational outlier -- it uses pairing-based commitments rather than hash-based -- and it has not demonstrated Ethereum block proving. zkWASM appears to be a niche play for web-native applications rather than a contender for the mainstream proving market.

---


## Related Topics

- [Trust Decomposition and System Architecture](../10-architecture/trust-decomposition-and-system-architecture.md)
- [Arithmetization and Constraint Systems](../05-arithmetization/arithmetization-and-constraint-systems.md)
- [Midnight Case Study](../12-midnight/midnight-case-study.md)
