# Weekly comparison package

## ADDED Requirements

### Requirement: WPK-901 Frozen evidence reporting

Retrospective reporting SHALL verify complete source metrics without rerunning experiments or changing old decisions.

#### Scenario: An old result is cited

- **WHEN** a method result appears in the review paper
- **THEN** it SHALL match named frozen evidence and retain its synthetic boundary

### Requirement: WPK-902 Review manuscript is a bounded derivative

The candidate manuscript SHALL preserve existing scientific claims and distinguish explanations from causal validation.

#### Scenario: Venue remains undecided

- **WHEN** a candidate-format PDF is generated
- **THEN** the readiness record SHALL state no submission or venue selection and SHALL not invent a paper identifier

### Requirement: WPK-903 Observable weekly delivery

The weekly package SHALL include first-person offline HTML, source links and fresh observed QA bound to final hashes.

#### Scenario: Artifact bytes change

- **WHEN** the report is rebuilt
- **THEN** earlier visual observations SHALL not be silently reused for different bytes
