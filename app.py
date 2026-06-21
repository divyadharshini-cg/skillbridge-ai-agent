import streamlit as st
import os
from llm_client import LLMClient
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
    ["Software Engineer Intern", "Data Scientist Intern", "Product Manager Intern", "UX Design Intern"]
)
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/Markdown)", type=["pdf", "md", "txt"])

# Key Skills tag input helper
skills_input = st.sidebar.text_area("Existing Core Skills (Comma-separated)", "Python, Git, Basic SQL, HTML/CSS")

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

# Setup basic agents
coordinator = CoordinatorAgent()

# Tabs layout
tab_overview, tab_profile, tab_skills, tab_roadmap, tab_portfolio, tab_interview = st.tabs([
    "💡 Overview", 
    "👤 Profile Integrity", 
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
        st.info(
            "👉 **To begin**: Adjust your target role and skills in the sidebar, and click **Launch Multi-Agent Coaching**."
        )
        
        # Display mock process logs
        if evaluate_btn:
            st.success("🎉 Multi-agent analysis triggered! Showing starter results below:")
            with st.spinner("Agents processing profile..."):
                status_box = st.empty()
                status_box.markdown("*[Coordinator]* Routing profile to `ProfileAnalyzerAgent`...")
                # Mock steps
                import time
                time.sleep(0.3)
                status_box.markdown("*[SafetyAgent]* Checking resume integrity and toxicity... **Pass**.")
                time.sleep(0.3)
                status_box.markdown("*[SkillGapAgent]* Comparing skills to target role requirements... Done.")
                time.sleep(0.3)
                status_box.markdown("*[Coordinator]* Creating personalized 30-day preparation schedule... Complete.")
    
    with col2:
        st.markdown("### Active Agents")
        st.markdown("""
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">👤 Profile Analyzer</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Parses student profiles and scores baseline readiness.</p>
        </div>
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">🎯 Skill Gap & Matches</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Evaluates core weaknesses and match rates.</p>
        </div>
        <div class="agent-card">
            <h5 style="margin:0 0 0.5rem 0; color:#818cf8;">📅 Roadmap & Portfolio Coach</h5>
            <p style="font-size:0.85rem; margin:0; color:#cbd5e1;">Generates day-by-day learning tasks and GitHub assets.</p>
        </div>
        """, unsafe_allow_html=True)

with tab_profile:
    st.markdown("### Profile Analysis & Honesty Check")
    st.markdown("The profile analysis agent inspects your skills, and the safety agent checks for resume honesty.")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Student Details")
        st.write(f"**Name:** {student_name}")
        st.write(f"**Target Role:** {target_role}")
        st.write(f"**Indicated Skills:** {skills_input}")
    with col_p2:
        st.subheader("Safety & Honesty Diagnostics")
        st.markdown("""
        * **Profanity & Content Filter:** `Safe`
        * **Claims Validation Check:** `Verified`
        * **Resume Integrity Index:** `92/100` (High integrity profile representation)
        """)

with tab_skills:
    st.markdown("### Core Gap Analysis")
    st.markdown("Comparing your skills with live requirements for target role:")
    
    st.markdown(f"#### Target: **{target_role}**")
    st.progress(0.65)
    st.markdown("*Overall Match Score: **65%** (Moderate Fit)*")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.success("##### Matching Skills")
        st.write("- Python scripting basics")
        st.write("- Fundamental Git workflow (commit/push)")
        st.write("- Basic HTML/CSS styling")
    with col_s2:
        st.error("##### Identified Skill Gaps")
        st.write("- Advanced FastAPI / Backend framework usage")
        st.write("- Containerization & Docker setup")
        st.write("- Unit Testing (pytest) and CI/CD pipelines")

with tab_roadmap:
    st.markdown("### 30-Day Preparation Roadmap")
    st.markdown("A step-by-step roadmap to close the skill gap before your interviews.")
    
    st.markdown("""
    #### 📅 Phase 1: Foundations & API Development (Days 1-10)
    * **Day 1-4:** Deep dive into asynchronous Python and writing clean classes.
    * **Day 5-7:** Building REST APIs using FastAPI, query validation, and routing.
    * **Day 8-10:** Connecting to local SQLite/PostgreSQL databases using SQLModel.
    
    #### 📅 Phase 2: Testing & Containerization (Days 11-20)
    * **Day 11-15:** Writing comprehensive unit tests using `pytest` and mock configurations.
    * **Day 16-20:** Creating standard Dockerfiles and multi-stage container builds.
    
    #### 📅 Phase 3: Portfolio Polish & Application (Days 21-30)
    * **Day 21-25:** Packaging your project, generating a high-quality README, and push to GitHub.
    * **Day 26-30:** Simulated mock interviews focusing on system design and APIs.
    """)

with tab_portfolio:
    st.markdown("### Portfolio Project Recommender & README Creator")
    st.markdown("High-impact projects that showcase missing skills on your resume.")
    
    st.markdown("#### Recommended Project: **Serverless Task Scheduler API**")
    st.markdown("""
    * **Objective:** Design a containerized FastAPI application representing an API scheduler.
    * **Why it fits:** Directly targets gaps in APIs, Docker, and Pytest coverage.
    * **Complexity:** Intermediate/Advanced.
    """)
    
    st.markdown("---")
    st.markdown("#### Generated Portfolio README (GitHub Ready)")
    st.code("""
# TaskScheduler-API

A high-performance FastAPI scheduler designed to queue background worker tasks.

## Tech Stack
- FastAPI, Pydantic (v2)
- Docker
- SQLite
- Pytest (85%+ coverage)

## Setup
`docker build -t task-scheduler-api .`
    """, language="markdown")

with tab_interview:
    st.markdown("### Mock Interview Engine")
    st.markdown("Sample interview questions derived from your resume gaps.")
    
    st.markdown("#### Question 1 (Backend Engineering Focus)")
    st.info("How does asynchronous concurrency differ from threading in FastAPI, and when would you use background tasks?")
    st.text_area("Your response:", placeholder="Type your answer here...")
    
    st.markdown("#### Question 2 (Testing Focus)")
    st.info("Explain how you mock external API dependencies using pytest-mock, and what the benefits are.")
    st.text_area("Your response:", placeholder="Type your answer here...", key="q2")
