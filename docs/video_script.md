# SkillBridge AI: Video Demo Script (5 Minutes)

Use this script as a teleprompter-friendly guide for your 5-minute YouTube submission. It includes visual cues, timing guidance, and spoken lines.

---

## ⏱️ Timeline Overview
* **0:00 - 0:30:** Problem Statement (The cold-start dilemma)
* **0:30 - 1:00:** Why AI Agents? (Limits of single prompts)
* **1:00 - 1:45:** Multi-Agent Architecture (The 10 choreographed agents & MCP tool layer)
* **1:45 - 3:30:** Live Demo Walkthrough (Streamlit UI dashboard)
* **3:30 - 4:15:** Security, Privacy & Fallback Mode
* **4:15 - 4:45:** Real-world Impact & Future Scope
* **4:45 - 5:00:** Conclusion & Call-to-Action

---

## 🎙️ Script Details

### 🎥 0:00 - 0:30 | Section 1: The Problem
* **[Visual]** Close-up of speaker, then overlaying bullet points showing: "No Industrial Skills", "Generic Portfolios", "Resume Honesty Warnings".
* **[Speaker]**
  "Landing your first technical internship is a major hurdle. 
  Most college students face a classic 'cold-start' dilemma: university courses teach general theory, but employers want practical software experience like FastAPI, Docker, and unit testing.
  Students don't know what skills they lack, they build generic projects, and they struggle with technical interview preparation.
  Meet **SkillBridge AI** — a secure multi-agent dashboard designed to coach students into internship readiness."

---

### 🎥 0:30 - 1:00 | Section 2: Why AI Agents?
* **[Visual]** Animation or diagram of a single LLM prompt vs. multiple specialized agents passing data.
* **[Speaker]**
  "But why use AI agents? 
  A single prompt to an LLM cannot solve this. Generating roadmap schedules, designing repository architectures, scoring candidate readiness, and running mock interviews is too complex.
  SkillBridge AI divides these tasks among **10 specialized agents** that cooperate in a choreographed pipeline.
  By separating safety, matching, roadmap generation, and interview evaluation, we ensure reliability, security, and high performance."

---

### 🎥 1:00 - 1:45 | Section 3: The Architecture
* **[Visual]** On-screen view of the Mermaid architecture diagram from `docs/architecture.md`.
* **[Speaker]**
  "Let's look at the architecture. 
  Our pipeline begins with the **Coordinator Agent** managing the state.
  First, the **Safety Agent** filters inputs and masks PII.
  Then, the **Profile Analyzer** and **Skill Gap Agents** cross-reference the student's background against our local role database.
  Finally, the **Roadmap**, **Portfolio**, **README**, and **Interview Agents** generate tailored preparation kits.
  Everything is backed by an **MCP-style tool registry** that separates functional python code from LLM generation, allowing the platform to run as a standard external Model Context Protocol server."

---

### 🎥 1:45 - 3:30 | Section 4: Live Demo Walkthrough
* **[Visual]** Screen recording of the Streamlit dashboard in action. Navigate through the tabs as you speak.
* **[Speaker]**
  "Here is our dashboard. Let's see it in action.
  In the sidebar, we configure our student: a sophomore AI student targeting an **AI/ML Intern** role, with basic skills like Python and NumPy, and a simple house price prediction project.
  Let's run the coaching evaluation.
  First, the **Safety Review** tab: it checks profile integrity. It computes an honesty score and redacts our email and phone details into safe placeholders.
  Next, the **Gap Analysis** tab: we see a readiness match of 65%. It highlights python as a strength but flags missing libraries like Pandas, Scikit-Learn, and deployment frameworks.
  Moving to the **30-Day Roadmap**: we get a customized week-by-week calendar.
  In the **Portfolio Project** tab: the agent suggests building a containerized FastAPI model server, complete with a download link for a professional README.
  Finally, the **Mock Interview** tab: the student can practice answering technical questions and receive immediate feedback from the Evaluation Agent."

---

### 🎥 3:30 - 4:15 | Section 5: Security, Privacy & Fallbacks
* **[Visual]** Focus on the sidebar notice showing fallback mode, then view the redacted code block in the Safety Review tab.
* **[Speaker]**
  "Security and privacy are built-in from the ground up.
  SkillBridge AI automatically masks emails, phone numbers, and secrets.
  It also checks for resume inflation. If a student tries to inject fake claims — like claiming they worked at Google when they didn't — the Safety Agent flags it and suggests honest alternatives.
  All exported Markdown and JSON reports are sanitized before writing to disk.
  Plus, the app runs fully in **Safe Fallback Mode** even if no Gemini API key is configured, using local database templates to prevent application crashes."

---

### 🎥 4:15 - 4:45 | Section 6: Real-World Impact & Future Scope
* **[Visual]** Visual cards highlighting "Enterprise-Ready", "100% Secure", "FastMCP Enabled".
* **[Speaker]**
  "SkillBridge AI provides high-value, secure, and personalized coaching.
  For college students, it demystifies the interview prep loop.
  Looking forward, we plan to connect live job search APIs to map real-time skill trends, and integrate directly with GitHub to auto-commit repository setups."

---

### 🎥 4:45 - 5:00 | Section 7: Closing
* **[Visual]** Final screen showing the GitHub repository URL, Kaggle hackathon logo, and "Developed with Antigravity".
* **[Speaker]**
  "SkillBridge AI is fully tested, secure, and ready for deployment.
  Thank you for watching our submission for the Kaggle AI Agents Intensive Hackathon!"
