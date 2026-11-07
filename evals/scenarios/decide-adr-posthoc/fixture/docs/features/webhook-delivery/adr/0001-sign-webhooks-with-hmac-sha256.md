---
status: Accepted
owner: "Sam Rivera (Architect)"
reviewers: ["Dana Ortiz (Tech Lead)"]
updated_at: "2026-10-05"
feature_size: "S"
ticket: "WH-40"
---

# 0001 — Sign webhooks with HMAC-SHA256

- **Status:** Accepted
- **Date:** 2026-10-05
- **Deciders:** Sam Rivera, Dana Ortiz

## Context

Merchants must be able to verify that a webhook really came from us (sad.md §1 quality goal 3).

## Decision drivers

- Payload authenticity (sad.md §1 goal 3).
- No extra infrastructure (sad.md §2).

## Considered options

1. **HMAC-SHA256 with a per-merchant shared secret** — simple, widely supported.
2. **Asymmetric signatures (Ed25519)** — no shared secret, but merchants need key tooling.

## Decision outcome

**Chosen:** Option 1. Every merchant SDK already verifies HMAC; no key distribution needed.

## Consequences

**Positive**
- Trivial for merchants to verify.

**Negative**
- Secret rotation needs a dual-secret window.

**Neutral**
- Moving to asymmetric signatures later only changes the signer.

## Links

- Spec: [[../spec.md]]
- SAD: [[../sad.md]] §8
