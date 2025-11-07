# Architectural Decision Records (ADRs)

An Architectural Decision (AD) is a justified software design choice that addresses a functional or non-functional requirement that is architecturally significant. An Architectural Decision Record (ADR) captures a single AD and its rationale.

For more information [see](https://adr.github.io/)

## How are we using ADRs to track technical decisions?

1. Copy `docs/decisions/adr-template.md` to `docs/decisions/NNNN-title-with-dashes.md`, where NNNN indicates the next number in sequence.
    1. Check for existing PR's to make sure you use the correct sequence number.
    2. There is also a short form template `docs/decisions/adr-short-template.md`
2. Edit `NNNN-title-with-dashes.md`.
    1. Status must initially be `proposed`
    2. List of `deciders` must include the github ids of the people who will sign off on the decision.
    3. You should list the names or github ids of all partners who were consulted as part of the decision.
    4. Keep the list of `deciders` short. You can also list people who were `consulted` or `informed` about the decision.
3. For each option list the good, neutral and bad aspects of each considered alternative.
    1. Detailed investigations can be included in the `More Information` section inline or as links to external documents.
4. Share your PR with the deciders and other interested parties.
   1. Deciders must be listed as required reviewers.
   2. The status must be updated to `accepted` once a decision is agreed and the date must also be updated.
   3. Approval of the decision is captured using PR approval.
5. Decisions can be changed later and superseded by a new ADR. In this case it is useful to record any negative outcomes in the original ADR.

## ADR Process for This Project

During implementation of the agent-template specification, create ADRs for:

- Architecture patterns (tool registration, dependency injection, event bus)
- Technology choices (framework selection, library decisions)
- Design patterns (component interaction, abstraction layers)
- API designs (public interfaces, method signatures, response formats)
- Naming conventions (class names, module structure, terminology)
- Testing strategies (test organization, mocking patterns, coverage targets)
- Performance trade-offs (caching strategies, optimization choices)
- Security decisions (authentication methods, data handling)
- UI/UX patterns (display formats, interaction models)

**Rule of thumb**: If the decision could be made differently and the alternative would be reasonable, document it with an ADR.

## Expected ADRs for Foundation Implementation

Based on the foundation specification, the following ADRs should be created:

1. **ADR-0001: Class-based Toolset Architecture** - Tool registration approach
2. **ADR-0002: Event Bus Pattern for Loose Coupling** - Middleware/display decoupling
3. **ADR-0003: Custom Exception Hierarchy Design** - Error type structure
4. **ADR-0004: Agent Response Format** - Tool response structure (success/error)
5. **ADR-0005: Configuration Management Strategy** - Config approach (env vars, dataclasses)
6. **ADR-0006: CLI Argument Design** - CLI flags and command structure
7. **ADR-0007: Testing Strategy and Coverage Targets** - Test organization and coverage goals
8. **ADR-0008: Module and Package Naming Conventions** - Python naming standards
9. **ADR-0009: Display Output Format and Verbosity Levels** - UI/UX output modes
10. **ADR-0010: Session Management Architecture** - Session persistence approach

## Templates

- **Full Template**: `adr-template.md` - Comprehensive template with all sections
- **Short Template**: `adr-short-template.md` - Simplified template for smaller decisions

## Reference Examples

See `ai-examples/agent-framework/docs/decisions/` for real-world examples of well-structured ADRs.
