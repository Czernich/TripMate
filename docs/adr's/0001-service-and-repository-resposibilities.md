# ADR-0001 - Service and Repository Responsibilities

Status: Accepted
Date: 2026-10-07
Owners: TripMate Team
Approved by: TripMate Team

## Context

During implementation of TPM-24, AC2 introduced the following requirement:

> The row is committed and visible through a fresh database session before success is returned. Generated values are available before serialization; flush/commit failures never produce 201.

To satisfy this requirement, the application must explicitly handle persistence synchronization and transaction completion.

This raised a responsibility boundary question between `TripService`, `TripRepository`, and the database session.

## Decision

Responsibilities are divided as follows:

- **Service** — application and business logic only.
- **Repository** — persistence operations related to an entity, including `add()`, `flush()` and `refresh()`.
- **Database session (`get_db`)** — transaction boundary, including `commit()` and `rollback()`.

`TripService` must not depend directly on `AsyncSession` or SQLAlchemy persistence operations.

`TripRepository.add()` is responsible for returning an entity with database-generated values available before serialization.

## Consequences

### Positive

- Service remains focused only on business logic.
- Persistence details are encapsulated in the repository.
- Transaction management remains centralized in `get_db()`.
- Generated values are available before response serialization.

### Negative

- Repository methods such as `add()` become asynchronous.
- `add()` performs both entity registration and persistence synchronization.

### Neutral / Trade-offs

- Repository owns entity-level persistence synchronization, while `get_db()` owns transaction lifecycle.

## Alternatives Considered

### Unit of Work

- Pros:
  - Provides a dedicated abstraction for persistence and transaction coordination.
  - Scales better when multiple repositories participate in one transaction.

- Cons:
  - Introduces additional complexity and abstraction.

- Reason rejected:
  - Not justified yet for the current project scope. It can be introduced when use cases require multiple dependent writes in one atomic transaction.

## Follow-up

Reconsider introducing Unit of Work when persistence flows become more complex or involve multiple repositories.

## Related

- TPM-24
- `TripService`
- `TripRepository`
- `get_db()`
