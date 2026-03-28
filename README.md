# symmetrical-garbanzo
mvp
# KPF Build Handoff

## Purpose

Build **KPF (Knowledge Product Factory)** as a **CLI-driven, browser-enabled, multi-agent runtime** that researches a niche, structures evidence, scores opportunities, designs a knowledge product, drafts launch assets, critiques the result, validates support and completeness, and exports artifacts.

This is **not** a chatbot, **not** a one-shot script, and **not** a UI-first product.

The system must be:
- local, inspectable, and resumable
- workspace-based
- SQLite-backed
- schema-validated
- stage-driven
- prompt-driven at the agent level
- deterministic for orchestration, scoring, and validation

## Primary Product Goal

Build a CLI app with these commands:

```bash
kpf run "<niche or problem>"
kpf inspect <run_id>
kpf validate <run_id>
kpf resume <run_id>
kpf export <run_id> --format markdown
```

Examples:

```bash
kpf run "IEP/504 parent advocacy"
kpf run "Seattle home renovation planning"
kpf run "small landlord tenant screening workflow"
```

A successful run must:
1. initialize a workspace
2. persist run state to SQLite
3. research the web through agents
4. extract structured evidence
5. verify claims
6. score opportunities
7. generate a product blueprint
8. generate a draft artifact
9. generate packaging assets
10. run adversarial critique
11. validate pass/fail
12. export human-readable artifacts

## Non-Negotiable Architecture Rules

1. Every structured output must have a Pydantic schema.
2. Every stage must write artifacts to disk.
3. Every important event must be logged to JSONL.
4. No stage may proceed if its gate fails.
5. Deterministic logic must live in Python, not inside prompts.
6. Prompts must live in separate `.md` files, not inline in code.
7. All thresholds must be configurable.
8. All paths must be resolved through workspace helpers.
9. All structured LLM outputs must be validated before acceptance.
10. No hidden state outside the workspace files and SQLite database.
11. The validator must be able to fail the run.
12. Build bottom-up. Do not start with fancy agent prose.
13. Do not build a UI.
14. Do not optimize for concurrency first.
15. Favor explicitness, traceability, and resumability over cleverness.
16. Keep the code runnable after every milestone.

## Target Repository Structure

```text
kpf/
  README.md
  pyproject.toml
  .env.example

  /kpf
    __init__.py

    /cli
      main.py
      run.py
      inspect.py
      resume.py
      validate.py
      export.py

    /config
      settings.py
      loader.py
      defaults.yaml

    /core
      runner.py
      orchestrator.py
      stage_manager.py
      task_graph.py
      workspace.py
      logging.py
      errors.py
      ids.py
      clock.py

    /db
      models.py
      session.py
      init_db.py
      queries.py

    /schemas
      source.py
      quote.py
      claim.py
      competitor.py
      opportunity.py
      blueprint.py
      validation.py
      task.py
      run_state.py
      artifact.py
      agent_result.py

    /agents
      base.py
      orchestrator_agent.py
      niche_research_agent.py
      pain_scout_agent.py
      spend_scout_agent.py
      competitor_analyst_agent.py
      authority_research_agent.py
      extractor_agent.py
      verifier_agent.py
      opportunity_scorer_agent.py
      product_architect_agent.py
      draft_writer_agent.py
      packaging_agent.py
      adversarial_reviewer_agent.py
      final_validator_agent.py

    /prompts
      orchestrator.md
      niche_research.md
      pain_scout.md
      spend_scout.md
      competitor_analyst.md
      authority_research.md
      extractor.md
      verifier.md
      opportunity_scorer.md
      product_architect.md
      draft_writer.md
      packaging.md
      adversarial_reviewer.md
      final_validator.md

    /llm
      base.py
      router.py
      client.py
      structured.py

    /retrieval
      search.py
      fetch.py
      html_extract.py
      pdf_extract.py
      snapshot.py
      dedupe.py
      normalize.py
      metadata.py

    /scoring
      rubric.py
      calculators.py
      thresholds.py

    /validation
      artifact_checks.py
      evidence_checks.py
      claim_checks.py
      gating.py

    /render
      markdown.py
      reports.py
      exports.py

    /templates
      opportunity_report.md.j2
      product_blueprint.md.j2
      sales_page.md.j2
      critique.md.j2
      validation_report.md.j2

    /utils
      files.py
      jsonl.py
      text.py
      dates.py
      urls.py

  /tests
    test_config.py
    test_workspace.py
    test_schemas.py
    test_db.py
    test_task_graph.py
    test_retrieval.py
    test_agents_smoke.py
    test_scoring.py
    test_validation.py

  /examples
    sample_run_config.yaml
    sample_workspace/
```

## Technical Stack

Use:
- Python 3.12+
- `typer`
- `pydantic`
- `sqlmodel` or `sqlalchemy + sqlite3`
- `jinja2`
- `httpx`
- `beautifulsoup4`
- `readability-lxml`
- `pypdf` or `pymupdf`
- `playwright` for browser fallback and screenshots
- `tenacity`
- `rich`
- `orjson`

Keep the LLM layer provider-agnostic.

Required abstraction methods:
- `generate_structured(...)`
- `generate_text(...)`
- `classify(...)`

## Workspace Requirements

Each run must create a workspace similar to:

```text
/workspaces/run_YYYYMMDD_NNN/
  config.yaml
  /cache
    /html
    /pdf
    /screenshots
  /artifacts
    niche_brief.json
    research_plan.json
    pain_signals.jsonl
    spend_signals.jsonl
    competitors.jsonl
    authority_sources.jsonl
    quotes.jsonl
    claims.jsonl
    opportunities.jsonl
    scorecard.json
    product_blueprint.json
    product_outline.md
    draft.md
    sales_page.md
    gumroad_listing.md
    faq.md
    email_sequence.md
    critique.md
    red_flags.json
    validation_report.json
  /logs
    run.jsonl
    agent_calls.jsonl
  /state
    run_state.json
    task_graph.json
    decisions.json
```

All artifact paths must be produced through workspace helper functions.

## Stage Model

Use these stages exactly:

```text
INIT
NICHE_DEFINITION
EVIDENCE_GATHERING
EXTRACTION
VERIFICATION
SCORING
PRODUCT_ARCHITECTURE
DRAFTING
PACKAGING
CRITIQUE
VALIDATION
COMPLETE
FAILED
```

Valid transitions:
- INIT -> NICHE_DEFINITION
- NICHE_DEFINITION -> EVIDENCE_GATHERING
- EVIDENCE_GATHERING -> EXTRACTION
- EXTRACTION -> VERIFICATION
- VERIFICATION -> SCORING
- SCORING -> PRODUCT_ARCHITECTURE
- PRODUCT_ARCHITECTURE -> DRAFTING
- DRAFTING -> PACKAGING
- PACKAGING -> CRITIQUE
- CRITIQUE -> VALIDATION
- VALIDATION -> COMPLETE
- any stage -> FAILED

No silent jumps. No hidden transitions.

## Required Agents

All agents must share a base interface with:
- `name()`
- `run(context) -> AgentResult`
- `load_prompt()`
- `validate_output()`

### Agent roster

1. **OrchestratorAgent** — breaks objective into tasks, assigns specialists, enforces progression, stops weak runs
2. **NicheResearchAgent** — outputs `niche_brief.json`, `research_plan.json`
3. **PainScoutAgent** — outputs `pain_signals.jsonl`
4. **SpendScoutAgent** — outputs `spend_signals.jsonl`
5. **CompetitorAnalystAgent** — outputs `competitors.jsonl`, `competitor_gap_report.json`
6. **AuthorityResearchAgent** — outputs `authority_sources.jsonl`, `facts.jsonl`
7. **ExtractorAgent** — outputs `quotes.jsonl`, `claims.jsonl`, `entities.jsonl`
8. **VerifierAgent** — outputs `verification_report.json` and claim status updates
9. **OpportunityScorerAgent** — outputs `opportunities.jsonl`, `scorecard.json`
10. **ProductArchitectAgent** — outputs `product_blueprint.json`, `product_outline.md`
11. **DraftWriterAgent** — outputs `draft.md`
12. **PackagingAgent** — outputs `sales_page.md`, `gumroad_listing.md`, `faq.md`, `email_sequence.md`
13. **AdversarialReviewerAgent** — outputs `critique.md`, `red_flags.json`
14. **FinalValidatorAgent** — outputs `validation_report.json`

## Agent Interface Requirements

### AgentContext must include
- run_id
- objective
- current_stage
- workspace paths
- config
- db/session handle
- tool registry
- llm client
- relevant source IDs
- relevant claim IDs
- thresholds/settings

### AgentResult must include
- status
- summary
- warnings
- errors
- produced_artifacts
- produced_records
- metrics

All structured agent outputs must validate against schemas before acceptance.

## Prompt Files to Create

Create separate `.md` prompt files for each agent.

### Prompt intent summary
- **Orchestrator**: coordinate stages and tasks, do not write final product content, enforce gates, prefer failed run over misleading run
- **Niche Research**: define audience segments, pain areas, search plan, unknowns, do not conclude viability yet
- **Pain Scout**: find repeated, concrete first-person pain; capture source, context, date, excerpt, category, severity, recurrence
- **Spend Scout**: find direct willingness-to-pay signals; capture product/service, price, payer, desired outcome, dissatisfaction, source excerpt
- **Competitor Analyst**: map offers, pricing, positioning, strengths, weaknesses, gaps
- **Authority Research**: gather official and primary sources for factual and procedural support
- **Extractor**: turn raw material into traceable quotes, claims, competitor details, process steps, price signals, objections, audience descriptors
- **Verifier**: confirm source support, quote accuracy, freshness, credibility, corroboration; assign verified, weak, contradicted, stale, unsupported
- **Opportunity Scorer**: cluster evidence into opportunities and score with explicit evidence refs
- **Product Architect**: create a tightly scoped product; define audience, before-state, after-state, format, modules, bonuses, exclusions, differentiation
- **Draft Writer**: write only from approved blueprint and verified claims; no filler, no unsupported examples
- **Packaging**: produce title, subtitle, positioning, sales page, listing copy, FAQ, email sequence; no exaggeration
- **Adversarial Reviewer**: attack unsupported demand, vague promises, weak differentiation, shaky distribution, generic content, legal/factual risk
- **Final Validator**: determine pass/fail; enforce artifact presence, support thresholds, coherent scope, and launch asset completeness

## Database and Schema Requirements

Use SQLite and define tables/models for at least:
- runs
- tasks
- sources
- quotes
- claims
- competitors
- opportunities
- artifacts
- validations
- agent_outputs

Also create matching Pydantic schemas in `/schemas`.

At minimum define these schema types:
- Source
- Quote
- Claim
- Competitor
- Opportunity
- ProductBlueprint
- ValidationReport
- TaskRecord
- RunState
- ArtifactRecord
- AgentResult

Fields must support:
- IDs
- timestamps
- statuses
- source traceability
- artifact traceability
- confidence, freshness, credibility where relevant

## Validation Gates

Implement deterministic gate checks in Python.

### Gate 1 — Evidence sufficiency
Minimum:
- 15 total sources
- 5 direct pain quotes
- 3 spend signals
- 3 competitor entries
- 2 authority sources for factual or procedural niches

### Gate 2 — Claim support
- no major claim unsupported
- legal or procedural claims require authority support
- stale claims must be flagged or excluded

### Gate 3 — Opportunity viability
Minimum example thresholds:
- total score >= 38/60
- pain >= 7
- spend >= 5
- solo feasibility >= 7

### Gate 4 — Blueprint coherence
- audience is specific
- before/after outcome is clear
- modules align to buyer outcome
- exclusions are defined

### Gate 5 — Shipping completeness
Required:
- product blueprint
- draft
- sales page
- FAQ
- critique
- validation report

No stage should proceed if its gate fails.

## Scoring Requirements

Implement deterministic scoring code, not prompt-only scoring.

Dimensions:
- pain severity
- pain frequency
- spend evidence
- distribution accessibility
- solo feasibility
- differentiation
- trust burden
- freshness dependency

Example weights:
- pain severity x 0.20
- pain frequency x 0.15
- spend evidence x 0.20
- distribution x 0.15
- solo feasibility x 0.15
- differentiation x 0.10
- trust burden x 0.03
- freshness dependency x 0.02

Each score should be explainable with evidence references.

## Retrieval Layer Requirements

Implement:
- search abstraction
- page fetcher
- HTML extraction
- PDF extraction
- snapshot caching
- source normalization
- metadata inference
- dedupe

Normalize and persist:
- URL
- title
- source type
- domain
- published and accessed dates when possible
- local snapshot path
- credibility class

Keep retrieval simple but solid for v1.

## Milestone Plan

### Milestone 1 — Foundations
Implement:
- repo skeleton
- `pyproject.toml` and dependencies
- CLI entrypoint
- config settings and loader
- workspace manager
- logging scaffold
- ids and clock helpers

Acceptance criteria:
- `kpf --help` works
- `kpf run "test niche"` creates a workspace and initial files
- run state file exists
- basic logs file exists

### Milestone 2 — Persistence and orchestration rails
Implement:
- SQLite models
- DB session/init/query helpers
- Pydantic schemas
- stage manager
- task graph
- runner scaffold
- orchestrator scaffold

Acceptance criteria:
- run is persisted to DB
- tasks can be created, updated, and queried
- stage transitions are explicit
- invalid transitions fail cleanly

### Milestone 3 — Retrieval
Implement:
- search abstraction
- fetcher
- HTML extraction
- PDF extraction
- source normalization
- snapshot caching
- dedupe
- source registration

Acceptance criteria:
- a URL can be fetched and stored
- extracted text can be saved
- source metadata persists
- duplicate sources are detected

### Milestone 4 — Agent framework and research pipeline
Implement:
- BaseAgent
- AgentContext
- AgentResult
- prompt loader
- LLM abstraction
- niche research agent
- pain scout
- spend scout
- competitor analyst
- authority researcher
- extractor
- verifier

Acceptance criteria:
- at least one dummy or mocked run can create sources, quotes, and claims
- agent outputs validate against schemas
- verification updates claim statuses

### Milestone 5 — Scoring and product design
Implement:
- scoring rubric, calculators, thresholds
- opportunity scorer
- product architect

Acceptance criteria:
- opportunities can be ranked reproducibly
- threshold checks work
- blueprint artifact is generated only after a valid opportunity exists

### Milestone 6 — Drafting and packaging
Implement:
- draft writer
- packaging agent

Acceptance criteria:
- `draft.md` is generated from blueprint and verified claims
- sales assets are generated and saved

### Milestone 7 — Critique, validation, and export
Implement:
- adversarial reviewer
- final validator
- validate command
- inspect command
- resume command
- export command
- markdown report rendering

Acceptance criteria:
- weak runs can fail
- strong runs can pass
- inspect shows status clearly
- export produces readable report output

### Milestone 8 — Tests, README, and polish
Implement:
- unit tests for config, workspace, schemas, db, task graph, scoring, validation
- smoke tests for mocked end-to-end run
- README
- examples

Acceptance criteria:
- core tests pass
- at least one mocked end-to-end run passes
- README documents setup and workflow

## Completion Report Format

At the end of each milestone, the implementation agent must stop and output exactly this structure:

```text
MILESTONE COMPLETION REPORT
Milestone: <name>
Status: COMPLETE | PARTIAL | BLOCKED

Implemented:
- <bullet list>

Changed Files:
- <path>
- <path>

Acceptance Criteria Check:
- <criterion>: PASS | FAIL
- <criterion>: PASS | FAIL

Tests Run:
- <test or command>: PASS | FAIL
- <test or command>: PASS | FAIL

Known Issues:
- <issue>
- <issue>

Next Recommended Milestone:
- <next milestone name>
```

Do not claim COMPLETE unless all acceptance criteria are actually satisfied.

## Testing Requirements

Add tests for:
- config loading
- workspace creation
- schema validation
- DB initialization and queries
- task graph transitions
- scoring math
- validation gates
- retrieval smoke behavior
- one mocked end-to-end run

Mock expensive or unstable pieces. Do not require live web and live model calls for all tests.

## Definition of Done

The repo is done enough for v1 when:
- `kpf --help` works
- `kpf run "<niche>"` creates a run, workspace, db records, and stage state
- sources can be fetched and stored
- structured evidence can be created
- at least one opportunity can be scored
- a blueprint can be generated
- draft and packaging artifacts can be produced
- critique can be produced
- validation can pass or fail explicitly
- inspect and export work
- at least one mocked end-to-end test passes

## Direct Implementation Instruction

Build the repo from the bottom up.

Execution order:
1. create the repo skeleton and package structure
2. implement config, workspace, logging, ids, and clock
3. implement SQLite models, DB init, and query helpers
4. implement schemas for all structured records
5. implement the stage manager and task graph
6. implement the runner and orchestrator scaffolding
7. implement retrieval: search abstraction, fetcher, HTML extraction, PDF extraction, metadata normalization, snapshot caching
8. implement the base agent framework and prompt loading
9. implement research agents: niche research, pain scout, spend scout, competitor analyst, authority research, extractor, verifier
10. implement scoring and thresholds
11. implement opportunity scorer and product architect
12. implement draft writer and packaging agent
13. implement adversarial reviewer and final validator
14. implement inspect, validate, resume, and export commands
15. add tests for each foundational subsystem and a smoke test for a mocked end-to-end run

Rules:
- do not build a UI
- do not skip schema validation
- do not hide deterministic logic inside prompts
- do not hardcode file paths
- do not use a monolithic script
- get each layer working before moving to the next
- keep the repo runnable after every milestone
- stop at each milestone and produce the completion report

## Final Note to the Build Agent

The goal is not to imitate intelligence. The goal is to build a reliable production line for knowledge product discovery and packaging.

Optimize for:
- explicitness
- traceability
- resumability
- validation
- auditability
- modular growth

A weaker but inspectable system is better than a more impressive but opaque one.
