# Service Interface Specification

## Purpose

This capability defines CLI, Python, Web, MCP, and local model-bridge access to
the same digital-twin behavior while keeping service exposure secondary to the
research model.

## Requirements

### Requirement: SVC-001 Shared core behavior

All service interfaces SHALL call the shared scenario, estimator, learning, and
recommendation behavior rather than maintain independent research models.

#### Scenario: Evaluating equivalent inputs

- **WHEN** Python, Web, and MCP interfaces receive equivalent scenario, time, device, point, and estimator inputs
- **THEN** their three-factor numerical results SHALL agree within serialization precision
- **AND** interface-specific formatting SHALL not change the underlying model

### Requirement: SVC-002 Secondary service-layer positioning

MCP, Web, and local language-model bridges SHALL be presented as access and
demonstration layers.

#### Scenario: Describing service novelty

- **WHEN** an abstract, conclusion, diagram, or presentation describes MCP or Web
- **THEN** it SHALL state that these layers expose the spatial-twin capability
- **AND** it SHALL not replace sparse sensing or impact learning as the primary contribution

### Requirement: SVC-003 MCP tool surface

The local stdio MCP server SHALL expose the five supported interaction flows:
`initialize_environment`, `sample_point`, `learn_impacts`,
`run_window_direct`, and `rank_actions`.

#### Scenario: Listing tools

- **WHEN** an MCP client requests the tool list
- **THEN** all five supported tools SHALL be returned with input schemas
- **AND** removed legacy tools SHALL not be presented as current flows

#### Scenario: Calling a tool

- **WHEN** a valid MCP tool call is received
- **THEN** the server SHALL return a structured result derived from the shared core
- **AND** JSON-RPC or validation failures SHALL be returned as explicit errors

### Requirement: SVC-004 Stateful MCP initialization

Point sampling, impact learning, direct-window simulation, and ranking SHALL use
an explicit registered environment state.

#### Scenario: Initializing an environment

- **WHEN** `initialize_environment` succeeds
- **THEN** the state SHALL preserve base scenario, indoor baseline, outdoor boundary, devices, furniture, default timing, and estimator preference
- **AND** the response SHALL summarize the effective state

#### Scenario: Calling a state-dependent tool too early

- **WHEN** a state-dependent tool is called before required environment state exists
- **THEN** the server SHALL return a precondition error
- **AND** it SHALL not silently initialize an unrelated scenario

### Requirement: SVC-005 Interface validation

Service interfaces SHALL reject invalid coordinates, incomplete targets,
unsupported device kinds, malformed numeric values, and incompatible learning
records with actionable errors.

#### Scenario: Invalid point input

- **WHEN** a service receives an out-of-room point
- **THEN** it SHALL identify the coordinate-bound violation
- **AND** no field value SHALL be returned for the invalid point

#### Scenario: Invalid recommendation input

- **WHEN** a point sample or any comfort target is missing
- **THEN** ranking SHALL fail validation
- **AND** candidate order SHALL not be returned

### Requirement: SVC-006 Local-only deployment boundary

The current MCP server and Web demo SHALL be treated as local prototype
interfaces without implied remote authentication, tenancy, or production
security.

#### Scenario: Documenting deployment

- **WHEN** deployment capability is described
- **THEN** MCP SHALL be identified as local stdio
- **AND** Web SHALL be identified as a local demonstration server
- **AND** remote OAuth, multi-user authorization, and production operations SHALL be out of scope
