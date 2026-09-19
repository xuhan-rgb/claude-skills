---
name: domain-variable-explainer
description: Explain project-specific variables, symbols, subscripts, tensor dimensions, schema fields, configuration keys, metrics, masks, coordinate conventions, and abbreviations from code, formulas, papers, logs, APIs, or technical documents. Use when a user asks what a variable means, points to unexplained notation, wants a variable glossary, needs every tensor axis explained, or asks to annotate specialized variables near where they appear. Trace evidence before interpreting names; distinguish confirmed meaning from inference.
---

# Domain Variable Explainer

Explain specialized notation so a reader can understand the artifact without guessing what a name, subscript, axis, unit,
or coordinate system means.

This skill is independent of presentation format. It applies to:

- source code and function signatures
- mathematical formulas and papers
- tensor shapes and model interfaces
- configuration files and command-line arguments
- logs, metrics, and experiment dashboards
- request/response schemas and database fields
- tables, diagrams, reports, and technical documentation

## Core rule

Never explain a project-specific variable from its spelling alone when evidence is available.

Trace the variable through the smallest useful evidence chain:

`definition or construction -> transformations -> consumers -> externally visible effect`

Prefer evidence in this order:

1. executable code, type definitions, and assertions
2. tests and fixtures
3. active configuration and schema definitions
4. current project documentation
5. upstream specifications, papers, or official references
6. naming-based inference

Label naming-based interpretations as inference. Do not silently turn convention into fact.

## What every explanation should resolve

For each requested variable or symbol, determine as many of these as the artifact supports:

1. **Exact identifier** — preserve the spelling, capitalization, subscript, and namespace.
2. **Plain-language meaning** — what real object, quantity, state, or concept it represents.
3. **Role** — input, parameter, index, mask, feature, target, prediction, metric, cache, or control value.
4. **Type and structure** — scalar, enum, string, record, list, matrix, tensor, optional value, and dtype when relevant.
5. **Shape and axes** — explain every axis semantically, not just the bracketed dimensions.
6. **Units and scale** — meters, seconds, pixels, radians, probability, normalized range, log scale, and so on.
7. **Reference frame or convention** — coordinate frame, axis order, sign convention, indexing base, orientation, or timestamp basis.
8. **Source** — where it is read, constructed, predicted, or configured.
9. **Transformations** — normalization, projection, padding, masking, aggregation, detaching, encoding, or conversion.
10. **Consumers** — which functions, modules, equations, reports, or outputs use it.
11. **Scope and lifecycle** — training-only, inference-only, optional, cached, per-sample, per-frame, persistent, or temporary.
12. **Constraints** — allowed values, dynamic versus fixed dimensions, validity conditions, and invariants.

Do not invent missing items. State “not established from the inspected sources” when necessary.

## Tensor and shape explanations

A tensor shape is incomplete until every axis has a meaning.

For a tensor written as `[A, B, C]`, answer:

- what entity each axis counts or encodes
- whether each size is fixed, configured, or dynamic
- whether an axis is a population count, time length, channel width, feature width, or coordinate tuple
- whether padding or a validity mask changes the effective count
- whether the layout changes between producer and consumer

Explicitly distinguish commonly confused concepts:

- number of items versus feature width
- batch size versus sequence length
- channels versus spatial dimensions
- raw coordinates versus learned features
- token count versus embedding dimension
- normalized values versus physical units
- current-time values versus history or future indices

Do not say only “it is an N by D tensor.” Say what one row represents and what one element or feature vector represents.

## Indices, subscripts, and superscripts

Explain every non-obvious index at its first relevant use.

Check whether an index denotes:

- time
- batch member
- camera, sensor, agent, or object
- network stage or pyramid level
- token, point, voxel, or query
- class or channel
- iteration, diffusion step, or optimization step
- coordinate frame or method variant

Do not assume the same letter has the same meaning across scopes. A symbol such as `K` may be a matrix in one module and
an attention key in another. Qualify it by context when ambiguity exists.

## Units, coordinates, and conventions

For geometry, robotics, simulation, time-series, and scientific variables, actively search for:

- source and destination coordinate frames
- transform direction
- row-major or column-major convention
- angle unit and wrap range
- spatial unit and normalization scale
- time unit, sampling interval, and horizon
- axis order and handedness
- inclusive/exclusive bounds and indexing convention

If these cannot be established, call out the ambiguity because it can change the interpretation materially.

## Language and terminology

Write explanations in the user's language.

- Preserve exact code identifiers, mathematical symbols, official model names, API names, standard abbreviations, and units.
- Translate ordinary descriptive prose when a natural translation exists.
- On first occurrence, pair an opaque identifier with a plain-language explanation.
- Do not rename the underlying variable unless the user explicitly asks for a code change.

The goal is readable explanation without losing traceability back to the source.

## Placement in an existing artifact

When the user asks to add explanations to an existing document, table, formula, diagram, or UI:

- put the definition at the first relevant occurrence or in the same local section/module
- use one variable-to-meaning mapping per line when several symbols appear together
- keep a global glossary only as a supplement, not the sole explanation for locally dense notation
- repeat a short definition when that prevents a long lookup and the repetition does not create clutter
- preserve the artifact's existing visual and editorial style

If the user only asks for an explanation or review, do not modify the artifact.

## Workflow

### 1. Establish scope

Identify the exact variables and the artifact or execution path in which they appear. If a symbol has multiple plausible
scopes, separate them before explaining it.

### 2. Inventory notation

Collect the requested variables plus any immediately dependent symbols needed to make them understandable. Do not expand
into an unrelated full-project glossary unless requested.

### 3. Trace evidence

Search definitions, assignments, shape assertions, type annotations, configuration, tests, and consumers. Follow aliases
and renamed fields when necessary.

### 4. Resolve semantics

Build an internal record for each variable:

```text
identifier:
meaning:
role:
type / shape:
axis meanings:
unit / frame:
source:
transformations:
consumers:
scope / constraints:
evidence:
confidence:
```

### 5. Choose the lightest output

- one to three variables: short per-variable paragraphs or bullets
- repeated field mappings: a compact table
- many related symbols: a scoped glossary grouped by module or domain
- dense tensor notation: a line-by-line shape breakdown
- existing artifact edit: local annotations near first occurrence

### 6. Verify

Before finishing, check:

- every requested identifier is covered
- every displayed tensor axis is explained
- units and frames are stated or explicitly unresolved
- producer and consumer descriptions agree
- training/inference or optionality claims match the execution path
- inferred meanings are marked as inference
- code identifiers remain exact and searchable
- empirical or externally sourced claims have appropriate evidence

## Recommended output table

Use only the columns that add value:

| Variable | Meaning | Type / shape and axes | Unit / frame | Source -> consumer | Evidence | Confidence |
|---|---|---|---|---|---|---|

For a single tensor, a clearer format is often:

```text
variable: plain-language meaning
shape: [axis_1, axis_2, ...]
axis_1: what it counts; fixed/configured/dynamic
axis_2: what it represents; fixed/configured/dynamic
unit/frame: ...
produced by: ...
used by: ...
```

## Confidence language

- **Confirmed** — directly established by executable code, schema, assertion, or authoritative specification.
- **Strongly supported** — converging evidence from tests, configs, and consumers.
- **Inferred** — plausible from naming or convention but not directly established.
- **Unresolved** — sources conflict or required evidence is absent.

Use calibrated language. Do not present an inferred expansion of an abbreviation as a confirmed project definition.

## Anti-patterns

Avoid:

- expanding an acronym without checking how the project uses it
- copying a shape without explaining its axes
- describing an index as “some dimension”
- omitting units or coordinate frames when they affect meaning
- mixing raw, normalized, and decoded values under one name
- confusing a feature count with feature width
- using a distant glossary as the only explanation for dense local notation
- explaining every familiar programming variable when only domain-specific notation is unclear
- changing code or documentation when the user asked only for analysis
- burying uncertainty behind confident prose
