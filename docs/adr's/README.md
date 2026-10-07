# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for TripMate.

ADRs document significant architectural decisions that affect the structure, responsibilities, or long-term evolution of the project.

## When to create an ADR

Create an ADR when a decision:

- defines or changes responsibility boundaries between application layers,
- introduces a new architectural pattern or abstraction,
- changes transaction, persistence, integration, or dependency-management strategy,
- has meaningful trade-offs or alternatives worth documenting,
- is likely to affect future implementation decisions.

Small implementation details, refactors without architectural impact, and temporary solutions do not require an ADR.

## Naming

Use sequential numbering:

```text
0001-service-and-repository-responsibilities.md
0002-...
0003-...
```

## Structure

Each ADR should follow `ADR_TEMPLATE.md` and contain:

- Context
- Decision
- Consequences
- Alternatives Considered
- Follow-up
- Related

## Status

Use one of the following statuses:

- Proposed
- Accepted
- Superseded
- Deprecated

If an ADR replaces an earlier decision, mark the previous ADR as `Superseded` and reference the new ADR.

## Principles

ADRs should be:

- concise,
- focused on the decision and its rationale,
- based on a concrete architectural problem,
- explicit about responsibility boundaries and trade-offs,
- updated through new ADRs rather than silently rewritten when the architecture changes.
