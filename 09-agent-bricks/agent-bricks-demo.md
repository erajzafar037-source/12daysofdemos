%md
**12 Days of Demos**
# 🎅 Supervisor Clause with Agent Bricks 🎄

Agent Bricks provides a streamlined way to build and optimize domain-specific AI agent systems. Instead of writing custom orchestration code, you configure what you need and Databricks handles model selection, optimization, and deployment.

Agent Bricks supports four patterns:
- **Information Extraction** — Turn documents into structured tables
- **Custom LLM** — Summarization, classification, text transformation
- **Knowledge Assistant** — Q&A over documents with citations
- **Multi-Agent Supervisor** — Coordinate multiple agents and tools

---

### Prerequisites

**⚠️ Important:** You must complete the following demos before running this one:

- **Day 7: Vector Search** — Creates the `santa_letters_index` vector search index over Santa's letters
- **Day 8: Managed MCP** — Creates the Unity Catalog functions for operational data queries

This demo builds directly on the assets created in those previous days.

###  Overview

This demo shows how to use **Databricks Agent Bricks** to build a multi-agent AI system that coordinates across different data domains. We create:

1. **Knowledge Assistant** — A RAG-powered chatbot that answers questions about Santa's letters using the vector search index from Day 7
2. **Multi-Agent Supervisor** — An orchestration layer that coordinates the Knowledge Assistant with the Unity Catalog functions from Day 8

###  Demo Steps

📖 **Read the full walkthrough:** [Building Multi-Agent AI Systems with Databricks Agent Bricks](https://medium.com/@derek.witt-databricks/cffb70b3702c)


**Part 1: Create the Knowledge Assistant**

1. Navigate to **Agents** → **Knowledge Assistant**
2. Configure the agent:
   - **Name:** `npmo-letter-assistant`
   - **Description:** "Answers questions about children's letters to Santa, including sentiment, gift requests, tone, and Christmas spirit."
3. Add knowledge source:
   - **Type:** Vector Search Index
   - **Source:** `santa_letters_index` (from Day 7)
   - **Doc URI Column:** `name`
   - **Text Column:** `letter`
4. Add optional instructions for behavior guidance
5. Click **Create Agent** and wait for it to build
6. Test in Playground with questions like:
   - "Find me letters from children who seem especially grateful and polite."
   - "Which letters show the most Christmas spirit and enthusiasm?"

**Part 2: Create the Multi-Agent Supervisor**

1. Navigate to **Agents** → **Multi-Agent Supervisor**
2. Configure the supervisor:
   - **Name:** `npmo-operations-supervisor`
   - **Description:** "Coordinates North Pole operations by combining letter analysis with real-time operational data."
3. Add sub-agents:
   - **Letter Analyst** (Agent Endpoint): Select `npmo-letter-assistant`
   - **Unity Catalog Functions** (from Day 8):
     - `get_coal_warning_list`
     - `get_top_nice_children`
     - `get_child_naughty_nice_score`
     - `get_behavior_events_by_type`
     - `get_low_energy_reindeer`
     - `get_team_quality_metrics`
     - `get_workshop_material_totals`
4. Add coordination instructions
5. Click **Create Agent** and wait for it to build
6. Test with multi-domain questions like:
   - "Find letters from grateful, creative children, then tell me if any of them are on the coal warning list."
   - "Show me the top 10 nicest children and find their letters so I can see what they asked for."

### Key Concepts

- **Semantic search over unstructured data** — The Knowledge Assistant uses vector search to find letters by meaning, not just keywords
- **Structured data queries** — Unity Catalog functions provide access to operational metrics and scores
- **Multi-agent orchestration** — The supervisor routes questions to the right specialist and synthesizes results
- **Human feedback loops** — Both agents support labeling sessions to improve quality over time

### Resources

- [Agent Bricks Overview](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [Knowledge Assistant Documentation](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant)
- [Multi-Agent Supervisor Documentation](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)