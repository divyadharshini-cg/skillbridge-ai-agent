# SkillBridge AI: Multi-Agent Internship Readiness Coach & Portfolio Builder

### Capstone Project Writeup — Kaggle AI Agents Intensive Hackathon

---

## 1. Problem Statement
For college students and career transitioners, securing a first technical internship is a notoriously high-barrier milestone. While academic curricula teach general computer science theories (such as algorithms or basic databases), they rarely cover the practical engineering workflows required in the modern software industry (such as FastAPI web endpoints, containerization with Docker, unit testing with pytest, and writing clean documentation). 

This mismatch leads to the **"cold-start" career dilemma**:
* **Lack of Direction:** Students do not know exactly which industrial skills are missing from their current profiles.
* **Generic Projects:** Their resumes contain standard class projects (like basic calculators or generic house-price prediction notebooks) that fail to stand out to recruiters.
* **Unstructured Roadmaps:** They struggle to formulate cohesive day-by-day learning schedules.
* **Interview Unpreparedness:** They lack personalized mock interview opportunities to practice questions directly relevant to their skill gaps.

SkillBridge AI solves this by providing a multi-agent coaching companion that transforms raw resumes into customized 30-day prep roadmaps, specifies high-impact portfolio projects, drafts professional GitHub repository documentation, and conducts targeted mock interviews.

---

## 2. Why Agents?
Standard LLM prompting strategies fail to deliver the cohesive, multi-layered coaching required for career readiness. A single prompt trying to analyze a profile, map skill gaps, create a calendar roadmap, write markdown templates, and ask mock questions will suffer from:
1. **Context Bloat & Hallucination:** Mixing formatting instructions, local schema data, and mock questions results in degradation of generation quality.
2. **Lack of Computational Precision:** LLMs cannot reliably compute match percentages or verify mathematical scoring rules without external tools.
3. **Monolithic Failure Modes:** An API quota limit, profile honesty violation, or formatting error crashes the entire generation.

### The Agentic Solution: Choreographed Pipeline Pattern
By using a **cooperative multi-agent architecture**, we divide the workload among **10 specialized agents**:
* Specialized prompts ensure high quality and domain focus.
* A central shared state database allows earlier analysis stages to directly seed subsequent generation steps (e.g., the mock interview questions are generated dynamically using the exact gaps identified by the Skill Gap Agent).
* Isolation of safety checks, mathematical evaluations, and data extraction guarantees reliability.

---

## 3. Solution Overview
SkillBridge AI delivers a premium, interactive agentic dashboard. A student selects their target role, enters their core skills, and uploads a resume. The system executes a coordinated multi-agent pipeline to produce:
1. **Safety Audit Report:** Automatic identification of fake credential requests and redaction of PII (emails, phones) and environment secrets.
2. **Skill Gap Diagnostics:** Visual metrics showing strengths, gaps, and missing technologies compared to standard industry expectations.
3. **Internship Readiness Index:** A composite score weighting profile matches against interactive mock interview performance.
4. **30-Day Preparation Roadmap:** A day-by-day study schedule tailored to the candidate's available hours.
5. **Portfolio Project Specifications:** A customized GitHub-ready project designed to fill the candidate's gaps.
6. **Mock Technical Interview:** An interactive terminal where students answer questions targeted to their gaps, receiving instant grading and recommendations.

---

## 4. Architecture
The architecture of SkillBridge AI separates UI presentation, orchestration, and execution:

### Agent Choreography Diagram
```
    ┌──────────────────────┐
    │  Streamlit Dashboard │◄───────────┐
    └──────────┬───────────┘            │
               │ (Inputs)               │ (Final Output State)
               ▼                        │
    ┌──────────────────────┐            │
    │   CoordinatorAgent   ├────────────┘
    └──────────┬───────────┘
               │ (State Dictionary Flow)
               ▼
     [1. Safety Agent]
               │
     [2. Profile Analyzer Agent]
               │
     [3. Skill Gap Agent] ◄────────► [Local Role Database]
               │
     [4. Internship Match Agent]
               │
     [5. Roadmap Agent]
               │
     [6. Portfolio Project Agent]
               │
     [7. README Agent]
               │
     [8. Interview Agent]
               │
     [9. Evaluation Agent]
```

### Decoupled MCP-Style Tool Layer
The system isolates functional code from LLM agents via an **MCP-style tool registry** (`tools/mcp_server.py`). The registry manages tool metadata, exposes parameters as JSON-schema descriptions, and executes tools on request.
* **Native FastMCP Integration:** The registry includes support for FastMCP, allowing the system to run as a native MCP server for external developer clients (such as Claude Desktop or the Antigravity IDE).
* **Registered Tools:** Includes database loaders (`get_role_requirements`), matcher utilities (`match_skills_to_role`), scoring engines (`calculate_readiness_score`), roadmappers, and safety sanitizers.

---

## 5. Implementation details & Code Highlights

### The 10 Coordinated Agents
1. **CoordinatorAgent:** Manages execution flow, logging, and collects outcomes.
2. **SafetyAgent:** Audits resume text for credential inflation and masks sensitive data.
3. **ProfileAnalyzerAgent:** Parses education and lists candidate skills.
4. **SkillGapAgent:** Maps strengths and gaps against role criteria.
5. **InternshipMatchAgent:** Computes readiness percentages.
6. **RoadmapAgent:** Builds 30-day week-by-week study calendar.
7. **PortfolioProjectAgent:** Outlines custom projects.
8. **ReadmeAgent:** Generates markdown repository README files.
9. **InterviewAgent:** Generates targeted technical mock questions.
10. **EvaluationAgent:** Grades response data to update matching status.

### Resilience: No-Key Safe Fallback Mode
A critical requirement for this hackathon is that the system must remain fully functional even without a Gemini API key.
* **LLM Availability Check:** On startup, the system tests if a `GOOGLE_API_KEY` is present in the `.env` file.
* **Safe Mode Activation:** If no key is found, the `CoordinatorAgent` switches execution to fallback mode.
* **Deterministic Generators:** The system serves high-quality, pre-structured roadmap templates, custom project outlines, and role mock questions sourced from our local database.
* **Crash-Free Integration:** The UI displays `⚠️ Running in safe fallback mode` in the sidebar and functions normally, while LLM-based polishing is bypassed gracefully.

---

## 6. Security and Privacy
SkillBridge AI implements multi-tiered security to protect student information and maintain application integrity:

* **Sensitive Data Redaction:** Before any text is analyzed, the `SafetyAgent` runs regular expression mapping to identify and mask:
  * **Emails:** Masked as `[REDACTED_EMAIL]`.
  * **Phone Numbers:** Masked as `[REDACTED_PHONE]`.
  * **Secrets & Credentials:** Identifies high-entropy tokens, passwords, and API key definitions (like `GOOGLE_API_KEY=`, `sk-`, `AIzaSy...`), masking them as `[REDACTED_SECRET]`.
* **Fake Claim Prevention:** Detects requests to insert false career achievements (e.g. *"add fake certificate from Coursera"*, *"say I know TensorFlow although I don't"*). The Safety Agent blocks the injection, flags the request as `FAKE_CLAIMS_REQUEST`, lowers the resume integrity index, and provides professional alternatives:
  > **"I can't help add fake experience or false claims. I can help you describe your real projects and skills more professionally."**
* **Safe File Exports:** Final reports exported to Markdown or JSON are automatically passed through the redaction sanitizer to prevent credential leaks on disk.

---

## 7. Interactive Demo Workflow

### The Student Profile
* **Target Role:** `AI/ML Intern`
* **Skills Stated:** `Python, NumPy, basic ML, LeetCode`
* **Background:** Sophomore AI & DS student.
* **Stated Project:** Simple house price prediction in Python.
* **Schedule:** 2 hours per day.

### Dashboard Operations
1. **Safety Tab:** Displays safety flags, honesty ratings, and the redacted version of the profile showing masked credentials.
2. **Gap Analysis Tab:** Lists Python & NumPy as strengths; flags missing libraries (e.g., Pandas, Scikit-Learn) and deployment frameworks (e.g., FastAPI, Docker).
3. **Roadmap Tab:** Provides a 30-day schedule detailing Scikit-Learn model selection (Weeks 1-2) and FastAPI deployment basics (Weeks 3-4).
4. **Portfolio Project Tab:** Recommends building a *House Price Prediction API* with FastAPI, fully containerized with Docker, and tested using Pytest. Includes a downloadable repository README template.
5. **Mock Interview Tab:** Serves questions on model evaluation (e.g., bias-variance tradeoff) and algorithmic complexities.

---

## 8. Impact
* **Accelerating Career Starts:** SkillBridge AI replaces generic career guides with structured, customized plans that target the exact skills companies demand.
* **Portfolio Elevating:** It guides students to build projects with industrial standards (FastAPI, testing, Docker, documentation), elevating their resumes.
* **Reducing Job-Hunt Friction:** By offering personalized interview preparation, students enter their interviews with hands-on practice.

---

## 9. Future Scope
* **Live Job APIs:** Pulling live requirements from platforms like LinkedIn or Indeed.
* **Version Control Integration:** Integrating with GitHub API to auto-initialize repositories with the generated README.md templates.
* **Audio Interviews:** Leveraging WebRTC for voice-based technical mock interviews.

---

## 10. Conclusion
SkillBridge AI illustrates how cooperative multi-agent systems, supported by a structured tool layer and resilient API fallbacks, can deliver secure, high-value personal coaching. By pairing advanced safety sanitization with professional career metrics, the application serves as a judge-ready capstone for the Kaggle AI Agents hackathon.
