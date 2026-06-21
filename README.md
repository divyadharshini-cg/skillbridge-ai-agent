# SkillBridge AI: Multi-Agent Internship Readiness Coach

SkillBridge AI is a multi-agent system designed to coach college students toward internship readiness. This project is developed as a capstone submission for the Kaggle AI Agents Intensive Vibe Coding Hackathon.

## Features

- **Profile Analyzer Agent**: Parses resumes and student profiles.
- **Skill Gap Agent**: Cross-references profiles with standard industry requirements.
- **Internship Match Agent**: Rates internship fit and compatibility.
- **Roadmap Agent**: Generates tailored 30-day learning and readiness roadmaps.
- **Portfolio Project Agent**: Suggests dynamic, high-impact projects.
- **Readme Agent**: Generates custom project READMEs to beef up portfolios.
- **Interview Agent**: Serves mock interview questions based on targeted roles.
- **Safety Agent**: Checks resume safety and ensures honesty check on profile details.
- **Evaluation Agent**: Evaluates progress and grades overall preparedness.
- **Coordinator Agent**: Oversees and schedules execution across the entire coaching pipeline.

## Setup Instructions

1. **Clone/Open the repository**:
   Ensure you are in the project folder.

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Add your API key:
   ```
   GOOGLE_API_KEY=your_actual_gemini_api_key
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

6. **Run Tests**:
   ```bash
   pytest
   ```
