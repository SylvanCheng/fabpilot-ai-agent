# ADR-0003: Separate, read-only business database

- Status: Accepted
- Date: 2026-11-02

## Context
The agent will run LLM-generated queries. In a real fab the business data (MES, metrology,
yield) belongs to other systems and must never be modified by an assistant.

## Decision
Two databases: `fab_business` (source data, accessed by role `fab_reader` with SELECT only and
`default_transaction_read_only = on`, plus a read-only session flag in the engine) and
`fabpilot_app` (agent-owned state). The generator writes with a separate `fab_loader` role.

## Consequences
Defence in depth against destructive SQL. Mirrors production reality, where the business DB is a
replica owned by another team. Cross-database joins are impossible by design.
