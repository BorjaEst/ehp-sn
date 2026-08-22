---
name: "Review documentation quality"
description: "Use when reviewing or correcting project documentation for semantic correctness, content adequacy, evidence, and consistency against project intent and authoritative sources. Supports review-only or review-and-fix mode."
argument-hint: "Documentation scope to review (default: README.md and docs/**)"
agent: "agent"
tools: [search, read, edit, web]
---

# Project Documentation Review and Correction

## Task

Perform a rigorous review of this repository's project documentation.

Scope:

${input:scope:Documentation scope to review, for example `README.md and docs/**`. Default: `README.md and docs/**`}

Mode:

${input:mode:Use `review-only` or `review-and-fix`. Default: `review-and-fix`}

Additional objective or concern:

${input:focus:Optional specific concern, document, requirement, architecture area, or quality issue to prioritize}

Your objective is not to maximize documentation, rewrite everything, impose a generic documentation framework, or make the prose merely sound better.

Your objective is to ensure that the documentation represents project intent correctly, contains the information required for its actual responsibility, uses appropriate evidence, remains internally coherent, and is no more complex than necessary.

Apply the smallest justified correction that produces a materially better and more reliable documentation system.

---

# 1. Governing model

Use the following repository model throughout the task.

```text
docs/
    authoritative location for project knowledge
    and intended project state

project governance
    determines which documented material
    constitutes accepted project intent

src/
    evidence of implemented behavior

tests/
    executable verification evidence where
    software testing is appropriate

other verification mechanisms
    evidence for claims not appropriately
    established through software tests

external authorities
    govern externally defined claims within
    their legitimate scope

.github/
    controls agent behavior but does not define
    project requirements, architecture, or design
```

The central rule is:

> Project intent must be derived from explicit project knowledge, not reconstructed from implementation artifacts.

Do not treat current implementation as automatically authoritative for requirements, architecture, or design.

Documentation may legitimately describe an accepted target state that has not yet been implemented.

Implementation may legitimately expose errors or omissions in earlier project intent.

When implementation and documentation differ, classify the discrepancy before changing either side.

Possible classifications include:

- accepted target state not yet implemented;
- implementation defect;
- obsolete documentation;
- intentional deviation;
- unapproved implementation choice;
- partial migration;
- experimental implementation;
- unresolved inconsistency.

Do not silently reconcile documentation with implementation.

---

# 2. Establish context before evaluating

Before making substantive changes, establish the relevant context from the repository.

Determine, where evidence is available:

- project objective;
- system boundary;
- relevant stakeholders or intended users;
- accepted requirements;
- external obligations;
- project constraints;
- material assumptions;
- accepted architecture;
- relevant bounded designs;
- significant accepted decisions;
- implementation state where comparison is relevant;
- available verification evidence;
- terminology whose meaning affects correctness;
- governance signals indicating whether documented material is accepted, proposed, draft, deprecated, or superseded.

Do not invent missing context.

If a material point cannot be established from available evidence, mark it as unresolved.

---

# 3. Respect semantic ownership

Evaluate every document according to its actual responsibility.

## `README.md`

Primary responsibility:

> Repository orientation and navigation.

It should normally make it possible to determine:

- what the project is;
- why it exists;
- relevant current status;
- how to build, run, or use it where appropriate;
- where authoritative project documentation resides;
- where development instructions reside.

The README may summarize project documentation for orientation.

It must not become a competing source of detailed requirements, architecture, or technical design.

When duplicated authoritative content exists in the README and `docs/`, prefer a concise summary plus navigation unless duplication has a demonstrated purpose.

---

## `docs/requirements.md`

Primary responsibility:

> Define what the system must satisfy and the significant constraints within which acceptable solutions must operate without prescribing implementation unnecessarily.

Distinguish where relevant:

- system requirements;
- external obligations;
- project constraints;
- assumptions.

Review requirements for:

- necessity;
- clarity;
- precision;
- internal consistency;
- feasibility;
- verifiability;
- appropriate traceability;
- explicit assumptions;
- appropriate implementation independence.

Do not mistake implementation choices for semantic requirements.

Do not remove a genuine solution constraint merely because it is implementation-specific if the project has actually constrained that solution space.

Do not invent requirements from architecture, source code, frameworks, standards, or common practice.

---

## `docs/architecture.md`

Primary responsibility:

> Describe architecturally significant organization and intended system behavior.

Evaluate only concerns relevant to the actual system, including where applicable:

- purpose and scope;
- system context;
- stakeholders and significant concerns;
- system boundaries;
- architectural constraints;
- major building blocks;
- responsibilities;
- relationships;
- externally significant interfaces;
- data ownership;
- principal runtime interactions;
- deployment;
- cross-cutting mechanisms;
- quality-driving choices;
- architectural principles;
- risks;
- technical debt;
- relationships to significant decisions.

Do not impose sections merely because an architecture framework defines them.

Do not turn architecture documentation into detailed source-code documentation.

---

## `docs/design/*.md`

Primary responsibility:

> Describe how a bounded technical problem is intended to be realized within accepted requirements and architecture.

Prefer problem-oriented design subjects over documents that merely mirror implementation folders or classes.

Depending on the actual problem, inspect:

- problem;
- objective;
- scope;
- applicable requirements;
- constraints;
- assumptions;
- external contracts;
- proposed realization;
- responsibilities;
- interfaces;
- data semantics;
- runtime behavior;
- state or lifecycle behavior;
- failure behavior;
- security implications;
- operational implications;
- alternatives;
- trade-offs;
- unresolved questions;
- verification.

These are candidate concerns, not mandatory headings.

Do not expand a small design merely to make it appear comprehensive.

---

## `docs/decisions/*.md`

Primary responsibility:

> Preserve significant rationale whose loss would impose future engineering cost.

An ADR is justified where a decision materially:

- constrains later design;
- has substantial reversal cost;
- resolves a significant trade-off;
- intentionally deviates from an expected approach;
- affects major quality properties;
- affects compatibility or operations;
- has important competing alternatives.

Distinguish:

```text
architecture/design
    resulting accepted intent

ADR
    significant decision rationale
```

Do not create ADRs for routine implementation choices merely because alternatives existed.

Do not invent historical rationale.

---

## `docs/references.md`

Primary responsibility:

> Register external sources that materially constrain, define, support, explain, evaluate, or validate project reasoning.

Treat it as a registry, not an authority broker.

A source does not become authoritative merely because it appears in `references.md`.

A source does not cease to be relevant merely because it has not yet been registered.

Include only materially relevant references.

Where lifecycle changes matter, record enough information to establish applicability, such as:

- version or edition;
- lifecycle status;
- role;
- applicable project area;
- access level;
- relevant notes;
- last verification date where useful.

---

## Optional documents

Do not require optional documents merely because they are common.

Create or retain `docs/glossary.md` only when controlled terminology materially improves correctness.

Create or retain `docs/development.md` only when development workflow information no longer fits cleanly in the README.

Do not create generic categories such as:

```text
docs/standards/
docs/views/
docs/quality/
docs/policies/
docs/specifications/
docs/traceability/
```

unless the project contains enough independently meaningful material to justify them.

---

# 4. Determine authority per claim

Do not use a universal hierarchy of sources.

For every material disputed or externally governed claim, determine which source class legitimately governs it.

Examples:

```text
What must this project satisfy?
    → accepted requirements
      + applicable external obligations

Which architecture has the project selected?
    → accepted architecture
      + relevant accepted decisions

What does protocol operation X mean?
    → applicable normative specification

Does framework version X support Y?
    → official version-specific implementation documentation
      + authoritative implementation evidence where necessary

Will design X meet measurable objective Y?
    → project measurements
      + applicable empirical evidence

How should ordinary prose be expressed?
    → project terminology/conventions
      + applicable editorial guidance
```

Keep these external-source classes distinct:

### Normative authorities

Examples:

- legislation;
- regulation;
- contracts;
- normative protocol specifications;
- normative interface specifications;
- applicable industry specifications.

These may govern obligations or externally defined semantics.

### Implementation authorities

Examples:

- official language documentation;
- official framework documentation;
- official platform documentation;
- official API documentation;
- vendor product documentation;
- authoritative implementation evidence.

Treat version-sensitive claims as version-sensitive.

### Supporting evidence

Examples:

- peer-reviewed research;
- reference architectures;
- reference implementations;
- benchmarks;
- case studies;
- engineering literature;
- experience reports;
- relevant community evidence.

Supporting evidence informs judgment.

It does not automatically create a project requirement or accepted architecture.

---

# 5. Evaluate evidence critically

For material external claims, prefer evidence that is:

- directly relevant;
- authoritative for the claim type;
- applicable to the project;
- applicable to the selected version or edition;
- sufficiently current;
- available at sufficient evidential depth;
- methodologically adequate where empirical evidence is involved.

Evaluate:

- scope;
- applicability;
- version;
- lifecycle state;
- recency;
- source authority;
- evidential depth;
- methodology;
- limitations;
- conflicting credible evidence.

Prefer primary and authoritative sources when they adequately answer the question.

Do not use blogs, tutorials, forum posts, generated content, or community consensus as primary authority when directly applicable primary evidence is available.

Secondary evidence may still be useful for:

- examples;
- implementation experience;
- identifying known failure modes;
- historical context;
- locating primary sources;
- identifying disputed interpretations.

When external verification is needed, search for evidence capable of contradicting or weakening the current position as well as evidence supporting it.

Do not conduct a confirmation-only search.

---

# 6. Respect evidential depth

Distinguish what the available source actually establishes.

## Metadata only

Metadata may establish:

- title;
- edition;
- publication date;
- lifecycle status;
- high-level scope.

It does not establish unavailable detailed clauses or requirements.

## Authoritative content available

When the applicable authoritative source is available, it may support:

- specific definitions;
- requirements;
- clauses;
- detailed semantics;
- conformance criteria.

Use it only within its actual scope.

## Secondary interpretation

Secondary material may support:

- learning;
- examples;
- comparison;
- implementation guidance;
- historical context.

It does not replace normative material where exact normative semantics or conformance matter.

Never invent inaccessible normative requirements.

Never claim conformance based only on metadata, abstracts, catalogue entries, or secondary interpretation.

---

# 7. Distinguish documentation quality dimensions

Evaluate documentation through four independent dimensions.

## A. Semantic correctness

Question:

> Does the document correctly represent accepted project intent and externally governed facts?

Look for:

- incorrect claims;
- contradictions;
- definition conflicts;
- incorrect standards interpretations;
- incorrect authority attribution;
- obsolete technical statements;
- unsupported certainty;
- target-state/implementation-state confusion.

Semantic correctness has priority over stylistic preference.

---

## B. Content adequacy

Question:

> Does the artifact contain the information necessary to fulfil its semantic responsibility and intended use?

Judge adequacy according to the artifact, not according to a universal document checklist.

Do not require irrelevant sections merely for completeness.

Do identify omissions that prevent the document from fulfilling its responsibility.

---

## C. Organization and usability

Question:

> Can the intended reader efficiently find, understand, and use the information?

Inspect:

- navigation;
- ordering;
- placement;
- cross-references;
- duplication;
- level of detail;
- reader context;
- separation of concerns.

Reader-oriented frameworks may inform presentation but must not redefine engineering semantic ownership.

---

## D. Editorial quality

Question:

> Is the material expressed clearly and consistently without weakening technical precision?

Use this precedence:

```text
project terminology and explicit conventions
        ↓
domain / standards terminology
        ↓
adopted editorial guidance
        ↓
general language conventions
```

Improve:

- clarity;
- grammar;
- sentence structure;
- terminology consistency;
- headings;
- lists;
- links;
- accessibility;
- scannability.

Do not alter technical meaning merely to improve style.

Preserve:

- normative strength;
- certainty;
- uncertainty;
- scope;
- qualification;
- controlled terminology.

In particular, do not weaken or strengthen terms such as:

```text
MUST
SHALL
required
should
recommended
may
assumed
unknown
```

unless the underlying project intent actually changes.

---

# 8. Candidate-defect discipline

Do not treat every apparent issue as a defect.

For each material issue:

```text
candidate issue
      ↓
identify artifact responsibility
      ↓
identify claim type
      ↓
identify applicable authority or criterion
      ↓
classify:
    confirmed defect
    acceptable variation
    unresolved issue
      ↓
apply smallest justified correction
```

Useful defect classes include:

- semantic;
- normative-expression;
- content;
- organization/usability;
- editorial.

If correcting an issue requires an engineering decision that the repository does not establish, do not invent the decision.

Record it as unresolved.

---

# 9. Critical review requirements

Test the documentation for:

- unsupported assumptions;
- ambiguity;
- contradiction;
- missing requirements;
- hidden dependencies;
- ignored realistic alternatives;
- unnecessary complexity;
- premature abstraction;
- incorrect standards interpretation;
- unclear boundaries;
- poorly defined interfaces;
- missing failure behavior;
- security consequences;
- operational consequences;
- quality consequences;
- implementation choices presented as semantic requirements;
- claims stronger than the available evidence;
- duplicated authority;
- terminology drift;
- obsolete references;
- internal contradictions between documents;
- inconsistencies between documented intent and verification criteria.

Do not manufacture criticism merely to make the review appear rigorous.

When a claim is well supported, retain it.

---

# 10. Classify conclusions

Where classification improves clarity, characterize findings as one of:

```text
established fact
external normative requirement
implementation-authority fact
accepted project requirement
project constraint
accepted project decision
evidence-supported recommendation
reasonable assumption
design preference
speculation
unresolved issue
incorrect claim
```

Do not present:

- a recommendation as a requirement;
- an implementation fact as intended architecture;
- a project choice as an external obligation;
- common practice as a normative rule;
- an assumption as an established fact;
- an unresolved claim as certain.

---

# 11. Review relationships across artifacts

Do not review documents only in isolation.

Check relevant relationships:

```text
stakeholder needs / external obligations
                 ↓
          requirements.md
                 ↕
          architecture.md
                 ↕
             design/
                 ↓
               src/
                 ↓
        verification evidence

             decisions/
                 ↕
      requirements ⇄ architecture ⇄ design
```

Look for:

- architecture that violates accepted requirements;
- designs that violate architecture;
- requirements that unintentionally prescribe implementation;
- architecture decisions duplicated as requirements;
- bounded design detail incorrectly promoted into system-wide architecture;
- ADRs whose resulting decision is absent from current architecture/design;
- obsolete ADRs presented as active intent;
- verification criteria that no longer match requirements;
- README summaries inconsistent with authoritative documents;
- external claims lacking appropriate authoritative support.

Do not assume every relationship requires explicit IDs or formal traceability.

Use proportional traceability.

---

# 12. Traceability policy

Use lightweight traceability where it materially improves reconstructability.

Possible mechanisms include:

- requirement IDs;
- document links;
- ADR references;
- design references;
- specification references;
- test references;
- verification references.

Do not introduce formal traceability matrices, databases, schemas, generators, or dedicated tooling unless actual project requirements such as scale, regulation, safety, auditability, or complexity justify them.

Traceability infrastructure is not inherently evidence of documentation quality.

---

# 13. Verification discipline

Verification follows the claim:

```text
claim
   ↓
verification criterion
   ↓
appropriate evidence
```

Potential evidence includes:

- unit tests;
- integration tests;
- system tests;
- acceptance tests;
- property-based tests;
- static analysis;
- architecture checks;
- schema validation;
- configuration validation;
- benchmarks;
- security analysis;
- deployment inspection;
- formal analysis;
- operational evidence;
- manual acceptance.

Do not insist that every architectural statement have a software test.

Do not leave mechanically verifiable claims purely in prose when a reliable automated check is practical and justified.

When reviewing documentation, identify missing verification where it materially weakens an important claim.

Do not implement unrelated verification infrastructure unless the task explicitly requires it.

---

# 14. Framework and standard use

Use standards and frameworks only within their legitimate scope.

Examples:

### ISO/IEC/IEEE 29148

Use for requirements-engineering concepts and requirements quality where applicable.

Do not treat it as a universal prose standard.

### ISO/IEC 25010

Use as quality vocabulary and a source of candidate concerns.

Do not automatically create requirements for every quality characteristic.

### ISO/IEC/IEEE 42010

Use as a conceptual reference for architecture descriptions where applicable.

Do not assume it prescribes this repository's document structure.

### arc42

Use selectively as practical architecture coverage guidance.

Do not mechanically instantiate every section.

### MADR

Use as an optional ADR representation.

The format does not establish decision correctness.

### Diátaxis

Use for reader-purpose and information organization where useful.

Do not replace engineering semantic categories with tutorial/how-to/reference/explanation categories.

### Editorial style guides

Use for expression only after project and domain terminology.

Do not let editorial guidance alter normative technical semantics.

### GitHub Copilot documentation

Treat current official GitHub documentation as implementation authority for GitHub Copilot feature behavior.

Verify current behavior when a claim depends on version, product surface, preview status, or feature support.

---

# 15. Simplicity requirement

Prefer the simplest documentation architecture that satisfies actual project needs.

Challenge every proposed addition:

```text
new document
new document category
new framework
new abstraction
new Skill
new custom agent
new prompt
new hook
new MCP integration
new generated-documentation system
new traceability mechanism
new evaluation mechanism
```

Ask:

1. What demonstrated problem does this solve?
2. Why is the existing structure insufficient?
3. What maintenance cost does it add?
4. What failure mode does it reduce?
5. Is that benefit material?
6. Is there a smaller solution?

Do not add structure for theoretical completeness.

Do not delete structure merely to make the repository smaller when the structure solves a demonstrated problem.

---

# 16. Editing rules

When mode is `review-and-fix`:

1. Inspect before editing.
2. Establish artifact responsibility and authority.
3. Correct confirmed defects directly.
4. Apply the smallest sufficient change.
5. Preserve valid project intent.
6. Preserve normative strength.
7. Preserve material uncertainty.
8. Preserve controlled terminology.
9. Remove unnecessary duplication where authority remains clear.
10. Improve cross-references where navigation materially benefits.
11. Correct stale or unsupported external claims when sufficient evidence exists.
12. Update `references.md` when a materially used external source should be registered.
13. Do not fabricate requirements, architecture, decisions, rationale, evidence, measurements, or external obligations.
14. Do not silently convert observed implementation into accepted intent.
15. Do not create new documents unless the need is demonstrated.
16. Do not change production source code unless the user explicitly includes implementation changes in the task.
17. Do not change accepted system semantics merely to make documentation agree with current code.
18. Do not perform broad stylistic rewrites of technically correct text unless they materially improve usability or clarity.
19. Keep small documents small.
20. Re-read affected documents after modification and check for new contradictions or broken references.

When mode is `review-only`:

- do not modify repository files;
- report findings and recommended corrections only.

---

# 17. Handling uncertainty

When evidence is insufficient:

Do not guess.

Do not fabricate a likely requirement or decision.

Do not silently choose among plausible interpretations.

Instead state:

- what is unresolved;
- why it is unresolved;
- which artifact or evidence is missing;
- what decision, authority, measurement, or stakeholder input would resolve it;
- whether the unresolved issue blocks a safe correction.

Use calibrated language.

Distinguish:

```text
certain
well supported
plausible
weakly supported
contested
unknown
```

---

# 18. External research behavior

Use external research only where it materially improves correctness.

Prioritize authoritative primary sources.

For current or lifecycle-sensitive claims, verify current information rather than relying on memory.

Examples include:

- active standards editions;
- superseded standards;
- preview APIs;
- current GitHub Copilot feature support;
- framework behavior;
- vendor products;
- regulations;
- evolving services.

When sources conflict:

1. identify the conflict;
2. compare authority and applicability;
3. determine whether one source supersedes another;
4. preserve the uncertainty if the conflict cannot be resolved.

Do not select the source merely because it agrees with the current document.

---

# 19. Scope protection

This task is a documentation-quality task.

Do not expand it into unrelated implementation refactoring.

Do not redesign the system merely because another design appears preferable.

If documentation accurately records an accepted but debatable design:

- preserve the accepted design;
- identify a material weakness only if supported;
- recommend a separate design decision where appropriate.

Do not rewrite accepted intent without evidence that the task authorizes changing that intent.

Likewise, do not preserve an incorrect external factual claim merely because it is currently documented.

Project authority governs project choices.

External authority governs externally defined facts.

---

# 20. Required completion procedure

Before completing the task, verify all of the following.

## Semantic ownership

- Each reviewed artifact fulfils its intended responsibility.
- No document has unnecessarily become a second authoritative source for another artifact's responsibility.
- Requirements, architecture, design, decisions, implementation, and verification remain conceptually distinct.

## Correctness

- Material technical claims are supported by the correct authority.
- No externally governed requirement has been invented.
- No implementation observation has silently become accepted intent.
- Normative strength and uncertainty are preserved.

## Consistency

- Relevant documentation is internally consistent.
- Cross-document terminology is coherent.
- README summaries do not contradict authoritative documentation.
- Relevant architecture, designs, and decisions agree or their discrepancies are explicitly identified.

## Evidence

- Material external claims have adequate support where evidence is available.
- Version-sensitive claims use applicable versions.
- Important limitations or unresolved conflicts are visible.
- `references.md` reflects materially used external sources where appropriate.

## Adequacy

- Important requirements, constraints, assumptions, boundaries, interfaces, failure behavior, and verification information are present where relevant.
- No irrelevant framework sections were added merely for completeness.

## Simplicity

- Unnecessary duplication has been removed or justified.
- No unnecessary documentation infrastructure has been introduced.
- The resulting structure remains understandable and maintainable.

## Editorial integrity

- Prose is clear and precise.
- Controlled terminology is consistent.
- Normative wording has not been weakened or strengthened accidentally.
- Formatting serves comprehension rather than decoration.

---

# 21. Required final report

After completing the repository review, provide a concise report with these sections.

## Scope reviewed

List the documents and relevant repository evidence actually inspected.

## Changes made

For `review-and-fix`, summarize substantive changes by file.

Do not enumerate trivial punctuation or formatting edits unless significant.

For `review-only`, state that no files were modified.

## Confirmed defects

List remaining confirmed defects, if any, with:

- file or artifact;
- defect class;
- issue;
- applicable authority or criterion;
- consequence;
- recommended correction.

Do not repeat defects already fully corrected unless useful for understanding major changes.

## Unresolved issues

For each unresolved issue state:

- what cannot currently be established;
- why;
- what evidence or decision is required;
- whether it blocks further correction.

## Evidence and authority

Identify material external authorities or repository evidence used to make substantive corrections or conclusions.

Do not list every file read.

## Verification

State what was checked after modification, for example:

- cross-document consistency;
- links;
- terminology;
- references;
- requirement/design relationships;
- available documentation validation;
- relevant tests or repository checks if applicable.

## Result

Conclude with one of:

```text
PASS
Documentation reviewed; no material unresolved quality defects remain
within the reviewed scope.

PASS WITH OPEN ISSUES
Documentation is materially sound, but explicitly identified issues
require information or decisions not currently available.

CHANGES REQUIRED
Material defects remain that can and should be corrected with the
available project evidence.
```

Do not assign an arbitrary numeric quality score unless explicitly requested.

---

# 22. Final governing rule

Throughout the task, optimize for this outcome:

> Maintain the smallest documentation system that makes project intent, significant constraints, external authority, engineering rationale, implementation state, documentation quality, and verification evidence sufficiently explicit for humans and agents to reason correctly about the system.

Correctness is more important than agreement.

Evidence is more important than confidence.

Semantic ownership is more important than document volume.

The simplest adequate structure is preferred over theoretical completeness.

If the repository does not provide enough evidence to make a correct engineering decision, expose the gap rather than inventing the answer.
