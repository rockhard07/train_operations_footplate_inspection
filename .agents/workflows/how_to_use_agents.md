---
description: How to use specific agents for operations project
---
# Utilizing Agent Workflows

To make the optimal use of AI agents in this project, we have defined specific agent personas/workflows. This folder (`.agents/workflows/`) contains markdown files that act as sets of instructions for the agent context.

## How to use them
When you want an AI agent to perform a specific task efficiently, you can point them to one of these workflows by saying:
**"Run the [Workflow Name] workflow to do [Specific Task]"** or by writing `/slash-command` if supported by your AI editor interface.

By dividing tasks this way:
1. **Frontend Agent** focuses only on HTML/CSS/Vanilla JS and respects the existing design system without trying to introduce heavy frameworks like React.
2. **Backend & DB Agent** handles Python proxy scripts, Supabase schema changes, data migrations, and secrets management securely.
3. **Data Processing Agent** handles complex Python utility scripts (`update_pages.py`, etc.) ensuring no frontend code gets broken during batch updates.

Explore the `.md` files in this directory for the exact specifications of each agent.
