# Kaggle AI Agents Intensive Capstone Writeup

## Project Title
**SkillBridge AI: Multi-Agent Internship Readiness Coach**

## Short Pitch
An intelligent multi-agent coach that transforms student resumes into comprehensive 30-day prep roadmaps, suggests tailored portfolio projects, generates repository READMEs, and conducts mock interviews to accelerate landing first technical internships.

## Hackathon Track
- [x] Agentic UI / Custom Streamlit Dashboard
- [x] Multi-Agent Choreography/Orchestration

## System Design & Architecture
- **Framework:** Streamlit (Custom interactive dashboard UI with CSS injections).
- **Core Orchestrator:** Coordinator Agent scheduling safety and generative pipelines.
- **Model:** Google Gemini (`gemini-1.5-flash` model client).
- **Knowledge Representation:** Local JSON role matching schema (`role_requirements.json`) and MCP integration templates.

## Evaluation & Results
- Profile analysis successfully segments strengths and gaps for common tech tracks.
- Automated tests verify accuracy and safety constraints.
- Evaluation agents measure honesty indices and question accuracy.

## Video Demo Link
- *To be populated (YouTube/Vimeo demo link)*
