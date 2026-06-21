import streamlit as st
import os
import time
from llm_client import LLMClient, is_llm_available
from agents.coordinator_agent import CoordinatorAgent

# Page configuration
st.set_page_config(
    page_title="SkillBridge AI - Multi-Agent Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #ffffff;
    }

    /* Main Title Styling */
    .title-container {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.4);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .title-container::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .title-header {
        font-size: 2.8rem;
        margin: 0;
        color: white !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .title-subheader {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        font-weight: 300;
    }

    .capstone-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Cards & Containers */
    .agent-card {
        background-color: #1e1b4b;
        border: 1px solid #312e81;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }

    /* Pulsing Active Indicator */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.6s infinite;
    }

    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar UI
st.sidebar.image("https://img.icons8.com/nolan/96/graduation-cap.png", width=70)
st.sidebar.markdown("### 🎓 Profile Dashboard")

# Student Details Input
student_name = st.sidebar.text_input("Student Name", "Alex Mercer")
target_role = st.sidebar.selectbox(
    "Target Internship Role",
    ["AI/ML Intern", "Data Analyst Intern", "Python Developer Intern", "Web Developer Intern", "GenAI Intern"]
)
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/Markdown)", type=["pdf", "md", "txt"])

# Key Skills tag input helper
skills_input = st.sidebar.text_area("Existing Core Skills (Comma-separated)", "Python, Git, SQLite, HTML5, CSS3")

# Privacy Note
st.sidebar.markdown("""<div style="background: rgba(239,68,68,0.10); border:1px solid rgba(239,68,68,0.3); border-radius:8px; padding:0.65rem 0.85rem; margin: 0.5rem 0; font-size:0.78rem; color:#fca5a5;">
🔒 <strong>Privacy Notice</strong><br>
Resume/profile text is processed <em>only for this session</em>. Do not paste passwords, API keys, or highly sensitive personal data.
</div>""", unsafe_allow_html=True)

# Run Evaluation Button
evaluate_btn = st.sidebar.button("🤖 Launch Multi-Agent Coaching", use_container_width=True)

# Main Title Header
st.markdown("""
<div class="title-container">
    <span class="capstone-badge">Kaggle AI Agents Intensive Capstone Project</span>
    <h1 class="title-header">SkillBridge AI</h1>
    <div class="title-subheader">Multi-Agent Internship Readiness Coach & Portfolio Builder</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Agent status check widget
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Coach Status")
st.sidebar.markdown("""
<div class="status-indicator">
    <div class="pulse-dot"></div>
    <span>Coordinator Agent Active</span>
</div>
""", unsafe_allow_html=True)

if is_llm_available():
    st.sidebar.markdown("""
    <div class="status-indicator" style="margin-top: 0.5rem;">
        <div class="pulse-dot" style="background-color: #10b981; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);"></div>
        <span>Running in Gemini-assisted mode</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="status-indicator" style="margin-top: 0.5rem;">
        <div class="pulse-dot" style="background-color: #f59e0b; box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); animation: pulse-orange 1.6s infinite;"></div>
        <span>Running in safe fallback mode</span>
    </div>
    <style>
    @keyframes pulse-orange {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 6px rgba(245, 158, 11, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Coordinator
coordinator = CoordinatorAgent()

# Initialize session state for report
if "report" not in st.session_state:
    st.session_state.report = None

# Handle running the multi-agent orchestration
if evaluate_btn:
    # Read resume file if uploaded
    profile_text = ""
    if uploaded_file is not None:
        try:
            profile_text = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")
            
    if not profile_text:
        # Build composite profile text from inputs
        profile_text = (
            f"Name: {student_name}\n"
            f"Target Role: {target_role}\n"
            f"Skills: {skills_input}\n"
            f"Education: Bachelor of Science in Computer Science\n"
            f"Branch: Computer Science"
        )
        
    with st.spinner("🤖 Coordinating SkillBridge agents..."):
        student_input = {
            "name": student_name,
            "target_role": target_role,
            "current_skills": [s.strip() for s in skills_input.split(",") if s.strip()],
            "profile_text": profile_text,
            "learning_time": 2.0,
            "deadline": 30
        }
        # Run coordinator pipeline
        st.session_state.report = coordinator.execute_pipeline(student_input)
        st.success("🎉 Multi-agent analysis completed successfully!")

# Tabs layout
tab_overview, tab_profile, tab_skills, tab_roadmap, tab_portfolio, tab_interview = st.tabs([
    "💡 Overview",
    "🛡️ Safety Review",
    "🎯 Gap Analysis",
    "📅 30-Day Roadmap",
    "💻 Portfolio Project",
    "💬 Mock Interview"
])

with tab_overview:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Welcome to SkillBridge AI!")
        st.markdown(
            "SkillBridge AI uses a multi-agent choreography pattern to guide college students through "
            "becoming internship-ready. By analyzing your resume and comparing it to live job requirements, "
            "our agents cooperate to tailor a 30-day prep guide, recommend realistic portfolio project milestones, "
            "write clean README templates, and test you with mock questions."
        )

        report = st.session_state.report
        if report:
            # ── Completed Analysis Summary ────────────────────────────────────
            st.markdown("### ✅ Analysis Complete — Your Readiness Summary")

            # Readiness score & target role
            readiness  = report.get("readiness_score", 0)
            profile    = report.get("profile_summary") or {}
            role_disp  = profile.get("target_role") or report.get("target_role", "N/A")

            m1, m2 = st.columns(2)
            with m1:
                st.metric("🎯 Internship Readiness Score", f"{readiness}%")
            with m2:
                st.metric("💼 Target Role", role_disp)

            st.progress(min(max(int(readiness), 0), 100) / 100.0)

            # Top 3 missing skills
            gap    = report.get("skill_gap_analysis") or {}
            ranked = gap.get("ranked_gaps") or []
            top3   = ranked[:3]
            st.markdown("#### 🔍 Top 3 Missing Skills")
            if top3:
                for skill_info in top3:
                    skill    = skill_info.get("skill", "Unknown") if isinstance(skill_info, dict) else str(skill_info)
                    priority = skill_info.get("priority", "")     if isinstance(skill_info, dict) else ""
                    badge    = f" *({priority} Priority)*" if priority else ""
                    st.markdown(f"- **{skill}**{badge}")
            else:
                st.markdown("- No skill gaps found — you're well-matched for this role! 🎉")

            # Recommended portfolio project
            proj       = report.get("portfolio_project") or {}
            proj_title = proj.get("title") or proj.get("project_name", "N/A")
            st.markdown("#### 💻 Recommended Portfolio Project")
            st.success(f"**{proj_title}**")

            # Next best action
            st.markdown("#### ⚡ Next Best Action")
            roadmap     = report.get("roadmap_30_days") or {}
            eval_sum    = report.get("evaluation_summary") or {}
            next_action = eval_sum.get("next_action") or eval_sum.get("next_step") or ""
            if not next_action and isinstance(roadmap, dict):
                weeks = roadmap.get("weeks") or []
                if weeks:
                    first_week = weeks[0] if isinstance(weeks[0], dict) else {}
                    next_action = first_week.get("goal") or first_week.get("focus") or ""
            if not next_action:
                next_action = (
                    f"Start closing your top skill gap: **{top3[0].get('skill', 'the missing skill') if top3 else 'key skills'}**. "
                    "Open the 📅 30-Day Roadmap tab for your personalised study plan."
                )
            st.info(f"👉 {next_action}")

            st.markdown("---")

            # ── Multi-Agent Execution Trace ───────────────────────────────────
            trace_list = report.get("agent_trace", []) or report.get("execution_trace", [])
            if trace_list:
                st.markdown("### 🤖 Multi-Agent Execution Trace")
                for trace in trace_list:
                    if isinstance(trace, dict):
                        agent_name  = trace.get("agent") or trace.get("name") or "Agent"
                        action_desc = trace.get("action") or trace.get("summary") or ""
                        st.info(f"**{agent_name}:** {action_desc}")
                    else:
                        st.info(str(trace))
        else:
            st.info(
                "👉 **To begin**: Adjust your target role and skills in the sidebar, and click **Launch Multi-Agent Coaching**."
            )

    with col2:
        st.markdown("### Cooperative Agents")
        st.markdown("""
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">👤 Profile Analyzer</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Parses student profiles and extracts education, branch, and skills.</p>
        </div>
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">🛡️ Safety Agent</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Scans for credential integrity, secrets exposure, and PII leaks.</p>
        </div>
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">🎯 Skill Gap & Matches</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Evaluates core weaknesses and ranks compatibility with roles.</p>
        </div>
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">📅 Roadmap & Project Coach</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Generates weekly goals, daily study hours, and repository README.md.</p>
        </div>
        """, unsafe_allow_html=True)

with tab_profile:
    st.markdown("### 🛡️ Safety Review & Honesty Check")
    st.markdown(
        "The Safety Agent audits your profile for honesty, secret leaks, PII, "
        "and fake claim requests before any coaching begins."
    )

    if st.session_state.report:
        report = st.session_state.report
        profile = report.get("profile_summary") or {}
        safety  = report.get("safety_review") or {}

        if not profile:
            st.warning("Profile summary is not available. Re-run the coaching pipeline.")
        else:
            # ── Row 1: Student snapshot ──────────────────────────────────────
            st.markdown("#### 👤 Student Profile Snapshot")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write(f"**Name:** {profile.get('name', 'N/A')}")
                st.write(f"**Target Role:** {profile.get('target_role', 'N/A')}")
                skills_list = profile.get('current_skills') or []
                st.write(f"**Extracted Skills:** {', '.join(skills_list) if skills_list else 'N/A'}")
            with col_p2:
                st.write(f"**Education:** {profile.get('education', 'N/A')}")
                st.write(f"**Branch/Major:** {profile.get('branch', 'N/A')}")

            st.markdown("---")

            # ── Row 2: Safety diagnostics ────────────────────────────────────
            st.markdown("#### 🔍 Safety Diagnostics")
            passed        = safety.get('passed_safety', True)
            honesty_score = safety.get('honesty_score', 100)
            flags         = safety.get('safety_flags') or []
            warnings_list = safety.get('warnings') or []
            alternatives  = safety.get('honest_alternatives') or []

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                icon = "✅" if passed else "❌"
                st.metric("Overall Safety", f"{icon} {'Passed' if passed else 'Failed'}")
            with col_s2:
                st.metric("Honesty Score", f"{honesty_score}/100")
            with col_s3:
                api_clean = "API_KEY_LEAK" not in flags
                st.metric("Secret Check", "✅ Clean" if api_clean else "⚠️ Secrets Found")

            # Active flags
            if flags:
                st.markdown("**🚩 Active Safety Flags:**")
                flag_labels = {
                    "FAKE_CLAIMS_REQUEST": "🚫 Fake Claims Request",
                    "SUSPICIOUS_CLAIMS":   "⚠️ Suspicious Experience Claims",
                    "API_KEY_LEAK":        "🔑 API Key / Secret Detected",
                    "PROFANITY_DETECTED":  "🤬 Profanity Detected",
                }
                for f in flags:
                    label = flag_labels.get(f, f)
                    st.error(label)

            # Warnings
            if warnings_list:
                st.markdown("**⚠️ Warnings:**")
                for w in warnings_list:
                    st.warning(w)

            st.markdown("---")

            # ── Row 3: Redacted safe profile ─────────────────────────────────
            st.markdown("#### 🔏 Sensitive Data Redaction Result")
            safe_text = safety.get('safe_profile_text', '')
            if safe_text:
                st.info(
                    "The profile below has had emails, phone numbers, and secrets automatically "
                    "replaced with `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, and `[REDACTED_SECRET]`."
                )
                st.code(safe_text, language="text")
            else:
                st.write("No profile text to display.")

            st.markdown("---")

            # ── Row 4: Improvement suggestions ───────────────────────────────
            st.markdown("#### 💡 Safe Resume Improvement Suggestions")
            if alternatives:
                for alt in alternatives:
                    st.success(alt)
            else:
                st.success(
                    "Your profile looks honest and clean. "
                    "Focus on quantifying real achievements (e.g., 'built X using Y, resulting in Z')."
                )

            # ── Row 5: Privacy reminder ───────────────────────────────────────
            st.markdown("---")
            st.markdown(
                "<div style='background:rgba(239,68,68,0.08);border:1px solid "
                "rgba(239,68,68,0.3);border-radius:8px;padding:0.75rem 1rem;font-size:0.85rem;"
                "color:#fca5a5;'>"
                "🔒 <strong>Privacy Reminder</strong> — Resume/profile text is processed "
                "<em>only for this session</em> and is never stored permanently. "
                "Do not paste passwords, API keys, or highly sensitive personal data."
                "</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("Run the agent dashboard from the sidebar to populate the safety review.")

with tab_skills:
    st.markdown("### Core Gap Analysis")
    st.markdown("Comparing your skills with live requirements for target role:")
    
    if st.session_state.report:
        report = st.session_state.report
        gap = report.get("skill_gap_analysis") or {}
        matches = report.get("internship_matches") or []
        profile = report.get("profile_summary") or {}
        readiness = report.get("readiness_score", 0)

        target_role_display = profile.get('target_role', 'N/A')
        st.markdown(f"#### Target: **{target_role_display}**")
        st.progress(min(max(readiness, 0), 100) / 100.0)
        st.markdown(f"*Overall Readiness Score: **{readiness}%***")

        if not gap:
            st.warning("Skill gap analysis data is not available. Re-run the coaching pipeline.")
        else:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.success("##### Matching Skills")
                matching = gap.get("matching_skills") or []
                for skill in matching:
                    st.write(f"- {skill}")
                if not matching:
                    st.write("No matching skills found for this role.")
            with col_s2:
                st.error("##### Identified Skill Gaps")
                ranked = gap.get("ranked_gaps") or []
                for skill_info in ranked:
                    st.write(f"- **{skill_info.get('skill', '')}** ({skill_info.get('priority', '')} Priority)")
                if not ranked:
                    st.write("No gaps identified. You match all required skills!")

            st.markdown("##### Skill Gap Explanation")
            st.markdown(gap.get("explanation") or "No explanation available.")

        if matches:
            st.markdown("---")
            st.markdown("### Database Role Matches")
            for match in matches:
                role_name = match.get('role_name', 'Unknown Role')
                fit_level = match.get('fit_level', 'N/A')
                score = match.get('match_score', 0.0)
                st.markdown(f"**{role_name}** - *{fit_level} (Score: {score:.1f}%)*")
                st.write(match.get("explanation", ""))
    else:
        st.info("Run the agent dashboard from the sidebar to populate gap analysis.")

with tab_roadmap:
    st.markdown("### 30-Day Preparation Roadmap")
    st.markdown("A step-by-step roadmap to close the skill gap before your interviews.")
    
    if st.session_state.report:
        report = st.session_state.report
        roadmap = report.get("roadmap_30_days") or {}
        markdown_content = roadmap.get("markdown") if isinstance(roadmap, dict) else str(roadmap)
        if markdown_content:
            st.markdown(markdown_content)
        else:
            st.warning("Roadmap data is not available. Re-run the coaching pipeline.")
    else:
        st.info("Run the agent dashboard from the sidebar to generate your roadmap.")

with tab_portfolio:
    st.markdown("### Portfolio Project Recommender & README Creator")
    st.markdown("High-impact projects that showcase missing skills on your resume.")
    
    if st.session_state.report:
        report = st.session_state.report
        proj = report.get("portfolio_project") or {}

        if not proj:
            st.warning("Portfolio project data is not available. Re-run the coaching pipeline.")
        else:
            title = proj.get('title') or proj.get('project_name', 'N/A')
            st.markdown(f"#### Recommended Project: **{title}**")
            st.markdown(f"**Problem Statement:** {proj.get('problem', 'N/A')}")
            st.markdown("**Core Features:**")
            for feature in (proj.get("features") or []):
                st.write(f"- {feature}")
            tech_list = proj.get('tech_stack') or []
            st.write(f"**Tech Stack:** {', '.join(tech_list) if tech_list else 'N/A'}")
            st.write(f"**Dataset Idea:** {proj.get('dataset_idea', 'N/A')}")
            folder = proj.get("folder_structure")
            if folder:
                st.write("**Folder Structure:**")
                st.code(folder)
            st.write(f"**Demo Plan:** {proj.get('demo_plan', 'N/A')}")

        st.markdown("---")
        st.markdown("#### Generated Portfolio README (GitHub Ready)")
        readme = report.get("generated_readme") or "README not generated yet."
        st.code(readme, language="markdown")
    else:
        st.info("Run the agent dashboard from the sidebar to recommend a project.")

with tab_interview:
    st.markdown("### Mock Interview Engine")
    st.markdown("Sample interview questions derived from your resume gaps.")
    
    if st.session_state.report:
        report = st.session_state.report
        questions = report.get("interview_questions") or []
        eval_sum = report.get("evaluation_summary") or {}

        if not questions:
            st.warning("Interview questions are not available. Re-run the coaching pipeline.")
        else:
            for i, q in enumerate(questions):
                category = q.get('category', 'General') if isinstance(q, dict) else 'General'
                question_text = q.get('question', str(q)) if isinstance(q, dict) else str(q)
                st.markdown(f"#### Question {i+1} ({category} Focus)")
                st.info(question_text)
                st.text_area("Your response:", placeholder="Type your answer here...", key=f"ans_{i}")

        st.markdown("---")
        st.subheader("Final Report Quality Review Check")
        if eval_sum:
            overall = eval_sum.get('overall_score', 'N/A')
            st.metric(label="Overall Quality Score", value=f"{overall}/100")
            st.write("**Evaluation Feedback:**")
            st.markdown(eval_sum.get("feedback") or "No feedback available.")
        else:
            st.warning("Evaluation summary is not available. Re-run the coaching pipeline.")
    else:
        st.info("Run the agent dashboard from the sidebar to see mock questions.")
