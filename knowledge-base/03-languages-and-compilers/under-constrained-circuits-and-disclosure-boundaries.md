# Under-Constrained Circuits and Disclosure Boundaries

This document focuses on the dominant application-layer failure mode in zero-knowledge systems: under-constrained circuits, witness/constraint divergence, and disclosure-boundary design in languages such as Compact.

## The Polygon zkEVM Cautionary Tale

Before we proceed, a cautionary tale.

The original version of this book listed Polygon zkEVM as the flagship example of Philosophy A -- the EVM-compatible approach. Five independent reviewers flagged the same problem: Polygon zkEVM was shut down.

Polygon acquired Hermez, the team behind one of the most ambitious zkEVM implementations, for approximately $250 million. The project aimed to prove every Ethereum opcode, faithfully reproducing the EVM's behavior inside a zero-knowledge circuit. It was technically impressive. It was also, in the end, commercially unviable.

In 2025, Polygon announced the sunsetting of zkEVM Mainnet Beta. The Hermez team, led by co-founder Jordi Baylina, spun off to form ZisK -- and pivoted to RISC-V. The very team that had spent years building the most faithful EVM-compatible proof system concluded that proving the EVM directly was not the path forward. Better to prove a clean, efficient instruction set (RISC-V) and layer EVM compatibility on top.

The lesson is not that EVM compatibility is wrong. Scroll and Linea are thriving. The lesson is that *how* you achieve compatibility matters enormously. Polygon bet on faithfully reproducing every EVM quirk at the circuit level. The cost -- in engineering complexity, in proving time, in the sheer number of constraints required to model 256-bit arithmetic -- proved prohibitive. Scroll and Linea survived because they found more efficient paths to the same goal.

For a system architect evaluating ZK infrastructure, the takeaway is concrete: a $250 million investment with a world-class team is not sufficient if the architectural approach creates an exponential constraint-generation problem. Philosophy A is viable, but only if you resist the temptation to prove the EVM literally. Abstract where you can. Approximate where you must. And keep one eye on the RISC-V projects that may make your compatibility layer unnecessary.

The cautionary tale has a coda. Jordi Baylina, who led Polygon Hermez and co-created Circom, took the team to ZisK and chose RISC-V. The person who knew more about EVM-compatible ZK proving than almost anyone else alive concluded that the direct approach was not the path forward. When the world's leading practitioner abandons a technique, the rest of the field should pay attention.

---

## The Developer's Actual Experience

The taxonomy of philosophies describes how *architects* think about Layer 2. But what does a *developer* actually do?

The original paper described choosing a language but never described using one. A smart reader would ask: "Fine, I picked a language. Now what?" The answer involves a lifecycle that most ZK documentation glosses over.

**Step 1: Write.** The developer writes source code. In SP1, this is standard Rust. In Circom, this is a template-based constraint description language. In Compact, this is TypeScript-like code with `witness` declarations and `circuit` exports. The writing experience varies enormously. An SP1 developer uses familiar tools -- VS Code, cargo, clippy. A Circom developer works in a specialized IDE with no debugger, no step-through execution, and error messages that refer to constraint indices rather than variable names.

**Step 2: Compile.** The compiler translates source code into a form the proof system can work with. For SP1, this means Rust to RISC-V machine code via the standard LLVM backend. For Circom, this means templates to R1CS constraint systems. For Compact, this means a 26-pass nanopass compilation pipeline that transforms the source through 26 intermediate languages -- from `Lsrc` through type checking (`Ltypes`), disclosure analysis (`Lnodisclose`), loop unrolling (`Lunrolled`), circuit flattening (`Lflattened`), and finally ZKIR output.

A critical finding from recent research: standard LLVM optimization passes (-O3) yield over 40% improvement when targeting zkVMs, compared to much larger gains on traditional CPUs. This is because LLVM's optimization heuristics are tuned for hardware features -- cache locality, branch prediction, instruction-level parallelism -- that do not exist in a zkVM. By refining a small set of LLVM passes to use a ZK-aware cost model, researchers achieved up to 45% on individual benchmarks (with average gains of 1-4%). The compiler is an underexplored optimization surface.

**Step 3: Test.** The developer tests their program. In the RISC-V world, this means running the program natively (without proof generation) and checking outputs. SP1 supports this directly: you can execute your Rust program on a standard CPU and verify correctness before paying the cost of proof generation. In Compact, the SDK provides a local execution oracle that simulates the blockchain environment -- block time, token balances, contract state -- without a running chain.

**Step 4: Prove.** The developer generates a proof. This is where the cost hits. Proof generation for a Compact circuit takes seconds to tens of seconds on local development hardware (detailed timings appear in Chapter 6). For an SP1 program, proving time depends on the number of RISC-V cycles executed -- a simple computation might take seconds; an Ethereum block might take minutes even on GPU clusters.

What does "prove" actually feel like? The experience is unlike anything else in software development. There is no analogy in web development, in systems programming, in machine learning training. It is its own thing, and it deserves honest description.

The first surprise is latency. A compiler error appears immediately. A failed unit test appears in seconds. A failed proof often appears after the system has already spent 20 seconds, or two minutes, building a witness, generating commitments, hashing transcripts, and running the prover's arithmetic. The feedback loop is not "edit, run, see red text." It is "edit, wait, watch fans spin, then discover that a constraint was unsatisfied at step 48,217." This changes developer behavior. It creates a strong incentive to separate *execution testing* from *proof testing*: first confirm that the program computes the right answer natively, then pay the proving cost only when the logic appears stable.

The second surprise is that performance becomes part of correctness. In ordinary software, a refactor that preserves output is usually considered safe unless it is catastrophically slower. In ZK systems, two programs that compute the same result may differ by orders of magnitude in proving cost. A loop that looks harmless in Rust can expand into millions of extra trace rows in a zkVM. A convenience abstraction in a circuit DSL can hide an enormous multiplication count. The developer does not just ask, "Is this program correct?" but also, "How many constraints did this introduce? How many cycles? Will this still prove on a laptop, or did I just require a GPU cluster?" Profiling is not an optimization pass at the end. It is part of the design process from the beginning.

The third surprise is psychological. A successful proof does not feel like a successful web request or a passing test suite. It feels more like sealing a crate and waiting for an inspection stamp. The output is often a blob of bytes, a proving transcript, a verification key, a gas estimate. Nothing about it is self-explanatory. The developer has to build new intuitions: witness generation failures usually mean program logic or environment issues; unsatisfied constraints usually mean a semantic mismatch between intended and actual circuit behavior; dramatic proving slowdowns usually mean the abstraction boundary hid a combinatorial cost. To work productively, teams evolve a tiered workflow: tiny local examples for rapid iteration, native execution for logic checks, small proof fixtures for regression tests, and only then full proving runs on production-sized inputs.

**Step 5: Deploy.** The proven program is deployed. For rollup-based systems, this means posting the proof and public inputs to Ethereum. For Compact, this means deploying the ZKIR circuit, TypeScript bindings, and proving keys to Midnight's network. Contract deployment on Midnight's devnet is dominated by proof generation for the constructor circuit (see Chapter 6 for measured latencies).

**Step 6: Monitor.** In production, the developer monitors for correctness, performance, and security. This step is almost entirely undocumented in the ZK ecosystem. There are no standard monitoring tools for ZK deployments. No dashboards for constraint utilization. No alerting for proof generation failures. The gap between "deploy" and "done" is where real-world systems fail.

One emerging bright spot: LLM-assisted ZK development. The ZK-Coder system improved Circom circuit generation success rates from 20% (baseline large language model) to 88%. This suggests that the developer experience barrier -- the steep learning curve, the unfamiliar constraint semantics, the cryptic error messages -- may be partially addressable through AI tooling. But 88% is not 100%, and the 12% failure cases may be precisely the subtle under-constrainedness bugs that are hardest to detect. An LLM that generates a circuit with a missing constraint is more dangerous than an LLM that fails to generate a circuit at all.

The developer workflow reveals something about Layer 2: the *language* is the part the developer sees, but the *compiler* is the part that matters. A language with beautiful syntax and a buggy compiler is worse than an ugly language with a correct compiler. The field is beginning to understand this. CirC, a unifying compiler infrastructure from Stanford, demonstrated that the compilation problem for ZK circuits shares fundamental structure with SMT solving and software verification. The same optimizations -- constant folding, dead code elimination, common subexpression elimination -- apply across all targets. This suggests that investment in ZK compiler infrastructure could pay off disproportionately, improving every language simultaneously rather than optimizing each one independently.

---

## Under-Constrained Circuits: The Dominant Failure Mode

Here is the fact that should keep every ZK developer awake at night: the most common way a zero-knowledge system fails in practice is not a cryptographic break. It is not a quantum computer. It is not a governance attack. It is a bug in the program.

The under-constrained vulnerability epidemic documented in Section 3.1 -- 95 of 141 real-world bugs -- is not an abstraction. To understand why it happens at this scale, you need to understand the dual-track problem.

In Circom -- the most widely deployed ZK language by project count -- every line of code simultaneously describes two things: how to *compute* a value (witness generation), and how to *constrain* that value (the mathematical rule the proof system enforces). These two descriptions use different operators. The arrow `<--` computes a value. The triple-equals `===` constrains it. The combined operator `<==` does both.

The Tornado Cash bug was this: a developer used `=` (JavaScript assignment) where `<==` (constrained assignment) was needed. The witness generator computed the correct value. The constraint system did not enforce it. A malicious prover could substitute any value, and the proof would still verify. One character. Complete soundness break.

This is not a rare edge case. The ZKAP static analysis framework, which introduced a Circuit Dependence Graph abstraction to detect vulnerabilities in Circom circuits, found 34 previously unknown vulnerabilities across 258 circuits in 15 open-source projects. Its analysis identified three root causes:

First, *nondeterministic signals* -- circuit outputs that can take multiple values for a given input because constraints are missing. Twenty-four percent of ZKAP's findings fell in this category.

Second, *unsafe component usage* -- sub-circuits invoked without properly constraining their inputs or outputs. This created gaps where values passed between components were computed but not verified.

Third, *constraint-computation discrepancies* -- places where the witness generator and the constraint system diverged. Division is the classic example: in witness generation, division computes a quotient. In constraints, division is expressed as multiplication (if $a/b = c$, the constraint is $b \cdot c = a$). When the divisor can be zero, these two formulations behave differently. Division-by-zero was the single most common vulnerability class in ZKAP's findings, accounting for 41% of all bugs.

The defensive tooling is evolving. Picus (also called QED^2) uses SMT-based techniques to automatically detect under-constrained circuits in R1CS, reducing the under-constrainedness problem to queries on systems of polynomial equations over finite fields. ZKAP introduced the Circuit Dependence Graph abstraction -- combining data flow edges (witness computation) with constraint edges (R1CS) -- and achieved an F1 score of 0.82, compared to 0.64 for the earlier Circomspect tool. zkFuzz, a fuzz-testing framework for ZK circuits, found 66 bugs including 38 zero-days. MTZK discovered 21 bugs across 4 different ZK compilers.

But these tools share a limitation: they work primarily on Circom circuits. The Rust-based systems that dominate production -- halo2 (used by Scroll and ZK Bridge projects), Plonky3 (used by SP1 and Stwo), and custom constraint systems in RISC Zero and Jolt -- are not covered. The most common ZK bug class has automated detection for the oldest ZK language but not for the systems where new code is being written.

NAVe, a formal verification tool for Noir programs announced in 2025, begins to close this gap. It formalizes Noir's ACIR intermediate representation and uses the cvc5 SMT solver to verify program properties. But formal verification at scale -- for circuits with millions of constraints -- remains beyond current tools. The combination of compile-time prevention (refinement types, disclosure analysis) and post-hoc verification (static analysis, formal methods) could provide comprehensive coverage, but no system achieves both today.

The evidence is clear: the most common failure mode in zero-knowledge systems is not a failure of cryptography. It is a failure of software engineering. The magician's choreography has a typo, and the proof system performs the typo faithfully.

---

## Compact's Disclosure Analysis

Compact, Midnight's smart contract language, takes a fundamentally different approach to the bug problem. Rather than giving developers direct access to constraints and hoping they get it right, Compact's compiler enforces a *disclosure rule*: witness values are private by default, and any attempt to use a private value in a public context without explicit consent is a compile-time error.

This is not a style guide. It is not a best practice recommendation. It is a hard compiler rejection.

Here is how it works. In Compact, private data enters the circuit through *witness* functions -- declared in Compact, implemented in TypeScript:

```typescript
witness get_secret(): Bytes<32>;
```

The implementation runs off-chain, in the user's browser or node:

```javascript
const witnesses = {
  get_secret: (ctx) => [ctx.privateState, hexToBytes("aabb...")]
};
```

The witness value is private. It exists only on the user's device. To use it inside a circuit -- where it will be constrained and proven -- the developer must explicitly call `disclose()`:

```typescript
export circuit verify(): [] {
  const sk = disclose(get_secret());
  const my_hash = persistentHash([pad(32, "auth:"), sk]);
  assert(my_hash == stored_hash, "not authorized");
}
```

Without `disclose()`, the compiler rejects the program. The error message traces the complete path from the witness value to the public surface:

```
potential witness-value disclosure must be declared but is not:
  witness value potentially disclosed:
    the return value of witness get_amount at line 8 char 1
  nature of the disclosure:
    ledger operation might disclose the witness value
  via this path through the program:
    the argument to increment at line 11 char 8
```

The compiler catches three categories of accidental leakage: witness values used in ledger operations (writing to on-chain state), witness values returned from circuits (visible in the proof's public outputs), and witness values passed to kernel operations (token transfers, balance queries).

The disclosure analysis pass runs as part of the 26-stage nanopass compilation pipeline, at the `Lnodisclose` intermediate language stage. The privacy boundary is verified before any code generation occurs. The compiler has already type-checked the program, analyzed data flow paths, and confirmed that every potential disclosure is explicitly marked -- or the compilation fails.

Consider a concrete case. The Midnight developer guide documents that the first attempt at implementing a private voting contract -- using naive if/else branching on witness values -- was rejected by the compiler with 11 disclosure errors. Each error traced the path from a witness value to a public surface. The compiler forced a fundamental redesign: Merkle trees replaced per-slot branching, nullifiers replaced voted-flags, and arithmetic tallying replaced conditional increments. The resulting design was not just compiler-compliant -- it was architecturally superior. The naive approach would have leaked which candidate each voter chose through the pattern of ledger writes. The compiler-forced redesign made this impossible.

No other ZK language provides this guarantee. In Circom, Noir, and Cairo, privacy depends on the developer correctly managing which values are public and which are private. A mistake does not produce a compiler error. It produces a privacy leak that may not be discovered until an attacker exploits it. Compact makes privacy a compiler guarantee rather than a developer responsibility.

The tradeoff is clear: Compact contracts are locked to Midnight's proof system (PLONK on BLS12-381), token model (Zswap), and ledger architecture. They cannot be deployed on another chain. In exchange, the developer gets something no general-purpose approach can offer: the compiler will not let you accidentally show the audience what is behind the curtain.

---

## Midnight: Compiler, IR, Circuit

Compact's three-part compilation architecture illustrates a principle that applies across all of Layer 2: the compilation target shapes the developer's world.

From a single `.compact` source file, the compiler produces three distinct artifacts:

**Artifact 1: ZKIR circuits.** ZKIR (Zero-Knowledge Intermediate Representation) is a JSON-formatted circuit description with 24 typed instructions organized into eight categories: arithmetic (`add`, `mul`, `neg`), constraints (`assert`, `constrain_bits`, `constrain_eq`), control flow (`cond_select`, `copy`), type encoding (`decode`, `encode`), cryptographic operations (`ec_mul`, `hash_to_curve`, `persistent_hash`), and I/O (`impact`, `output`, `private_input`, `public_input`).

Every ZKIR circuit has two transcript channels. The `publicTranscript` records ledger operations -- reads, writes, comparisons -- visible to the on-chain verifier. The `privateTranscriptOutputs` contains witness-derived values visible only to the prover. The ZKIR checker verifies that the serialized public transcript matches exactly what the circuit computed. Tampering with either transcript causes rejection with specific, diagnostic error messages.

**Artifact 2: TypeScript bindings.** The compiler generates type-safe JavaScript/TypeScript API code that handles contract interaction from the dApp frontend. This includes witness provider interfaces (the functions that supply private inputs), serialization between TypeScript types and field elements, and the transaction construction and submission pipeline. The witness functions run off-chain with access to private state, external APIs, and databases -- computation that could never run inside a ZK circuit.

**Artifact 3: Proving keys.** Contract-specific cryptographic material for the PLONK-based proof system on BLS12-381. Different circuits produce different keys. The proof server requires these keys to generate proofs; validators require them to verify proofs.

This three-part split is not an implementation detail. It reflects the fundamental architecture of privacy-preserving computation: what can be proven (ZKIR), what runs privately (TypeScript), and what makes proofs possible (keys). No other ZK language produces all three from a single source file with first-class blockchain integration. Circom produces R1CS plus a witness generator but no blockchain API. Noir produces ACIR but no TypeScript bindings and no blockchain integration. Cairo produces execution traces but no privacy separation. Compact unifies the entire dApp development pipeline.

For a system architect, the lesson generalizes beyond Midnight: the choice of Layer 2 language is not just a choice of syntax. It is a choice of compilation target, developer tooling, privacy model, and deployment pipeline. The language shapes everything downstream.

---

The choreography is written. The developer has expressed their computation in a language -- whether Rust targeting RISC-V, Cairo targeting Starknet, or Compact targeting Midnight's ZKIR. The compiler has translated the program into a form the proof system can work with.

But the program is just the *plan*. It describes what the computation should do. It does not contain the private data. It does not contain the execution trace. It does not contain the secret.

Now the magician goes backstage. The curtain closes. The audience waits. Behind the curtain, the magician will run the computation with real data -- real bank balances, real identity credentials, real votes -- and record every step. This recording is the witness: the complete execution trace that later layers will prove properties about without ever revealing.

The recording is where the real cost lives. And it is where the real vulnerabilities hide.

---


## Related Topics

- [ZK Languages and Compiler Design](languages-and-compiler-design.md)
- [Witness Generation and Execution Traces](../04-witness-generation/witness-generation-and-execution-traces.md)
- [Arithmetization and Constraint Systems](../05-arithmetization/arithmetization-and-constraint-systems.md)
- [Proof Systems, Recursion, and Folding](../06-proof-systems/proof-systems-recursion-and-folding.md)
- [Verification, Governance, and Data Availability](../08-verification/verification-governance-and-data-availability.md)
- [Privacy-Enhancing Technologies](../09-privacy-technologies/privacy-enhancing-technologies.md)
- [Midnight Case Study](../12-midnight/midnight-case-study.md)
- [The Seven-Layer Model](../01-foundations/seven-layer-model.md)
