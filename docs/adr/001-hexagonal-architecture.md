# ADR-001: Adoption of Hexagonal Architecture (Ports & Adapters)

## Status

Accepted

## Context

The Fintech Tech Challenge requires the integration of three distinct domains: Installments, PIX, and Anti-Fraud. These domains have different rates of change and external dependencies.

- **Installments**: Pure mathematical logic, stable.
- **PIX**: High dependency on external PSPs (simulated), stateful, high concurrency.
- **Anti-Fraud**: Rule-based, frequent changes to heuristics.

A traditional Layered Architecture (Controller -> Service -> DAO) often leads to tight coupling between business logic and infrastructure (e.g., SQLAlchemy models leaking into business rules).

## Decision

We will adopt **Hexagonal Architecture (Ports & Adapters)** combined with **Domain-Driven Design (DDD)** principles.

### Key Components

1. **Domain Layer (Core)**: Contains entities and business rules. Pure Python, no dependencies on frameworks (FastAPI, SQLAlchemy).
2. **Application Layer**: Orchestrates use cases (Services). Depends only on Domain and abstract Ports.
3. **Infrastructure Layer (Adapters)**: Implements Ports. Contains Database repositories, API routers, and external integrations.

## Consequences

### Positive

- **Testability**: Domain logic can be tested in isolation without mocking databases or HTTP requests.
- **Flexibility**: We can swap the database (SQLite -> PostgreSQL) or the API framework (FastAPI -> Flask) without touching business rules.
- **Maintainability**: Clear separation of concerns reduces cognitive load when modifying specific domains.

### Negative

- **Complexity**: Requires more boilerplate (DTOs/Schemas vs Domain Models vs ORM Models).
- **Learning Curve**: Developers must understand dependency injection and inversion of control.

## Compliance

All new modules must strictly follow the directory structure:
`app/<domain>/[models.py, schemas.py, service.py, router.py]`
where `service.py` acts as the Application layer and `router.py` as the Primary Adapter.
