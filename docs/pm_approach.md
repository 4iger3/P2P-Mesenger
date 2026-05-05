# Project Management Approach for P2P Messenger

## Workflow Model
- Hybrid workflow: combines Scrum-style planning with Kanban-style execution.
- Use short development stages with clear goals, while keeping a flexible task board for prioritization and review.
- This approach supports rapid iteration and maintains alignment with the centralized client-server architecture.

## Roles and Responsibilities

### Human Developer
- testing, and verifying system behavior
- implements core client and server features according to the rules in AGENTS.md
- leads application architecture and makes final design decisions
- documents the project and maintains README, requirements, and architectural notes

### AI Agent
- is responsible for writing code, helps plan tasks, shape the roadmap, and document the approach
- suggests improvements while following the constraint of using only standard library and `websockets`
- verifies compliance with the client-server architecture and project rules
- generates code examples and fixes on request, but does not replace human oversight

## Collaboration Principles
- Clearly separate design from execution: human makes architectural decisions, agent helps implement and verify
- Avoid unnecessary complexity and keep client/server simplicity
- Continuously refer to AGENTS.md when adding features or changing architecture
