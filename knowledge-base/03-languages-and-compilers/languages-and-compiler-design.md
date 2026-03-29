# ZK Languages and Compiler Design

This document extracts the language-layer material from the manuscript for AI coding agents working with domain-specific languages, circuit compilers, zkVM toolchains, and under-constrained circuit risks.

*Layer 2 -- Language*

---

## RISC-V Won. Why Taxonomy Still Matters.

If RISC-V has won -- if eight of ten major zero-knowledge virtual machines now target the same general-purpose instruction set -- why bother presenting a taxonomy of competing philosophies at all? Why not just say "write Rust, compile to RISC-V, the proof system handles the rest"?

Because the taxonomy is not about which instruction set the machine runs. It is about what *the developer sees*. And what the developer sees determines what bugs the developer makes. Those bugs -- not cryptographic breaks, not quantum computers, not governance attacks -- are the single largest source of real-world failures in zero-knowledge systems. Sixty-seven percent of all known SNARK vulnerabilities are under-constrained circuits: programs where the developer said less than they meant, and the proof system happily proved false statements as a result.

The language layer is where the magician writes the choreography for the act. The choice of notation determines what mistakes are possible. Some notations let the performer accidentally step into the audience's view. Others physically prevent it. That distinction is worth understanding, even in a world where RISC-V has won the instruction set war.

> **The Running Example: A Sudoku Proof**
>
> To ground the abstractions that follow, we will trace a single computation through every layer of the stack. The computation: proving you know the solution to a 4x4 Sudoku puzzle without revealing it.
>
> The puzzle has these givens:
>
> ```
> +---+---+---+---+
> | 1 |   |   | 4 |
> +---+---+---+---+
> |   | 4 | 1 |   |
> +---+---+---+---+
> |   | 1 |   |   |
> +---+---+---+---+
> | 4 |   |   | 1 |
> +---+---+---+---+
> ```
>
> The program checks: every row contains {1,2,3,4} with no repeats, every column contains {1,2,3,4}, every 2x2 box contains {1,2,3,4}, and every filled cell matches the given clue. The prover knows the solution. The verifier knows only the puzzle. At Layer 2, this is a program. We follow it through every layer to come.

---

## From Circuits to Virtual Machines: A Brief Evolution

To understand where we are, we need to understand where we came from.

The first generation of zero-knowledge programming looked nothing like programming. In 2018, if you wanted to prove a computation in zero knowledge, you wrote *circuits* -- not programs, but direct descriptions of mathematical relationships. The dominant tool was Circom, a domain-specific language created by Jordi Baylina and the iden3 team. In Circom, you did not write `if balance >= amount then approve`. You wrote constraint templates: mathematical equations that the proof system would verify. The developer was simultaneously writing two programs in one file -- one that computed the witness (the private data), and one that generated the constraints (the mathematical rules). These two programs had to agree perfectly on every input. When they did not, the result was an under-constrained circuit: a proof system that would certify false statements as true.

Imagine asking a playwright to write both the script and the stage directions in a single document, using two different notations that had to be perfectly synchronized, with no compiler to check whether they matched. That is what early ZK development felt like.

Circom was powerful. It gave developers complete control over the constraint system. But that control came at a cost. The Chaliasos SoK confirmed the scale of the problem: 95 of 141 catalogued vulnerabilities were under-constrained circuits -- the epidemic described at the opening of this chapter. The Tornado Cash bug was a single character: `=` where `<==` was needed. One character. Complete soundness break. A malicious prover could generate proofs for false statements, and the verifier would accept them.

The second generation asked a different question: what if the developer never saw the constraints at all? What if they wrote a program in a language they already knew, and a compiler handled the translation to mathematics?

Cairo, created by StarkWare in 2021, pioneered this approach. Cairo defined a new instruction set architecture -- a virtual CPU designed from the ground up so that every instruction's execution could be efficiently encoded as polynomial constraints. The developer wrote programs. The compiler generated constraints. The proof system verified the constraints. The developer never touched a mathematical equation.

But Cairo required learning a new language, a new toolchain, a new way of thinking about computation. The programs you had already written -- in Rust, in C++, in Python -- could not run on Cairo. You had to rewrite everything.

The third generation asked the obvious follow-up: what if we proved a processor that developers already targeted? What if the instruction set was not some exotic ZK-native design, but plain RISC-V -- the open standard that Rust, C, and C++ compilers already produce code for?

This is the generation we live in now. SP1 (Succinct), RISC Zero, Airbender (ZKsync), ZisK (the team formerly known as Polygon Hermez), and Pico Prism all prove RISC-V execution. The developer writes standard Rust. The compiler targets standard RISC-V. The proof system proves the execution trace. The developer may never know they are working with zero-knowledge proofs at all.

But this triumphant narrative -- circuits to custom VMs to RISC-V -- leaves out a fourth thread. There is another approach, one that does not fit the evolutionary story. It does not prove a processor at all. It proves *state transitions*. And its compiler does something no instruction-set-based approach can do: it prevents privacy leaks at compile time.

---

## The Four Philosophies

Every approach to Layer 2 answers the same question differently: how should a developer express a computation that will be proven in zero knowledge?

Four distinct philosophies have emerged. Each makes a different bet about what matters most.

**Philosophy A: EVM-Compatible.** Prove the Ethereum Virtual Machine itself. The developer writes Solidity, the same language used for ordinary Ethereum smart contracts. The proof system executes the EVM bytecode and proves that execution was correct. The advantage is obvious: every existing Ethereum application "just works." The Solidity ecosystem -- its tooling, its auditors, its libraries, its millions of lines of battle-tested code -- transfers wholesale.

The leading examples are Scroll, with $748 million in total value locked, and Linea (ConsenSys), with over $2 billion. Both prove EVM execution using different strategies: Scroll uses a custom zkEVM circuit, while Linea has been converging toward a RISC-V backend with EVM compatibility layered on top.

The disadvantage is equally obvious: the EVM was not designed for proving. It has 256-bit arithmetic (proof systems prefer 31-bit or 64-bit fields). It has dynamic gas metering. It has a complex memory model. Proving every quirk of the EVM is computationally expensive -- like translating a novel into a language that has no word for half the concepts.

**Philosophy B: ZK-Native ISA.** Design a new instruction set from scratch, optimized for proving. The developer learns a new language, but every instruction translates efficiently into polynomial constraints. Cairo is the canonical example. Its instruction set was co-designed with StarkWare's STARK proof system. Layer 2 was literally shaped by Layer 4 -- the language exists *because* of the arithmetization.

Cairo's execution trace model -- columns for program counter, flags, operands, with polynomial constraints between adjacent rows -- became the template for every subsequent zkVM. The Goldilocks prime field ($2^{64} - 2^{32} + 1$) that Cairo adopted has since been used by RISC Zero, SP1, and others. Cairo bet on algebraic efficiency over developer familiarity, and for the Starknet ecosystem, that bet paid off: it is the most battle-tested ZK system after Circom, handling real assets on mainnet since 2020.

The cost is ecosystem isolation. Cairo programs do not run anywhere except Starknet. The tooling, libraries, and developer community are Cairo-specific. Every line of code is a bet on one ecosystem. But that bet has paid returns: Starknet processes real assets, real DeFi, real NFTs. Cairo is not a research project. It is production infrastructure.

The evolution from Cairo 0 to Cairo 1.0 is itself instructive. The original Cairo was barely recognizable as a programming language -- it looked more like assembly with syntactic sugar. Cairo 1.0 aligned with mainstream language features: Rust-like syntax, a borrow checker, generic types. The lesson for the field: even a language designed for proof efficiency eventually converges toward familiar developer ergonomics, because adoption requires accessibility.

**Philosophy C: General-Purpose ISA.** Prove a standard processor. RISC-V has won this category so decisively that it is no longer a competition. SP1 (Succinct), RISC Zero (with its R0VM 2.0 reducing Ethereum block proving from 35 minutes to 44 seconds), Airbender (ZKsync, achieving 21.8 million cycles per second on a single H100 GPU), ZisK (the ex-Polygon team), and Pico Prism all target RISC-V.

The appeal is obvious: the developer writes Rust, C, or C++. The compiler produces RISC-V machine code. The zkVM executes that code and generates a proof. Standard toolchains, standard debuggers, standard testing frameworks. The ZK-specific complexity hides behind the compilation boundary.

Even projects that started with EVM compatibility are converging on RISC-V. ZKsync's Airbender proves RISC-V execution and layers EVM compatibility on top. The trend is clear: RISC-V is the assembly language of the zero-knowledge world.

**Philosophy D: Application-Specific DSL.** This is the philosophy that does not fit the evolutionary narrative. Instead of proving a processor, these languages prove *state transitions*. Instead of hiding ZK complexity behind a compilation boundary, they make privacy a first-class language concept.

Three languages define this category.

*Compact* (Midnight/IOG) is a TypeScript-like language for privacy-preserving smart contracts. Its compiler produces three artifacts from a single source file: a ZKIR circuit (the constraint system), TypeScript bindings (the application interface), and proving keys (the cryptographic setup material). No other ZK language generates all three from one source. More importantly, Compact's compiler includes a *disclosure analysis* pass that statically rejects any program where a private value might leak to a public surface without explicit developer consent. We will return to this in detail.

*Noir* (Aztec Labs) is a Rust-inspired, backend-agnostic ZK language. It compiles to an Abstract Circuit Intermediate Representation (ACIR). Noir does not target a specific proof system -- it targets multiple backends. This makes it the closest thing the ZK world has to a "write once, prove anywhere" language.

Noir 1.0 was pre-released in late 2025. It became an officially recognized language on GitHub. NoirCon conferences have been held (NoirCon0 in November 2024). The ecosystem includes over 600 projects and 900 GitHub stars. Key adopters include zkEmail, zkPassport, and zkLogin. Aztec's Ignition Chain went live in November 2025 as the first decentralized L2 on Ethereum, with 185+ operators across 5 continents and 3,400+ sequencers -- and its core cryptography was rewritten in Noir.

Noir breaks the three-philosophy taxonomy because it is neither ISA-based nor chain-specific: it is a universal circuit language. Its privacy model is straightforward -- all inputs are private unless explicitly declared `pub` -- but it lacks the compile-time disclosure analysis that Compact provides. The developer bears responsibility for correctly managing the public/private boundary. In exchange, Noir programs can target any proving backend that accepts ACIR, making them portable across proof systems in a way that no other ZK language achieves.

*Leo* (Aleo) is a privacy-first language for the Aleo blockchain, with syntax borrowing from Rust and TypeScript. Leo targets Aleo's record-based (UTXO-like -- a UTXO, or Unspent Transaction Output, is a model where each digital coin is a discrete object created by one transaction and consumed by another, like physical bills in a wallet) privacy model and includes hooks for formal verification. With over 400,000 CLI downloads, Leo represents the privacy-specialized variant of the application DSL approach.

To understand why these three languages matter -- why they are not merely syntactic alternatives to writing Rust and compiling to RISC-V -- you need to see what development actually looks like in each one. The differences are not cosmetic. They are structural. Each language imposes a different mental model on the developer, and that mental model determines what classes of bug are possible, what classes of privacy leak are preventable, and what the compiler can guarantee before a single proof is generated.

### Compact: Privacy by Compilation

Consider a simple scenario: a private token transfer. The sender wants to prove they have sufficient balance without revealing what that balance is. In Compact, the developer writes something that looks, at first glance, like an ordinary TypeScript function:

```typescript
export circuit transfer(
  recipient: Bytes<32>,
  amount: Unsigned Integer
): [] {
  const my_balance = disclose(get_balance());
  assert(my_balance >= amount, "insufficient funds");

  const new_sender_balance = my_balance - amount;
  const new_recipient_balance = get_recipient_balance(recipient) + amount;

  ledger.sender_balances[sender()] = new_sender_balance;
  ledger.recipient_balances[recipient] = new_recipient_balance;
}
```

The keyword `circuit` is the first departure from ordinary programming. This function will not execute on a server. It will be compiled into a zero-knowledge circuit -- a set of polynomial constraints that a prover can satisfy and a verifier can check. Every variable inside this function will become a wire in that circuit. Every operation will become a gate.

The keyword `disclose` is the second departure, and the more consequential one. The function `get_balance()` is a witness function -- it retrieves the sender's private balance from off-chain storage. That value is, by default, invisible to anyone but the prover. The `disclose()` call is the developer's explicit declaration: "I acknowledge that this private value will influence public state." Without it, the compiler rejects the program. Not at runtime. Not during testing. At compile time, before any proof is generated, before any key material is created, before any circuit is emitted.

The practical consequence is that a developer cannot accidentally write a transfer function that leaks the sender's balance. They can intentionally leak it -- `disclose()` is an explicit consent mechanism, not a prohibition. But the accidental case, which accounts for the majority of real-world privacy bugs, is eliminated by the compiler's disclosure analysis pass.

The compilation itself is worth understanding. Compact's 26-pass nanopass pipeline transforms the source through a sequence of increasingly specialized intermediate languages. The program begins as `Lsrc` -- essentially the developer's TypeScript-like code. It passes through type inference (`Ltypes`), where the compiler determines the bit-width of every value. It passes through disclosure analysis (`Lnodisclose`), where the compiler traces every data-flow path from witness inputs to public outputs. It passes through loop unrolling (`Lunrolled`), where bounded loops are expanded into straight-line code -- necessary because ZK circuits have no concept of iteration. It passes through circuit flattening (`Lflattened`), where nested expressions are decomposed into individual gates. And it emerges as ZKIR: a JSON-formatted circuit description ready for the proof system.

At no point does the developer interact with constraints, gates, or polynomials. The entire mathematical substrate is hidden behind the compilation boundary. The developer writes TypeScript-like code. The compiler produces a zero-knowledge circuit. The gap between intent and implementation -- the gap where under-constrained bugs live -- is bridged by the compiler, not by the developer.

### Noir: Write Once, Prove Anywhere

Noir takes a different approach to the same problem. Where Compact is chain-specific and privacy-first, Noir is backend-agnostic and correctness-first. A Noir program compiles not to a specific proof system's constraint format, but to ACIR -- Abstract Circuit Intermediate Representation -- which can then be lowered to any compatible backend.

Consider the same token transfer scenario in Noir:

```rust
fn main(
    sender_balance: Field,
    amount: pub Field,
    recipient_balance: Field,
) -> pub Field {
    assert(sender_balance >= amount);
    let new_recipient_balance = recipient_balance + amount;
    new_recipient_balance
}
```

The privacy model is visible in the function signature. Parameters without the `pub` keyword are private -- they are part of the witness, known only to the prover. Parameters marked `pub` are public inputs, visible to the verifier. The return value, also marked `pub`, is the public output.

This is simpler than Compact's disclosure analysis. There is no `disclose()` mechanism, no 26-pass pipeline tracing data-flow paths. The developer declares privacy at the function boundary: this input is private, that input is public, and the compiler enforces the declaration. It is the developer's responsibility to get the declaration right. Noir will not warn you if you accidentally mark a sensitive value as `pub`. But it will guarantee that every private input remains invisible to the verifier -- that the proof reveals nothing about private inputs beyond what the public outputs logically imply.

Where Noir stands apart is composability. A Noir developer can write a library of circuit components -- hash functions, signature verifiers, Merkle tree checkers -- and reuse them across projects targeting different proof systems. The same Noir code that runs on Aztec's Barretenberg backend today could, in principle, run on a PLONK backend, a Groth16 backend, or a future proof system that does not yet exist. This is not theoretical: the Noir ecosystem already includes standard libraries for common cryptographic primitives, and projects like zkEmail, zkPassport, and zkLogin use these libraries to build real applications.

A more realistic Noir program demonstrates the language's expressiveness. Here is a simplified credential verification -- proving you are over 18 without revealing your birthdate:

```rust
use std::hash::poseidon;

fn main(
    birth_year: Field,
    birth_month: Field,
    birth_day: Field,
    credential_hash: pub Field,
    current_year: pub Field,
    threshold_age: pub Field,
) {
    // Verify the credential hash matches the private birthdate
    let computed_hash = poseidon::bn254::hash_3([birth_year, birth_month, birth_day]);
    assert(computed_hash == credential_hash);

    // Verify age threshold without revealing exact birthdate
    let age = current_year - birth_year;
    assert(age >= threshold_age);
}
```

The developer writes Rust-like code. The standard library provides cryptographic primitives. The compiler handles the translation to constraints. The program is readable, auditable, and portable across proof backends. What the program cannot do -- what no Noir program can do -- is enforce at compile time that the developer has not accidentally marked `birth_year` as `pub`. That responsibility rests with the developer, not the compiler.

### Leo: Privacy as a Record System

Leo takes a third approach, one rooted in Aleo's record-based execution model. Where Compact models privacy as a property of data flow and Noir models it as a property of function signatures, Leo models privacy as a property of *records* -- discrete objects that are created, consumed, and transferred, much like physical banknotes.

A Leo token transfer looks different from both Compact and Noir:

```rust
program token.aleo {
    record Token {
        owner: address,
        amount: u64,
    }

    transition transfer(
        input: Token,
        recipient: address,
        amount: u64,
    ) -> (Token, Token) {
        let remaining: u64 = input.amount - amount;

        let sender_token: Token = Token {
            owner: self.caller,
            amount: remaining,
        };

        let recipient_token: Token = Token {
            owner: recipient,
            amount: amount,
        };

        return (sender_token, recipient_token);
    }
}
```

The keyword `record` defines a private data structure. Records in Leo are encrypted on-chain -- only the owner can decrypt them. When a `transition` consumes a record and produces new records, the old record is nullified (marked as spent) and the new records are encrypted for their respective owners. The entire UTXO lifecycle -- creation, transfer, consumption -- is expressed in the language itself.

The keyword `transition` is Leo's equivalent of Compact's `circuit`. It defines a function that will be proven in zero knowledge. But where Compact's circuits operate on abstract state and Noir's functions operate on field elements, Leo's transitions operate on records -- typed, owned, encrypted objects with a lifecycle managed by the Aleo runtime.

Leo's privacy model is structural rather than analytical. Privacy does not emerge from a disclosure analysis pass or from `pub` annotations on function parameters. It emerges from the record model itself: records are encrypted, transitions consume and produce records, and the only public artifact is a nullifier (proving a record was spent) and a commitment (proving a new record was created). The developer does not choose what is private. Everything inside a record is private by default. Publicity is the exception, declared through explicit `public` annotations on transition inputs.

The tradeoff is the same one that appears throughout Philosophy D: Leo programs run only on Aleo. The record model, the transition semantics, the encryption scheme -- all are Aleo-specific. But for developers building on Aleo, Leo provides something that general-purpose languages cannot: a programming model where privacy is not a layer of annotation on top of ordinary computation, but the fundamental unit of state.

### The Philosophy D Synthesis

What unites these three languages is a conviction that privacy cannot be an afterthought. In Philosophies A, B, and C, the proof system guarantees computational integrity -- it proves the computation was done correctly. But it says nothing about what information the computation reveals. Privacy depends on the developer correctly managing which values are public and which are private. A mistake does not produce a compiler error. It produces a privacy leak.

Philosophy D languages treat privacy as a compiler concern. The language itself knows the difference between public and private. And in Compact's case, the compiler physically prevents the developer from accidentally crossing that boundary.

What unites Philosophies A, B, and C is a shared assumption: the developer does not need to think about privacy. The proof system guarantees computational integrity -- it proves the computation was done correctly. But it says nothing about what information the computation reveals. Whether to encrypt inputs, hide outputs, or shield metadata is left to the application layer, if it is considered at all.

Philosophy D breaks this assumption. Privacy is not a layer above the language -- it is embedded in the language itself.

The following table summarizes the four philosophies:

| Philosophy | Representative | What It Proves | Privacy Model | Developer Experience | Tradeoff |
|---|---|---|---|---|---|
| **A: EVM-Compatible** | Scroll, Linea | EVM execution | None (transparent) | Familiar (Solidity) | Proving the EVM is expensive |
| **B: ZK-Native ISA** | Cairo (Starknet) | Custom CPU trace | None (transparent) | New language required | Locked to one ecosystem |
| **C: General-Purpose ISA** | SP1, RISC Zero, Airbender | RISC-V execution | None (transparent) | Familiar (Rust, C++) | Arithmetization overhead |
| **D: Application DSL** | Compact, Noir, Leo | State transitions or circuits | Compiler-enforced | Domain-specific syntax | Locked to one chain (Compact/Leo) or one IR (Noir) |

The taxonomy is not a ranking. Each philosophy serves a different constituency. The following decision guide distills each philosophy's sweet spot:

| Philosophy | Choose This When | Avoid When |
|-----------|-----------------|------------|
| **A: EVM-Compatible** | Existing Solidity codebase; need L1 security inheritance; team knows EVM tooling | Building from scratch; performance-critical new system; proving cost is binding constraint |
| **B: ZK-Native ISA** | Maximum proving efficiency; willing to learn Cairo; building within Starknet ecosystem | Need ecosystem portability; team cannot invest in new language; multi-chain deployment required |
| **C: General-Purpose ISA** | Standard Rust/C++ codebase; want ecosystem portability; broadest developer pool; zkVM as proving backend | Need compile-time privacy enforcement; need lowest possible proof latency for simple circuits |
| **D: Application DSL** | Privacy-preserving smart contracts; want compiler-enforced disclosure rules; domain-specific state model | Need general-purpose computation; team wants familiar language; multi-backend portability (except Noir) |

To make these four philosophies concrete: **Philosophy A** is like translating a novel into a language that has no word for half the concepts -- faithful but expensive. **Philosophy B** is like building a custom theater for a specific play -- the acoustics are perfect, but the theater can only stage that one production. **Philosophy C** is like staging the play in any theater in the world by writing it for a universal stage: RISC-V is the universal stage, and the play (your Rust program) works anywhere. **Philosophy D** is like writing a play where the script physically prevents the actors from breaking character -- in Compact, the compiler will not let a private value reach a public surface without explicit consent. Philosophy A serves Ethereum developers who want to reuse existing code. Philosophy B serves ecosystems willing to invest in a custom stack for maximum proof efficiency. Philosophy C serves the broadest developer community with the least friction. Philosophy D serves applications where privacy is not optional -- where the language must prevent the developer from accidentally revealing what should stay hidden.

---

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

PLACEHOLDER_PROVE_REST

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

- [Trusted Setup Ceremonies](../02-setup-ceremonies/trusted-setup.md)
- [Under-Constrained Circuits and Disclosure Boundaries](../03-languages-and-compilers/under-constrained-circuits-and-disclosure-boundaries.md)
- [Witness Generation and Execution Traces](../04-witness-generation/witness-generation-and-execution-traces.md)
- [Arithmetization and Constraint Systems](../05-arithmetization/arithmetization-and-constraint-systems.md)
- [Proof Systems, Recursion, and Folding](../06-proof-systems/proof-systems-recursion-and-folding.md)
- [Cryptographic Primitives and Hardness Assumptions](../07-cryptographic-primitives/cryptographic-primitives-and-hardness-assumptions.md)
- [Verification, Governance, and Data Availability](../08-verification/verification-governance-and-data-availability.md)
- [The Seven-Layer Model](../01-foundations/seven-layer-model.md)
