---
name: prompt-optimize
description: >-
  Canonical, production-ready skill for state-of-the-art prompt optimization and
  evaluation. Set up and run automatic prompt optimization (APO) and evaluation.
  Built with high-quality APO algorithms, a mature human-in-the-loop agentic
  experience, and a variety of reporting and customization capabilities.
---

# Prompt Optimization with GAF SDK

This skill guides you through orchestrating a prompt optimization for a user,
improving a prompt's performance on a target model using GAF SDK (an agent
harness for Prompt Optimization).

## 1. Orient

Before interacting with the user or running any commands, you must orient
yourself:

-   **Read the GAF SDK README**: You MUST read
    `learning/prompts/gemini_adoption/gaf_sdk/README.md` to deeply understand
    the available APIs, configuration options, and best practices. Do not assume
    you know the details. The README is the source of truth for the technical
    "how".
-   **Understand the CUJ**: The goal is to take a prompt, evaluate it on a
    target model, and then optimize it for that same model to improve
    performance.

## 2. Onboard the User

Act as the user interface. If the user has not already provided these, help them
get started by setting expectations and gathering high-level intent.

-   **Acknowledge the optimization**: Confirm that you will help them optimize
    their prompt for the target model, explicitly verifying the exact model
    variant (e.g., flash vs flash-lite).
-   **Gather high-level intent**: Understand what the prompt does and what the
    user hopes to achieve with the optimization.
-   **Defer details to README**: Refer to the `gaf_sdk/README.md` to know what
    inputs are required (e.g., dataset, prompt) and guide the user to provide
    them. Do not hardcode lists of required inputs here, as they may vary by
    case.
-   **Set expectations**: Advise the user that the initial setup and automated
    auditing may take 10-60 minutes as the agent iterates autonomously on
    correctness and addresses subagent critiques to ensure a correct setup
    before APO or evaluations begin.
-   **Plan the steps**: Explicitly outline the plan for the 3 distinct
    evaluation steps to the user before proceeding with execution (Baseline,
    APO, Final Eval).

## 3. Setup Code and Data

Before running the orchestration flow, you must prepare the environment. The
user knows their use case but likely does not know GAF SDK internals. You must
handle the technical setup.

-   **Preprocess Data**: If the user's dataset needs cleaning, formatting, or
    conversion to CSV/JSONL as required by GAF SDK, perform these operations.
-   **Write Glue Code**: Write the Python scripts needed to invoke the GAF SDK
    methods (as learned from the README) for this specific use case.
-   **Abstract Complexity Correctly**: The user may not know the gaf_sdk
    internals, though they do know their use case.

## 4. Typical Orchestration Flow

While you should always adapt to the user's specific needs and constraints, a
typical prompt optimization flow follows this pattern. Rely on the
`gaf_sdk/README.md` for the technical details of each step.

### Step 1: Establish Baseline on Target Model

-   Evaluate the existing prompt on the target model to get a baseline score.
-   This provides the reference point for the optimization's success.

### Step 2: Optimize for the Target Model

-   Run the APO (Automatic Prompt Optimization) loop targeting the **target
    model**, starting with the **existing prompt** as the starting point.
-   This generates the new optimized prompt tailored for the model's
    capabilities.

### Step 3: Compare and Report

-   Compare the performance to demonstrate the value of the optimization.
-   A typical comparison is between:
    *   Initial Prompt (Baseline)
    *   Optimized Prompt
-   Present the score delta and relevant reports to the user.

## 5. Open-Ended Exploration

After the structured flow, the user will likely transition to open-ended
investigation:

-   Ask the user what they want to dig into next (e.g., investigate what
    improved, failure analysis, criteria refinement).
-   Rely on the SDK's analysis tools as described in the README to answer their
    questions.
