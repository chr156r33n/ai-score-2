AI Opportunity Framework - Technical Specification (V1)

Objective

Build a repeatable and largely deterministic framework for prioritising AI optimisation opportunities across a website.

The framework should estimate:

Where should we invest effort to improve AI visibility?

The framework is NOT attempting to:

* Predict citations
* Predict recommendation probability
* Attribute revenue to AI systems
* Model LLM reasoning

Instead, the framework estimates opportunity using observable and measurable signals.

⸻

Core Principle

Opportunity is a combination of:

1. AI Attention (Demand)
2. Interpretability Gap (Technical)
3. Eligibility Gap (Content)
4. Credibility Gap (Off-page)

The framework should score areas that can be measured directly and avoid attempting to score opaque AI decision-making processes.

⸻

High-Level Formula

Opportunity Score
=
AI Attention
×
(
Interpretability Gap
+
Eligibility Gap
+
Credibility Gap
)

The exact weighting can be configurable.

Initial recommendation:

Interpretability: 20%
Eligibility: 50%
Credibility: 30%

⸻

Component 1: AI Attention

Purpose

Estimate how much AI-related activity exists around a topic, page or entity.

This serves as the closest equivalent to search demand.

Inputs

Potential sources:

* GPTBot visits
* ChatGPT-User visits
* Other AI crawler visits
* AI referral traffic
* Citation frequency
* Prompt prevalence datasets
* Query frequency datasets

Output

{
  "ai_attention_score": 0-100
}

Requirements

* Must be normalised across the site
* Should support percentile-based scaling
* Must allow multiple signals to be combined

⸻

Component 2: Interpretability Gap

Purpose

Determine whether a machine can easily consume and understand the page.

This is primarily a technical assessment.

Inputs

Primary source:

* Screaming Frog exports

Potential checks:

* Crawlability
* Indexability
* Canonicalisation
* Structured data presence
* Structured data validity
* Internal linking
* Renderability
* Metadata quality
* Content extraction success

Method

Deterministic.

No LLM required.

Output

{
  "interpretability_score": 0-100,
  "issues": [...]
}

Gap calculation:

Interpretability Gap
=
100 - Interpretability Score

⸻

Component 3: Eligibility Gap

Purpose

Measure how well content covers the information required to answer questions within a topic.

This is a content coverage problem.

Overview

Eligibility is measured against a benchmark corpus.

Pages are not scored in isolation.

Pages are scored relative to what AI systems may need to answer relevant questions.

⸻

Step 1: Build Benchmark Corpus

Potential sources:

* AlsoAsked
* People Also Ask
* SERP competitors
* Citation sources
* Top-ranking content
* Internal subject matter sources

Output:

{
  "topic": "...",
  "benchmark_questions": [...],
  "benchmark_facts": [...]
}

⸻

Step 2: Extract Page Facts

Use deterministic extraction wherever possible.

Potential methods:

* Named entities
* Structured data
* Headings
* Key-value extraction
* LLM-assisted extraction

Output:

{
  "page_facts": [...]
}

⸻

Step 3: Coverage Analysis

Compare page facts against benchmark facts.

Calculate:

Coverage %

Example:

Benchmark Facts: 100
Present Facts: 65
Coverage = 65%

⸻

Step 4: Utility Weighting

LLM involvement begins here.

Prompt:

* Benchmark facts
* Present facts
* Missing facts

Ask the model to:

1. Identify missing facts
2. Weight importance (1-5)
3. Output structured JSON only

Example:

{
  "missing_fact": "Pet Policy",
  "importance": 5
}

⸻

Output

{
  "eligibility_score": 0-100,
  "missing_facts": [...],
  "high_priority_gaps": [...]
}

Gap calculation:

Eligibility Gap
=
100 - Eligibility Score

⸻

Component 4: Credibility Gap

Purpose

Estimate trust and authority signals available to AI systems.

This is NOT attempting to directly measure trust.

It measures observable trust-related signals.

⸻

Inputs

Potential sources:

* DataForSEO
* Backlink APIs
* Review APIs
* Brand mention APIs
* Local profile APIs

Potential metrics:

* Referring domains
* Review volume
* Average review score
* Brand mentions
* Citation frequency
* Entity consistency

⸻

Output

{
  "credibility_score": 0-100
}

Gap calculation:

Credibility Gap
=
100 - Credibility Score

⸻

Design Principles

Deterministic First

Python should own:

* Scoring
* Calculations
* Aggregation
* Weighting
* Benchmark creation

Avoid agent-based orchestration.

⸻

LLM as Specialist

The LLM should only be used where judgement is required.

Current use cases:

* Missing fact importance weighting
* Fact deduplication
* Fact classification

The LLM should not:

* Drive workflows
* Choose tools
* Build benchmarks autonomously

⸻

Explainability

Every score must be explainable.

The system should always be able to answer:

* Why did this page score 72?
* Why did this page score lower than another page?
* What actions would increase the score?

⸻

Desired Outputs

For each URL:

{
  "url": "...",
  "ai_attention": 84,
  "interpretability": 76,
  "eligibility": 61,
  "credibility": 68,
  "opportunity": 83
}

Additionally:

{
  "top_recommended_actions": [...]
}

⸻

Non-Goals (V1)

Do NOT attempt to:

* Predict LLM recommendations
* Predict citation likelihood
* Predict revenue
* Infer hidden model behaviour
* Score “trust” directly

The framework should focus exclusively on observable and actionable signals.
