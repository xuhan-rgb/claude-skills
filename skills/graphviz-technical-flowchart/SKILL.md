---
name: graphviz-technical-flowchart
description: >-
  Create, edit, or review technical flowcharts and architecture diagrams using Graphviz/DOT for models, tensors, data,
  training, software, systems, services, workflows, and deployment. This is the single user-facing Graphviz skill. When
  specialized variables, tensor axes, units, coordinate systems, or abbreviations appear, automatically load and apply
  domain-variable-explainer without requiring a separate user invocation. Verify structure from code/config/docs, keep
  DOT as source of truth, regenerate maintained outputs, and inspect the render.
---

# Graphviz Technical Flowchart

Produce an implementation-backed diagram with one readable primary flow. The user only needs to invoke
`$graphviz-technical-flowchart`.

## Automatic variable routing

Before drafting DOT, detect non-obvious project notation: variables, subscripts, tensor axes, schema/config fields,
masks, metrics, units, normalization, coordinate frames, or transform directions.

If any appear, MUST read and apply `domain-variable-explainer` completely. Trace meanings to code, config, schema, tests,
or authoritative docs; distinguish confirmed meaning from inference; then place explanations inside the relevant node or
in a nearby note in the same functional region. Continue drawing without asking the user to invoke another skill.

If no specialized notation appears, use this skill alone. If the companion is unavailable, state that briefly and use
the same evidence-first analysis as a fallback.

## Workflow

### 1. Establish scope and evidence

Decide whether the artifact shows a complete system, runtime/deployment, training, one subsystem, data lineage, or a
failure/lifecycle path. Make the title, nodes, edges, and legend agree with that scope.

Verify only the necessary surface in code, config, schemas, tests, and current docs:

- components, responsibilities, and real dependency direction
- interfaces, shapes, schemas, request/response types, or state transitions
- optional/config-gated, offline, training-only, runtime, error, history, cache, and feedback paths
- dynamic versus configuration-specific dimensions

Use screenshots for presentation evidence, not hidden behavior. For a local edit, inspect the target region and its direct
connections; do not redesign unrelated regions.

### 2. Build the topology

Default to one left-to-right primary flow:

`Input -> Transform -> Core processing -> Output`

Put optional inputs, controls, history, errors, feedback, and reference data near their consumers. Separate offline,
training-only, maintenance, and failure paths from runtime. Draw an edge only for a real data, control, supervision,
state, or reference dependency.

Group functional regions into concise numbered clusters. Keep the overview readable in one pass; expand only complex or
easy-to-misunderstand modules with a nearby nested subgraph. Preserve stable region numbers during a surgical edit unless
the user asks to renumber.

### 3. Annotate interfaces

Keep an ordinary node to roughly three or four lines:

1. component name
2. core action
3. important interface, state, or shape
4. optional scope/config qualification

When cross-module signal provenance is important, prefer a four-line processing-node contract:

1. component name
2. `输入：` important incoming variables or interface
3. `处理：` the transformation, decision, or state update
4. `输出：` important outgoing variables or interface

Do not apply this mechanically. If a module only filters, gates, synchronizes, or forwards the same clearly named signal,
combine the repeated input/output wording and state only the information that changes. State/decision ellipses may describe
entry conditions and results instead of forcing an input/process/output template.

Use the user's language for ordinary prose. Preserve proper nouns, code/API identifiers, standard abbreviations,
mathematical symbols, and units. Do not leave generic foreign-language boilerplate when a natural user-language label
exists.

Annotate only important interfaces:

- models: symbolic shapes and axis semantics
- data pipelines: schemas, record types, partitions, or artifacts
- services: request/response/event types
- workflows: artifacts or state transitions

Use symbolic dynamic dimensions and mark fixed values as configuration-specific. Put central variable definitions inside
the node; put shared definitions in a nearby regional note, one symbol-to-meaning mapping per line. A global legend is for
edge styles and truly global conventions, not the sole explanation of local notation.

With `splines=ortho`, keep edge text to a short interface identifier such as a field name, type, or unit. Do not put a
formula, transformation, sentence, or repeated source/target description in `label` or `xlabel`; place it inside the
consumer node or a nearby note instead. If the connected nodes already establish the interface unambiguously, leave the
edge unlabeled. This prevents Graphviz from placing long external labels over nodes, arrows, or cluster titles.

Prefer node contracts over edge text for short links and for consumers with several incoming edges. Label only a genuinely
long connection whose source would otherwise be hard to trace, and keep that label to one line of exact output identifiers
near the consumer end. Do not insert visible proxy/input-interface boxes solely to carry labels unless the user explicitly
requests that notation. If a long-line label overlaps anything after rendering, remove it and rely on the consumer's
`输入：` line; readability takes priority over labeling every edge.

### 4. Separate execution scopes

- Keep ground truth and losses out of the inference path.
- Terminate supervision at its loss/objective.
- Distinguish stop-gradient, offline, optional, and error branches when shown.
- Put deployment outputs on the primary path.
- If the user requests deployment only, omit the entire training region and its residual wording.

When removing a region, also remove its nodes, edges, exclusive legend entries, stale labels, obsolete invisible layout
constraints, and titles that overstate the remaining scope. Do not leave an empty cluster.

### 5. Edit the DOT source

When `.dot` exists, edit it and regenerate derived artifacts; do not hand-edit generated SVG/PDF/PNG as the primary
change.

Start with natural topology:

```dot
graph [
  rankdir=LR,
  splines=ortho
];
```

Do not set `ratio`, `size`, or fixed positions unless the target medium requires them. Use `constraint=false` only for a
genuinely auxiliary edge that distorts the primary rank.

Reduce clutter in this order:

1. remove false/redundant dependencies
2. move auxiliary paths near their consumers
3. disable only auxiliary constraints
4. extract a complex subgraph
5. tune `nodesep` and `ranksep`

Audit invisible edges after every structural deletion. With `splines=ortho`, a stale invisible anchor can distort layout
or trigger a Graphviz routing assertion; remove it before attempting spacing workarounds.

### 6. Render and verify

Regenerate only formats the user requested or the project already maintains:

```sh
dot -Tsvg diagram.dot -o diagram.svg
dot -Tpdf diagram.dot -o diagram.pdf
dot -Tpng diagram.dot -o diagram.png
```

Capture and resolve Graphviz warnings. Inspect the final rendering; do not claim visual verification without doing so.

Check:

- primary-flow direction and region numbering
- runtime/offline/training/optional/error separation
- unnecessary crossings or edges entering the wrong cluster
- overlap, clipping, whitespace, font size, and cluster-title readability
- every edge label at the affected region: no text may touch or cover a node border, node text, arrowhead, another edge
  label, or cluster title; inspect a native-resolution crop when the full graph scales text down
- every affected rectangular processing node states its input, processing, and output, or has an intentional documented
  omission because the same signal passes through unchanged in meaning
- long-line labels are single-line output identifiers; short edges and crowded multi-input consumers do not repeat the
  node contract
- interface and variable-annotation accuracy
- legend consistency and absence of stale removed content

When available, validate SVG as XML, inspect PDF page metadata, and check PNG dimensions.

## Default edge semantics

Use the project's established convention when one exists; otherwise:

- solid: primary runtime/data flow
- red dashed: error, supervision, or loss
- gray dashed: offline, reference, or non-mutating dependency
- purple dashed: optional or auxiliary branch

Explain each used style once and remove unused legend entries. Keep edge labels to short identifiers; orthogonal routing
handles labels poorly. Move long or repeated edge text into the consumer node, and remove any edge label that overlaps
the rendered graph rather than trying to fix it with spacing alone.

## Target medium

Do not reject a natural graph merely because it is wide. Compact or split only for a stated paper, portrait, slide, print,
or embedded-panel constraint. When splitting, keep one overview and make detail views subordinate to it.

## Completion checklist

- [ ] Scope/title and included branches agree.
- [ ] Components, interfaces, and edges are evidence-backed.
- [ ] One primary flow is dominant; auxiliary scopes are separated.
- [ ] Specialized variables triggered `domain-variable-explainer` automatically and are explained locally.
- [ ] DOT remains the source of truth; maintained formats were regenerated.
- [ ] Graphviz has no unresolved warnings.
- [ ] The final rendering was inspected for accuracy, readability, overlap, and clipping.
