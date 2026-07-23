# Agentic Coding Development Toolkit

> **Thesis:** build **AI developer workflows**—the system that builds the system—instead of treating one feedback loop as the whole engineering discipline.

The source argues that reliable agentic engineering combines three actors at the right place and time: **engineers** supply intent and judgment, **agents** supply adaptive compute, and **deterministic code** supplies fast, repeatable control. The integrated map below follows that idea from a prompt-and-review primitive through validation loops, isolated parallel execution, organizational intake, specialized incident response, and a routed software factory.

```mermaid
flowchart TB
    im_meta_human(["Engineer designs the agentic layer"])
    im_intake_code{"Ticket or prompt intake"}
    im_router_agent["Workflow Router Agent"]
    im_plan_agent["Planner Agent"]
    im_build_agent["Build Agent"]
    im_validate_code{"Lint, format, test, CI/CD"}
    im_review_human(["Engineer validates outcomes"])
    im_ship_code{"Merge and ship"}
    im_improve_human(["Engineer improves the factory"])

    im_meta_human --> im_intake_code --> im_router_agent
    im_router_agent -->|feature, bug, chore| im_plan_agent
    im_plan_agent --> im_build_agent --> im_validate_code
    im_validate_code -->|fail with context| im_build_agent
    im_validate_code -->|pass| im_review_human
    im_review_human -->|reject| im_plan_agent
    im_review_human -->|approve| im_ship_code --> im_improve_human
    im_improve_human -->|build the system that builds the system| im_meta_human

    subgraph im_parallel_group["Parallel isolated execution"]
        direction LR
        im_sandbox_a_agent["Sandbox Agent A"]
        im_sandbox_b_agent["Sandbox Agent B"]
        im_sandbox_c_agent["Sandbox Agent C"]
    end

    im_router_agent -->|high-value or urgent work| im_sandbox_a_agent
    im_router_agent -->|scale compute| im_sandbox_b_agent
    im_router_agent -->|race alternatives| im_sandbox_c_agent
    im_sandbox_a_agent --> im_review_human
    im_sandbox_b_agent --> im_review_human
    im_sandbox_c_agent --> im_review_human
```

## Visual legend

- **Humans — rounded nodes:** `(["Engineer Review"])`
- **Agents — rectangles:** `["Build Agent"]`
- **Deterministic code and conditions — diamonds:** `{"Lint Code"}`
- **Worktrees and sandboxes — labeled `subgraph` containers**
- **Control and feedback — labeled edges:** `-->|pass|`, `-->|fail|`, `-->|approve|`, and `-->|reject|`
- Neutral conceptual labels may use a separately styled rectangle, but every operational node follows the shape language above.

## Sources and timestamp method

- [Source video: “It’s Time To Talk About Loop Engineering”](https://www.youtube.com/watch?v=VQy50fuxI34)
- [Timestamped transcript](./VQy50fuxI34_transcript.txt)

The supplied PNGs were cropped captures and did not show player controls. Their filenames are therefore listed only as **capture filenames**, not video timestamps. Each **representative video position** below is the nearest frame match recovered from source-video pixels and cursor placement, then checked against the adjacent transcript range. The PNG files are not included in this repository.

## Phase 1 — Actors of value creation

### S01 — Engineers, agents, and code

- **Capture filename:** `截圖 2026-07-23 下午3.37.40.png`
- **Frame-matched representative video position:** **03:51**
- **Supporting transcript range:** **03:37–04:44**
- **Conceptual takeaway:** Agentic engineering is the deliberate composition of engineers, agents, and deterministic code. Code is the most predictable and least expensive actor; agents add adaptive compute; engineers supply intent and judgment.

```mermaid
flowchart TB
    s01_concept["Actors of value creation"]
    s01_engineer_human(["Engineers"])
    s01_agents_agent["Agents"]
    s01_code_code{"Code"}

    s01_concept --> s01_engineer_human
    s01_concept --> s01_agents_agent
    s01_concept --> s01_code_code
```

## Phase 2 — Progressive workflow ladder

### S02 — The primitive human-model-human workflow

- **Capture filename:** `截圖 2026-07-23 下午3.38.05.png`
- **Frame-matched representative video position:** **05:03**
- **Supporting transcript range:** **04:50–05:03**
- **Conceptual takeaway:** Every later workflow grows from a simple primitive: an engineer supplies intent, a model performs work, and an engineer reviews the result.

```mermaid
flowchart LR
    s02_prompt_human(["Engineer Prompt"])
    s02_llm_agent["LLM"]
    s02_review_human(["Engineer Review"])

    s02_prompt_human --> s02_llm_agent --> s02_review_human
```

### S03 — The first deterministic validation loop

- **Capture filename:** `截圖 2026-07-23 下午3.38.22.png`
- **Frame-matched representative video position:** **05:56**
- **Supporting transcript range:** **05:20–05:56**
- **Conceptual takeaway:** Put deterministic linting outside the agent. Pass its failure context back into the same build workflow; only a pass reaches human review.

```mermaid
flowchart LR
    s03_prompt_human(["Engineer Prompt"])
    s03_build_agent["Build Agent"]
    s03_lint_code{"Lint Code"}
    s03_review_human(["Engineer Review"])

    s03_prompt_human --> s03_build_agent --> s03_lint_code
    s03_lint_code -->|fail| s03_build_agent
    s03_lint_code -->|pass| s03_review_human
```

### S04 — Layer linting and formatting

- **Capture filename:** `截圖 2026-07-23 下午3.38.29.png`
- **Frame-matched representative video position:** **06:14**
- **Supporting transcript range:** **05:59–06:48**
- **Conceptual takeaway:** Add deterministic checks incrementally. Lint and format failures both return structured context to the build agent; human attention remains at the boundary.

```mermaid
flowchart LR
    s04_prompt_human(["Engineer Prompt"])
    s04_build_agent["Build Agent"]
    s04_lint_code{"Lint Code"}
    s04_format_code{"Format Code"}
    s04_review_human(["Engineer Review"])

    s04_prompt_human --> s04_build_agent --> s04_lint_code
    s04_lint_code -->|fail| s04_build_agent
    s04_lint_code -->|pass| s04_format_code
    s04_format_code -->|fail| s04_build_agent
    s04_format_code -->|pass| s04_review_human
```

### S05 — Complete deterministic validation stack

- **Capture filename:** `截圖 2026-07-23 下午3.38.34.png`
- **Frame-matched representative video position:** **07:13**
- **Supporting transcript range:** **06:50–07:26**
- **Conceptual takeaway:** Lint, formatting, and tests form a repeatable validation pipeline. Every failure returns to Build; the engineer appears at planning and final validation rather than every internal step.

```mermaid
flowchart LR
    s05_prompt_human(["Engineer Prompt"])
    s05_build_agent["Build Agent"]
    s05_lint_code{"Lint Code"}
    s05_format_code{"Format Code"}
    s05_test_code{"Test Code"}
    s05_review_human(["Engineer Review"])

    s05_prompt_human --> s05_build_agent --> s05_lint_code
    s05_lint_code -->|fail| s05_build_agent
    s05_lint_code -->|pass| s05_format_code
    s05_format_code -->|fail| s05_build_agent
    s05_format_code -->|pass| s05_test_code
    s05_test_code -->|fail| s05_build_agent
    s05_test_code -->|pass| s05_review_human
```

### S06 — Delegate validation to a test agent

- **Capture filename:** `截圖 2026-07-23 下午3.38.45.png`
- **Frame-matched representative video position:** **08:16**
- **Supporting transcript range:** **07:40–08:22**
- **Conceptual takeaway:** A test agent can orchestrate validation and return failures to Build. Review remains a human gate, and rejection also re-enters Build before shipping.

```mermaid
flowchart LR
    s06_prompt_human(["Engineer Prompt"])
    s06_build_agent["Build Agent"]
    s06_test_agent["Test Agent"]
    s06_review_human(["Engineer Review"])
    s06_ship_human(["Ship"])

    s06_prompt_human --> s06_build_agent --> s06_test_agent
    s06_test_agent -->|fail: loop back| s06_build_agent
    s06_test_agent -->|pass| s06_review_human
    s06_review_human -->|fail| s06_build_agent
    s06_review_human -->|pass| s06_ship_human
```

### S07 — Separate planning, building, and testing

- **Capture filename:** `截圖 2026-07-23 下午3.38.52.png`
- **Frame-matched representative video position:** **08:29**
- **Supporting transcript range:** **08:23–09:07**
- **Conceptual takeaway:** The familiar SDLC becomes an AI developer workflow: plan, build, test, review, and ship. Separating agent contexts makes each responsibility inspectable and replaceable.

```mermaid
flowchart LR
    s07_prompt_human(["Engineer Prompt"])
    s07_plan_agent["Planner Agent"]
    s07_build_agent["Build Agent"]
    s07_test_agent["Test Agent"]
    s07_review_human(["Engineer Review"])
    s07_ship_human(["Ship"])

    s07_prompt_human --> s07_plan_agent
    s07_plan_agent -->|plan review| s07_prompt_human
    s07_plan_agent --> s07_build_agent --> s07_test_agent
    s07_test_agent -->|fail| s07_build_agent
    s07_test_agent -->|pass| s07_review_human
    s07_review_human -->|fail| s07_plan_agent
    s07_review_human -->|pass| s07_ship_human
```

## Phase 3 — Parallel isolation

### S08 — Parallel worktree workflows

- **Capture filename:** `截圖 2026-07-23 下午3.38.58.png`
- **Frame-matched representative video position:** **09:11**
- **Supporting transcript range:** **09:08–10:37**
- **Conceptual takeaway:** Deterministic code creates isolated worktrees so several planner-build-test-review pipelines can execute in parallel without colliding, then converge at merge.

```mermaid
flowchart LR
    s08_prompt_human(["Engineer Prompt"])
    s08_create_code{"Build Worktree Code"}
    s08_merge_human(["Merge"])
    s08_ship_human(["Ship"])

    s08_prompt_human --> s08_create_code

    subgraph s08_worktree_1["Worktree 1"]
        direction LR
        s08_w1_plan_agent["Planner Agent"] --> s08_w1_build_agent["Build Agent"] --> s08_w1_test_agent["Test Agent"]
        s08_w1_test_agent -->|fail| s08_w1_build_agent
        s08_w1_test_agent -->|pass| s08_w1_review_human(["Engineer Review"])
        s08_w1_review_human -->|fail| s08_w1_plan_agent
    end

    subgraph s08_worktree_2["Worktree 2"]
        direction LR
        s08_w2_plan_agent["Planner Agent"] --> s08_w2_build_agent["Build Agent"] --> s08_w2_test_agent["Test Agent"]
        s08_w2_test_agent -->|fail| s08_w2_build_agent
        s08_w2_test_agent -->|pass| s08_w2_review_human(["Engineer Review"])
        s08_w2_review_human -->|fail| s08_w2_plan_agent
    end

    subgraph s08_worktree_3["Worktree 3"]
        direction LR
        s08_w3_plan_agent["Planner Agent"] --> s08_w3_build_agent["Build Agent"] --> s08_w3_test_agent["Test Agent"]
        s08_w3_test_agent -->|fail| s08_w3_build_agent
        s08_w3_test_agent -->|pass| s08_w3_review_human(["Engineer Review"])
        s08_w3_review_human -->|fail| s08_w3_plan_agent
    end

    s08_create_code --> s08_w1_plan_agent
    s08_create_code --> s08_w2_plan_agent
    s08_create_code --> s08_w3_plan_agent
    s08_w1_review_human -->|pass| s08_merge_human
    s08_w2_review_human -->|pass| s08_merge_human
    s08_w3_review_human -->|pass| s08_merge_human
    s08_merge_human --> s08_ship_human
```

### S09 — Upgrade worktrees to agent sandboxes

- **Capture filename:** `截圖 2026-07-23 下午3.39.14.png`
- **Frame-matched representative video position:** **11:54**
- **Supporting transcript range:** **10:41–11:58**
- **Conceptual takeaway:** Give each branch a complete computer-like sandbox. Full isolation lets agents run applications and tests while engineers can enter the environment to inspect results before merge.

```mermaid
flowchart LR
    s09_prompt_human(["Engineer Prompt"])
    s09_create_code{"Build Agent Sandbox Code"}
    s09_merge_human(["Merge"])
    s09_ship_human(["Ship"])

    s09_prompt_human --> s09_create_code

    subgraph s09_sandbox_1["Agent Sandbox 1"]
        direction LR
        s09_sb1_plan_agent["Planner Agent"] --> s09_sb1_build_agent["Build Agent"] --> s09_sb1_test_agent["Test Agent"]
        s09_sb1_test_agent -->|fail| s09_sb1_build_agent
        s09_sb1_test_agent -->|pass| s09_sb1_review_human(["Engineer Review"])
        s09_sb1_review_human -->|fail| s09_sb1_plan_agent
    end

    subgraph s09_sandbox_2["Agent Sandbox 2"]
        direction LR
        s09_sb2_plan_agent["Planner Agent"] --> s09_sb2_build_agent["Build Agent"] --> s09_sb2_test_agent["Test Agent"]
        s09_sb2_test_agent -->|fail| s09_sb2_build_agent
        s09_sb2_test_agent -->|pass| s09_sb2_review_human(["Engineer Review"])
        s09_sb2_review_human -->|fail| s09_sb2_plan_agent
    end

    subgraph s09_sandbox_3["Agent Sandbox 3"]
        direction LR
        s09_sb3_plan_agent["Planner Agent"] --> s09_sb3_build_agent["Build Agent"] --> s09_sb3_test_agent["Test Agent"]
        s09_sb3_test_agent -->|fail| s09_sb3_build_agent
        s09_sb3_test_agent -->|pass| s09_sb3_review_human(["Engineer Review"])
        s09_sb3_review_human -->|fail| s09_sb3_plan_agent
    end

    s09_create_code --> s09_sb1_plan_agent
    s09_create_code --> s09_sb2_plan_agent
    s09_create_code --> s09_sb3_plan_agent
    s09_sb1_review_human -->|pass| s09_merge_human
    s09_sb2_review_human -->|pass| s09_merge_human
    s09_sb3_review_human -->|pass| s09_merge_human
    s09_merge_human --> s09_ship_human
```

## Phase 4 — Organizational intake and full pipeline

### S10 — Turn organizational demand into planning context

- **Capture filename:** `截圖 2026-07-23 下午3.39.24.png`
- **Frame-matched representative video position:** **12:23**
- **Supporting transcript range:** **12:02–14:07**
- **Conceptual takeaway:** Support, product, and engineering feed one ticket system. A normal path uses an engineer to translate the ticket; advanced teams can route well-formed tickets directly into planning, scouting, and plan generation.

```mermaid
flowchart LR
    s10_support_human(["Support"])
    s10_product_human(["Product"])
    s10_engineer_human(["Engineer"])
    s10_ticket_code{"Kanban Ticket"}
    s10_prompt_human(["Engineer Prompt"])
    s10_planning_code{"Status: Planning"}
    s10_scout_agent["Scout Agent"]
    s10_plan_agent["Plan Agent"]

    s10_support_human --> s10_ticket_code
    s10_product_human --> s10_ticket_code
    s10_engineer_human --> s10_ticket_code
    s10_ticket_code --> s10_prompt_human --> s10_planning_code
    s10_ticket_code -->|advanced teams| s10_planning_code
    s10_planning_code --> s10_scout_agent --> s10_plan_agent
```

### S11 — Full ticket-to-production workflow

- **Capture filename:** `截圖 2026-07-23 下午3.39.32.png`
- **Frame-matched representative video position:** **13:03**
- **Supporting transcript range:** **13:03–15:15**
- **Conceptual takeaway:** Ticket status changes are deterministic control nodes around specialized Scout, Plan, Build, and Test agents. Test and CI/CD failures return to Build; successful delivery still passes through engineering review.

```mermaid
flowchart LR
    s11_support_human(["Support"])
    s11_product_human(["Product"])
    s11_engineer_human(["Engineer"])
    s11_ticket_code{"Kanban Ticket"}
    s11_prompt_human(["Engineer Prompt"])

    subgraph s11_sandbox_group["Sandbox"]
        direction LR
        s11_planning_code{"Status: Planning"}
        s11_scout_agent["Scout Agent"]
        s11_plan_agent["Plan Agent"]
        s11_building_code{"Status: Building"}
        s11_build_agent["Build Agent"]
        s11_testing_code{"Status: Testing"}
        s11_test_agent["Test Agent"]
        s11_cicd_code{"CI/CD"}

        s11_planning_code --> s11_scout_agent --> s11_plan_agent --> s11_building_code
        s11_building_code --> s11_build_agent --> s11_testing_code --> s11_test_agent
        s11_test_agent -->|fail| s11_build_agent
        s11_test_agent -->|pass| s11_cicd_code
        s11_cicd_code -->|fail| s11_build_agent
    end

    s11_review_human(["Engineer Review"])
    s11_ship_human(["Ship"])

    s11_support_human --> s11_ticket_code
    s11_product_human --> s11_ticket_code
    s11_engineer_human --> s11_ticket_code
    s11_ticket_code --> s11_prompt_human --> s11_planning_code
    s11_ticket_code -->|advanced teams| s11_planning_code
    s11_cicd_code -->|pass| s11_review_human
    s11_review_human -->|pass| s11_ship_human
```

## Phase 5 — Hotfix race

### S12 — Production-crash response with racing sandboxes

- **Capture filename:** `截圖 2026-07-23 下午3.39.54.png`
- **Frame-matched representative video position:** **17:46**
- **Supporting transcript range:** **15:21–17:46**
- **Conceptual takeaway:** A specialized hotfix agent optimizes for restoration speed. A human approval gate protects the high-risk transition, after which several isolated sandboxes race; the first validated result can ship.

```mermaid
flowchart LR
    s12_crash_human(["Support: Production Crash"])
    s12_prompt_human(["Engineer Prompt"])
    s12_scout_agent["Scout Agent"]
    s12_hotfix_agent["Hot Fix Agent"]
    s12_gate_human(["Approve or Reject"])
    s12_create_code{"Build Sandboxes"}
    s12_review_human(["Engineer Review"])
    s12_ship_human(["Ship"])

    s12_crash_human --> s12_prompt_human --> s12_scout_agent --> s12_hotfix_agent --> s12_gate_human
    s12_gate_human -->|reject| s12_hotfix_agent
    s12_gate_human -->|approve| s12_create_code

    subgraph s12_sandbox_1["Sandbox 1"]
        direction LR
        s12_sb1_build_agent["Build Agent"] --> s12_sb1_test_agent["Test Agent"]
        s12_sb1_test_agent -->|fail| s12_sb1_build_agent
    end

    subgraph s12_sandbox_2["Sandbox 2"]
        direction LR
        s12_sb2_build_agent["Build Agent"] --> s12_sb2_test_agent["Test Agent"]
        s12_sb2_test_agent -->|fail| s12_sb2_build_agent
    end

    subgraph s12_sandbox_3["Sandbox 3"]
        direction LR
        s12_sb3_build_agent["Build Agent"] --> s12_sb3_test_agent["Test Agent"]
        s12_sb3_test_agent -->|fail| s12_sb3_build_agent
    end

    s12_create_code --> s12_sb1_build_agent
    s12_create_code --> s12_sb2_build_agent
    s12_create_code --> s12_sb3_build_agent
    s12_sb1_test_agent -->|pass| s12_review_human
    s12_sb2_test_agent -->|pass| s12_review_human
    s12_sb3_test_agent -->|pass| s12_review_human
    s12_review_human -->|fail| s12_hotfix_agent
    s12_review_human -->|pass| s12_ship_human
```

## Phase 6 — Routed software factory

### S13 — Route each ticket to the right specialized workflow

- **Capture filename:** `截圖 2026-07-23 下午3.40.02.png`
- **Frame-matched representative video position:** **21:51**
- **Supporting transcript range:** **19:11–23:44**
- **Conceptual takeaway:** A software factory classifies work and selects a workflow whose cost, model quality, isolation, controls, and human gates fit the job. Hotfixes, features, bugs, chores, and custom ADWs converge at merge and ship.

```mermaid
flowchart LR
    s13_support_human(["Support"])
    s13_product_human(["Product"])
    s13_engineer_human(["Engineer"])
    s13_ticket_code{"Kanban Ticket"}
    s13_prompt_human(["Engineer Prompt"])
    s13_start_code{"Start Factory"}
    s13_progress_code{"Status: In Progress"}
    s13_router_agent["Factory Router Agent"]
    s13_setup_code{"Setup Sandbox"}
    s13_merge_human(["Merge"])
    s13_ship_human(["Ship"])

    s13_support_human --> s13_ticket_code
    s13_product_human --> s13_ticket_code
    s13_engineer_human --> s13_ticket_code
    s13_ticket_code --> s13_prompt_human --> s13_start_code
    s13_ticket_code -->|advanced teams| s13_start_code
    s13_start_code --> s13_progress_code --> s13_router_agent --> s13_setup_code

    subgraph s13_hotfix_group["Hotfix Sandbox"]
        direction LR
        s13_hot_scout_agent["Scout Agent"] --> s13_hot_fix_agent["Hot Fix Agent"] --> s13_hot_gate_human(["Approve or Reject"])
        s13_hot_gate_human -->|reject| s13_hot_fix_agent
        s13_hot_gate_human -->|approve| s13_hot_build_agent["Build Agent"]
        s13_hot_build_agent --> s13_hot_test_agent["Test Agent"]
        s13_hot_test_agent -->|fail| s13_hot_build_agent
        s13_hot_test_agent -->|pass| s13_hot_review_human(["Engineer Review"])
        s13_hot_review_human -->|fail| s13_hot_build_agent
    end

    subgraph s13_feature_group["Feature Sandbox"]
        direction LR
        s13_feature_plan_agent["Planner Agent"] --> s13_feature_build_agent["Build Agent"] --> s13_feature_test_agent["Test Agent"]
        s13_feature_test_agent -->|fail| s13_feature_build_agent
        s13_feature_test_agent -->|pass| s13_feature_cicd_code{"CI/CD"}
        s13_feature_cicd_code -->|fail| s13_feature_build_agent
        s13_feature_cicd_code -->|pass| s13_feature_review_human(["Engineer Review"])
        s13_feature_review_human -->|fail| s13_feature_build_agent
    end

    subgraph s13_bug_group["Bug Sandbox"]
        direction LR
        s13_bug_plan_agent["Plan Agent"] --> s13_bug_build_agent["Build Agent"] --> s13_bug_test_agent["Test Agent"]
        s13_bug_test_agent -->|fail| s13_bug_build_agent
        s13_bug_test_agent -->|pass| s13_bug_cicd_code{"CI/CD"}
        s13_bug_cicd_code -->|fail| s13_bug_build_agent
        s13_bug_cicd_code -->|pass| s13_bug_review_human(["Engineer Review"])
        s13_bug_review_human -->|fail| s13_bug_build_agent
    end

    subgraph s13_chore_group["Chore Sandbox"]
        direction LR
        s13_chore_build_agent["Build Agent"] --> s13_chore_lint_code{"Lint"}
        s13_chore_lint_code -->|fail| s13_chore_build_agent
        s13_chore_lint_code -->|pass| s13_chore_cicd_code{"CI/CD"}
        s13_chore_cicd_code -->|fail| s13_chore_build_agent
        s13_chore_cicd_code -->|pass| s13_chore_review_human(["Engineer Review"])
        s13_chore_review_human -->|fail| s13_chore_build_agent
    end

    subgraph s13_custom_group["Any specialized ADW you need"]
        direction LR
        s13_custom_agent["Your ADW"]
    end

    s13_setup_code -->|hotfix| s13_hot_scout_agent
    s13_setup_code -->|feature| s13_feature_plan_agent
    s13_setup_code -->|bug| s13_bug_plan_agent
    s13_setup_code -->|chore| s13_chore_build_agent
    s13_setup_code -->|custom| s13_custom_agent
    s13_hot_review_human -->|pass| s13_merge_human
    s13_feature_review_human -->|pass| s13_merge_human
    s13_bug_review_human -->|pass| s13_merge_human
    s13_chore_review_human -->|pass| s13_merge_human
    s13_custom_agent -->|pass| s13_merge_human
    s13_merge_human --> s13_ship_human
```

## Operating playbook from the transcript

1. **Start simple.** Begin with the smallest workflow that solves a real problem: one build agent followed by one external deterministic check.
2. **Separate agents from code.** A skill that internally invokes every tool is still one opaque agent. Production workflows need explicit boundaries between adaptive agent work and deterministic execution.
3. **Walk the workflow manually first.** Perform every node, path, condition, review, and production transition yourself before encoding the orchestration.
4. **Specialize only after proof.** Split planner, scout, frontend, backend, test, or hotfix agents when observed workload and failure modes justify narrower context.
5. **Keep context and information flows explicit.** Store and pass results between steps deliberately, including failures, session identity, tickets, plans, test evidence, and review decisions.
6. **Balance agents with deterministic code.** Use agents where interpretation is valuable; use code where speed, reliability, repeatability, and zero-token execution are available.
7. **Retain classic modular and testable engineering.** Prefer isolated, decoupled nodes with single interfaces. Test planning, building, status updates, validation, failure routing, and shipping independently.
8. **Optimize the right work at the right performance, price, and speed.** A chore may need one lightweight workhorse; a production incident may justify state-of-the-art planning and many racing sandboxes.
9. **Keep engineers on the compounding layer.** Human effort is most leveraged in workflow design, guardrails, planning, and validation—the agentic layer that improves every future execution.

## Screenshot coverage matrix

| ID | Capture filename | Representative video position | Transcript range | Conceptual phase | Represented |
|---|---|---:|---:|---|---|
| S01 | `截圖 2026-07-23 下午3.37.40.png` | 03:51 | 03:37–04:44 | Actors | Yes |
| S02 | `截圖 2026-07-23 下午3.38.05.png` | 05:03 | 04:50–05:03 | Progressive workflow ladder | Yes |
| S03 | `截圖 2026-07-23 下午3.38.22.png` | 05:56 | 05:20–05:56 | Progressive workflow ladder | Yes |
| S04 | `截圖 2026-07-23 下午3.38.29.png` | 06:14 | 05:59–06:48 | Progressive workflow ladder | Yes |
| S05 | `截圖 2026-07-23 下午3.38.34.png` | 07:13 | 06:50–07:26 | Progressive workflow ladder | Yes |
| S06 | `截圖 2026-07-23 下午3.38.45.png` | 08:16 | 07:40–08:22 | Progressive workflow ladder | Yes |
| S07 | `截圖 2026-07-23 下午3.38.52.png` | 08:29 | 08:23–09:07 | Progressive workflow ladder | Yes |
| S08 | `截圖 2026-07-23 下午3.38.58.png` | 09:11 | 09:08–10:37 | Parallel isolation | Yes |
| S09 | `截圖 2026-07-23 下午3.39.14.png` | 11:54 | 10:41–11:58 | Parallel isolation | Yes |
| S10 | `截圖 2026-07-23 下午3.39.24.png` | 12:23 | 12:02–14:07 | Organizational intake | Yes |
| S11 | `截圖 2026-07-23 下午3.39.32.png` | 13:03 | 13:03–15:15 | Full organizational pipeline | Yes |
| S12 | `截圖 2026-07-23 下午3.39.54.png` | 17:46 | 15:21–17:46 | Hotfix race | Yes |
| S13 | `截圖 2026-07-23 下午3.40.02.png` | 21:51 | 19:11–23:44 | Routed software factory | Yes |

**Coverage: 13 of 13 supplied screenshots represented; no screenshot PNGs uploaded.**
