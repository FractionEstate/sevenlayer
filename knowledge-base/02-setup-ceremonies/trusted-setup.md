# Trusted Setup Ceremonies

## Overview

A trusted setup ceremony is the process by which a zero-knowledge proof system's foundational mathematical parameters — the Structured Reference String (SRS) — are generated and the dangerous secret used to create them is destroyed. The security of every proof in the system depends on the integrity of this process.

## The Fair Shuffle Problem

The intuition behind a trusted setup is a card-shuffling analogy: if nobody trusts the dealer to shuffle fairly, you need a protocol that produces a provably fair shuffle even though someone must do the physical shuffling.

One solution: get a large number of people to each add randomness to the shuffle, one after another. Each person makes an unpredictable change, passes the result on, and destroys their memory of what they did. The result is fair as long as *even one* participant acted honestly — genuinely random and genuinely forgetful.

The Ethereum KZG Summoning Ceremony (2023) used exactly this approach with 141,416 participants — the largest cryptographic ceremony in history. What they were "shuffling" was a set of mathematical parameters called a Structured Reference String (SRS).

## The Structured Reference String (SRS)

A Structured Reference String is a list of specially constructed points on an elliptic curve. These points let you measure certain things (verify polynomial evaluations) but do not let you reconstruct the manufacturing process (recover the secret value from the markings). The scheme was invented by Kate, Zaverucha, and Goldberg in 2010 and is universally known as **KZG**.

The secret value used to generate the SRS is called the **trapdoor**, or more evocatively, **toxic waste**. If anyone retains knowledge of the trapdoor, they can forge proofs of false statements — proving that 2 + 2 = 5, that an empty bank account holds a billion dollars, or that an invalid transaction is valid. No one would be able to tell the forged proof from a real one.

### The Algebra

The SRS is a sequence of elliptic curve points:

$$[s]G, [s^2]G, [s^3]G, \ldots, [s^d]G$$

where $s$ is the toxic waste and $G$ is the generator point. During the ceremony, each participant $i$ takes the current SRS, multiplies every point by their own secret $\tau_i$, and passes the result forward. After all $N$ participants have contributed, the effective secret is:

$$s = \tau_1 \cdot \tau_2 \cdot \tau_3 \cdots \tau_N$$

To recover $s$, an adversary must know *every* $\tau_i$. The secrets do not add — they multiply. A product of unknowns is unknown.

## The 1-of-N Trust Model

Security holds if even one participant out of N genuinely destroyed their contribution. This is the **1-of-N trust model**.

With six participants, a well-resourced adversary could conceivably investigate, coerce, or compromise all six. With 141,416 anonymous participants from around the world, many contributing through ephemeral browser sessions, collusion becomes operationally infeasible. The security is sociological as much as cryptographic: you are not trusting a specific person — you are trusting that it is impossible to corrupt *everyone*.

**Key insight:** A ceremony is only as *insecure* as its *strongest* link. This is the inverse of the chain metaphor (weakest link). The 1-of-N model's structural optimism means you don't need every participant to be careful — you need the population to be large and diverse enough that at least one participant is careful enough.

## Evolution of Ceremonies

| Year | Ceremony | Participants | Notes |
|------|----------|-------------|-------|
| 2016 | Zcash Sprout | 6 pre-selected | Air-gapped machines physically destroyed. Two days. First production trusted setup. |
| 2018 | Zcash Sapling | ~90 (87 phase 1, 91 phase 2) | BGM17 "MMORPG" framework. 2.5 hours per contribution. First scalable ceremony protocol. |
| 2019–2022 | Proliferation | Dozens of projects | Tornado Cash, Hermez, Aztec, Loopring — mostly Groth16 on BN254. |
| 2023 | Ethereum KZG Summoning | 141,416 | Permissionless, web-based. Ran for months. Maximum-scale "more-the-merrier" model. |
| 2025+ | On-chain ceremonies | TBD | Smart-contract-mediated setups, contributions verified on-chain, no coordinator needed. |

## The Human Interior of a Ceremony

### Zcash Sprout (2016)

Six participants from different countries, using air-gapped computers purchased new and never connected to the internet. Each computer was destroyed after use:

- **Peter Todd** purchased a laptop with cash from a randomly chosen store, generated his contribution in a room with no wireless signals, and filmed himself incinerating the machine. The computer had touched a secret and the protocol required it cease to exist.
- **Andrew Miller** used a CD-ROM-based operating system running entirely in volatile memory — nothing was ever written to permanent storage. When powered down, the secret evaporated with the electrical charge in the RAM chips.

These are not colorful anecdotes — they are the actual security analysis. Evaluating the ceremony requires reasoning about furnaces, cash purchases, volatile memory, and the thermal decay time of DRAM cells.

### Ethereum KZG Summoning (2023)

The interface was a web page at ceremony.ethereum.org. Participants connected a wallet, waited in a queue, and their browser generated a random number, performed elliptic curve multiplication, submitted the result, and discarded the secret. The entire contribution took 20 seconds to 2 minutes.

141,416 people participated from bedrooms, offices, and coffee shops worldwide — on phones, tablets, gaming rigs, and ancient ThinkPads. The mathematics does not require informed consent; it requires honest randomness. A participant who clicks because a friend told them to contributes exactly as much security as one who has read every paper on polynomial commitments since 2010.

## Ritual as Protocol, Protocol as Ritual

The progression from Sprout to the KZG Summoning traces the **democratization of a priestly function**:

- **2016:** Generating contributions required expertise, specialized equipment, and intelligence-agency-grade operational security. Participants were effectively priests — a small caste entrusted with a dangerous sacrament.
- **2023:** The priestly function was automated and distributed. The browser handled cryptography, hardware RNG provided entropy, and the protocol enforced sequencing. The ceremony became *permissionless* — anyone could join, no one could be excluded.

This inversion changes how we think about cryptographic system foundations. The traditional model assumes a small number of trusted parties performing critical operations (certificate authorities, key escrow agents). The ceremony model replaces this with something closer to a vote of presence.

## The Bug That Was Not a Ceremony Failure

In 2019, vulnerability CVE-2019-7167 in the BCTV14 construction used by Zcash would have allowed unlimited counterfeiting of tokens — and it had nothing to do with the trusted setup ceremony. The flaw was in the cryptographic construction itself.

**Lesson:** Ceremony integrity is necessary but not sufficient. You can build a perfect stage and still get the show wrong. Security is a conjunction: every link must hold simultaneously.

## Sociology of Trust at Scale

The Ethereum KZG ceremony achieved social credibility through three mechanisms:

1. **Radical openness** — Source code published, coordination protocol specified publicly, every contribution logged in a publicly verifiable transcript.
2. **Permissionless participation** — Anyone with an Ethereum address could contribute, creating collective ownership rather than delegated trust.
3. **Diversity of entropy sources** — Different hardware, operating systems, network configurations, physical locations, and jurisdictions. The heterogeneity of 141,416 independent computing environments is itself a security property.

A fourth mechanism: the **unforgeable cost of participation**. Each contributor spent real time waiting and computing. Thousands of person-hours of aggregate attention signal genuine commitment.

## Trust-Minimized, Not Trustless

"If the toxic waste is destroyed, how does anyone *know* it was actually destroyed?"

Nobody knows. "Destruction" is a physical claim about a digital artifact. You cannot prove you deleted something from your own computer. The 1-of-N model rests on trusting that at least one person is honest, *and* that their computer was not compromised, *and* that no backup exists, *and* that no side-channel leaked the secret during generation.

This is weaker than trusting a single entity. But it is not zero trust. The accurate word is **trust-minimized**.

## Key Takeaways

- A trusted setup ceremony generates the SRS and destroys the toxic waste (trapdoor) used to create it
- The 1-of-N trust model means security holds if even one participant was honest — the ceremony's security is determined by its strongest link, not its weakest
- Ceremonies have evolved from 6 pre-selected participants (Zcash Sprout, 2016) to 141,416 permissionless contributors (Ethereum KZG, 2023)
- The multiplicative structure of secrets ($s = \tau_1 \cdot \tau_2 \cdots \tau_N$) is why the 1-of-N model works mathematically
- Ceremony integrity is necessary but not sufficient — the BCTV14 bug (CVE-2019-7167) proved that construction correctness is independent of ceremony correctness
- Trusted setups are trust-minimized, not trustless — the distinction matters at every layer

## Related Topics

- [Transparent Setup](transparent-setup.md) — the alternative that requires no ceremony
- [Elliptic Curves and Field Selection](curves-and-fields.md) — the mathematical foundations underlying the SRS
- [The ADOPT Framework](adopt-framework.md) — evaluating ceremony quality across five properties
