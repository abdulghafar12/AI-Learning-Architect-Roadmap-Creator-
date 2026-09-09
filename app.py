# AI Learning Architect — Streamlit application

import html
import json
import os
import streamlit as st
from groq import Groq


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Learning Architect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GROQ CLIENT
# ============================================================


def get_groq_api_key():
    """Read the Groq key from Streamlit secrets or an environment variable."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None

    return key or os.getenv("GROQ_API_KEY")


api_key = get_groq_api_key()

if not api_key:
    st.error(
        "GROQ_API_KEY is not configured. Add it to Streamlit secrets "
        "or set it as an environment variable before running the app."
    )
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# ROADMAP VALIDATION
# ============================================================

def validate_roadmap(data):

    required_fields = [
        "domain",
        "level",
        "goal",
        "available_time",
        "deadline",
        "overview",
        "phases",
        "projects",
        "skills_to_master",
        "topics_to_postpone",
        "final_advice"
    ]

    # Check that the main object is a dictionary
    if not isinstance(data, dict):
        return False, "Roadmap is not a dictionary."

    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    # Check data types
    if not isinstance(data["phases"], list):
        return False, "'phases' must be a list."

    if not isinstance(data["projects"], list):
        return False, "'projects' must be a list."

    if not isinstance(data["skills_to_master"], list):
        return False, "'skills_to_master' must be a list."

    if not isinstance(data["topics_to_postpone"], list):
        return False, "'topics_to_postpone' must be a list."

    # Check phases
    for phase in data["phases"]:

        if not isinstance(phase, dict):
            return False, "Each phase must be a dictionary."

        phase_fields = [
            "phase_number",
            "phase_name",
            "description",
            "estimated_duration",
            "topics"
        ]

        for field in phase_fields:
            if field not in phase:
                return False, f"Phase is missing field: {field}"

        if not isinstance(phase["topics"], list):
            return False, "Phase topics must be a list."

        # Check topics
        for topic in phase["topics"]:

            if not isinstance(topic, dict):
                return False, "Each topic must be a dictionary."

            topic_fields = [
                "topic_name",
                "importance",
                "estimated_time",
                "why_learn",
                "prerequisites",
                "practice"
            ]

            for field in topic_fields:
                if field not in topic:
                    return False, f"Topic is missing field: {field}"

            if not isinstance(topic["prerequisites"], list):
                return False, "Topic prerequisites must be a list."

            if not isinstance(topic["practice"], list):
                return False, "Topic practice must be a list."

    return True, "Roadmap structure is valid."


# ============================================================
# AI ROADMAP GENERATION
# ============================================================

def generate_roadmap(domain, level, goal, available_time, deadline):

    prompt = f"""
Create a personalized learning roadmap.

Student:
- Domain: {domain}
- Level: {level}
- Goal: {goal}
- Available time: {available_time}
- Deadline: {deadline}

Return ONLY valid JSON.

The JSON MUST have exactly these top-level fields:

domain
level
goal
available_time
deadline
overview
phases
projects
skills_to_master
topics_to_postpone
final_advice

Structure:

phases:
[
  {{
    "phase_number": 1,
    "phase_name": "...",
    "description": "...",
    "estimated_duration": "...",
    "topics": [
      {{
        "topic_name": "...",
        "importance": "high",
        "estimated_time": "...",
        "why_learn": "...",
        "prerequisites": [],
        "practice": []
      }}
    ]
  }}
]

projects:
[
  {{
    "project_name": "...",
    "difficulty": "beginner",
    "description": "...",
    "skills_practiced": []
  }}
]

topics_to_postpone:
[
  {{
    "topic": "...",
    "reason": "..."
  }}
]

Rules:
- Create 3 to 5 phases.
- Keep the roadmap concise.
- Make it realistic for the deadline.
- Keep topic descriptions short.
- Include practical exercises.
- Include useful projects.
- importance must be high, medium, or low.
- difficulty must be beginner, intermediate, or advanced.
- Return valid JSON only.
- Do not use markdown.
- Do not add explanations outside JSON.
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": """
You are an expert learning curriculum designer.

Return ONLY valid JSON.
Follow the requested structure exactly.
Do not use markdown.
Do not add text outside the JSON object.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        },

        max_completion_tokens=3000,

        reasoning_effort="low"
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    roadmap = json.loads(content)

    if not isinstance(roadmap, dict):
        raise ValueError("AI returned an invalid roadmap.")

    # Normalize importance
    for phase in roadmap.get("phases", []):
        for topic in phase.get("topics", []):

            importance = str(
                topic.get("importance", "medium")
            ).lower().strip()

            if importance not in ["high", "medium", "low"]:
                importance = "medium"

            topic["importance"] = importance

    # Normalize difficulty
    for project in roadmap.get("projects", []):

        difficulty = str(
            project.get("difficulty", "beginner")
        ).lower().strip()

        if difficulty not in [
            "beginner",
            "intermediate",
            "advanced"
        ]:
            difficulty = "beginner"

        project["difficulty"] = difficulty

    return roadmap


# ============================================================
# DASHBOARD RENDERER
# ============================================================

def render_dashboard(roadmap):

    # =========================
    # DASHBOARD DATA
    # =========================

    total_topics = sum(
        len(phase["topics"])
        for phase in roadmap["phases"]
    )

    total_projects = len(roadmap["projects"])
    total_phases = len(roadmap["phases"])
    total_skills = len(roadmap["skills_to_master"])


    # =========================
    # PHASES + TOPICS
    # =========================

    phases_html = ""

    for phase in roadmap["phases"]:

        topics_html = ""

        for topic in phase["topics"]:

            importance = topic["importance"].lower()

            if importance == "high":
                badge_class = "high"
                icon = "🔥"

            elif importance == "medium":
                badge_class = "medium"
                icon = "⭐"

            else:
                badge_class = "low"
                icon = "💡"


            practice_html = "".join(
                f"<li>{practice}</li>"
                for practice in topic["practice"]
            )


            topics_html += f"""
            <div class="topic-card">

                <div class="topic-header">

                    <div class="topic-title-area">

                        <div class="topic-name">
                            {topic["topic_name"]}
                        </div>

                        <div class="topic-meta">
                            ⏱ {topic["estimated_time"]}
                        </div>

                    </div>

                    <span class="badge {badge_class}">
                        {icon} {topic["importance"].title()}
                    </span>

                </div>


                <div class="why">

                    <strong>Why learn this?</strong>

                    <p>
                        {topic["why_learn"]}
                    </p>

                </div>


                <div class="practice">

                    <strong>Practice</strong>

                    <ul>
                        {practice_html}
                    </ul>

                </div>

            </div>
            """


        phases_html += f"""
        <div class="phase-card">

            <div class="phase-number">
                {phase["phase_number"]}
            </div>


            <div class="phase-content">

                <div class="phase-title-row">

                    <div class="phase-heading-area">

                        <h2>
                            {phase["phase_name"]}
                        </h2>

                        <p>
                            {phase["description"]}
                        </p>

                    </div>


                    <span class="duration">
                        {phase["estimated_duration"]}
                    </span>

                </div>


                {topics_html}

            </div>

        </div>
        """


    # =========================
    # PROJECTS
    # =========================

    projects_html = ""

    project_icons = [
        "🏠",
        "🌸",
        "🚀",
        "💻",
        "📊"
    ]


    for i, project in enumerate(roadmap["projects"]):

        icon = project_icons[
            i % len(project_icons)
        ]

        skills = " • ".join(
            project["skills_practiced"]
        )


        projects_html += f"""
        <div class="project-card">

            <div class="project-icon">
                {icon}
            </div>


            <div class="project-content">

                <h3>
                    {project["project_name"]}
                </h3>


                <span class="project-level">
                    {project["difficulty"].title()}
                </span>


                <p>
                    {project["description"]}
                </p>


                <small>
                    {skills}
                </small>

            </div>

        </div>
        """


    # =========================
    # SKILLS
    # =========================

    skills_html = ""

    for skill in roadmap["skills_to_master"]:

        skills_html += f"""
        <span class="skill">
            ✓ {skill}
        </span>
        """


    # =========================
    # POSTPONED TOPICS
    # =========================

    postponed_html = ""

    for item in roadmap["topics_to_postpone"]:

        postponed_html += f"""
        <div class="postponed">

            <strong>
                ⏸ {item["topic"]}
            </strong>

            <p>
                {item["reason"]}
            </p>

        </div>
        """


    # =========================
    # COMPLETE HTML
    # =========================

    html = f"""

    <style>

        /* ==========================================
           GLOBAL
        ========================================== */

        * {{
            box-sizing: border-box !important;
        }}


        .dashboard {{
            font-family:
                Inter,
                Arial,
                Helvetica,
                sans-serif !important;

            background: #f7f7f7 !important;

            color: #202020 !important;

            padding: 30px !important;

            border-radius: 20px !important;

            line-height: 1.5 !important;
        }}


        /* ==========================================
           UNIVERSAL TEXT RULE
        ========================================== */

        .dashboard div,
        .dashboard span,
        .dashboard p,
        .dashboard li,
        .dashboard small,
        .dashboard strong {{
            color: #202020 !important;
        }}


        /* ==========================================
           UNIVERSAL CARD BORDER
        ========================================== */

        .dashboard .hero,
        .dashboard .stat,
        .dashboard .phase-card,
        .dashboard .topic-card,
        .dashboard .project-card,
        .dashboard .skill,
        .dashboard .info-card,
        .dashboard .postponed,
        .dashboard .topic-header,
        .dashboard .phase-content,
        .dashboard .project-content {{
            border-color: #8B0000 !important;
        }}


        /* ==========================================
           HERO
        ========================================== */

        .dashboard .hero {{
            background:
                linear-gradient(
                    135deg,
                    #171717,
                    #303030
                ) !important;

            color: #ffffff !important;

            padding: 35px !important;

            border-radius: 22px !important;

            border: 0.1px solid #8B0000 !important;

            margin-bottom: 24px !important;
        }}


        .dashboard .hero * {{
            color: #ffffff !important;
        }}


        .dashboard .hero .hero-label {{
            color: #d9a3a3 !important;

            font-size: 13px !important;

            font-weight: 700 !important;

            letter-spacing: 1.2px !important;

            text-transform: uppercase !important;
        }}


        .dashboard .hero h1 {{
            color: #ffffff !important;

            font-size: 38px !important;

            line-height: 1.15 !important;

            margin: 10px 0 14px 0 !important;

            font-weight: 800 !important;
        }}


        .dashboard .hero p {{
            color: #eeeeee !important;

            max-width: 800px !important;

            line-height: 1.7 !important;

            margin: 0 !important;
        }}


        /* ==========================================
           HERO TAGS
        ========================================== */

        .dashboard .tags {{
            display: flex !important;

            flex-wrap: wrap !important;

            gap: 10px !important;

            margin-top: 22px !important;
        }}


        .dashboard .tag {{
            background: #242424 !important;

            color: #ffffff !important;

            border: 0.1px solid #8B0000 !important;

            padding: 8px 14px !important;

            border-radius: 999px !important;

            font-size: 13px !important;
        }}


        .dashboard .tag * {{
            color: #ffffff !important;
        }}


        /* ==========================================
           SECTION HEADINGS
        ========================================== */

        .dashboard .section-title {{
            color: #2563EB !important;

            font-size: 23px !important;

            font-weight: 800 !important;

            margin: 32px 0 16px 0 !important;

            line-height: 1.3 !important;
        }}


        /* ==========================================
           STATS
        ========================================== */

        .dashboard .stats {{
            display: grid !important;

            grid-template-columns:
                repeat(4, minmax(0, 1fr)) !important;

            gap: 16px !important;

            margin-bottom: 24px !important;
        }}


        .dashboard .stat {{
            background: #ffffff !important;

            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 18px !important;

            padding: 22px !important;
        }}


        .dashboard .stat-icon {{
            color: #8B0000 !important;

            font-size: 24px !important;
        }}


        .dashboard .stat-number {{
            color: #8B0000 !important;

            font-size: 29px !important;

            font-weight: 800 !important;

            margin-top: 8px !important;
        }}


        .dashboard .stat-label {{
            color: #202020 !important;

            font-size: 13px !important;

            font-weight: 600 !important;

            margin-top: 4px !important;
        }}


        /* ==========================================
           PHASE CARD
        ========================================== */

        .dashboard .phase-card {{
            display: flex !important;

            gap: 18px !important;

            background: #ffffff !important;

            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 20px !important;

            padding: 22px !important;

            margin-bottom: 18px !important;
        }}


        .dashboard .phase-number {{
            min-width: 42px !important;

            height: 42px !important;

            border-radius: 50% !important;

            background: #8B0000 !important;

            color: #ffffff !important;

            border: 0.1px solid #8B0000 !important;

            display: flex !important;

            align-items: center !important;

            justify-content: center !important;

            font-weight: 800 !important;

            flex-shrink: 0 !important;
        }}


        .dashboard .phase-number {{
            color: #ffffff !important;
        }}


        .dashboard .phase-content {{
            flex: 1 !important;

            color: #202020 !important;
        }}


        .dashboard .phase-title-row {{
            display: flex !important;

            justify-content:
                space-between !important;

            gap: 15px !important;

            align-items:
                flex-start !important;
        }}


        .dashboard .phase-heading-area {{
            flex: 1 !important;
        }}


        .dashboard .phase-title-row h2 {{
            color: #0F172A;  !important;

            margin: 0 !important;

            font-size: 21px !important;

            font-weight: 800 !important;
        }}


        .dashboard .phase-title-row p {{
            color: #202020 !important;

            line-height: 1.6 !important;

            margin: 8px 0 0 0 !important;
        }}


        .dashboard .duration {{
            background: #f4eaea !important;

            color: #2563EB !important;

            border:
                0.1px solid #8B0000 !important;

            padding: 7px 12px !important;

            border-radius: 999px !important;

            font-size: 12px !important;

            font-weight: 700 !important;

            white-space: nowrap !important;
        }}


        /* ==========================================
           TOPIC CARD
        ========================================== */

        .dashboard .topic-card {{
            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 12px !important;

            padding: 18px !important;

            margin-top: 14px !important;

            background: #fcfcfc !important;
        }}


        .dashboard .topic-header {{
            display: flex !important;

            justify-content:
                space-between !important;

            gap: 15px !important;

            align-items:
                center !important;

            border: 0 !important;
        }}


        .dashboard .topic-title-area {{
            flex: 1 !important;
        }}


        .dashboard .topic-name {{
            color: #2563EB !important;

            font-weight: 800 !important;

            font-size: 16px !important;
        }}


        .dashboard .topic-meta {{
            color: #202020 !important;

            font-size: 12px !important;

            margin-top: 5px !important;
        }}


        /* ==========================================
           IMPORTANCE BADGES
        ========================================== */

        .dashboard .badge {{
            padding: 6px 10px !important;

            border-radius: 8px !important;

            font-size: 11px !important;

            font-weight: 700 !important;

            white-space: nowrap !important;

            border: 0.1px solid #8B0000 !important;
        }}


        .dashboard .badge.high {{
            background: #f9e6e6 !important;

            color: #2563EB !important;
        }}


        .dashboard .badge.medium {{
            background: #f9f0df !important;

            color: #8B0000 !important;
        }}


        .dashboard .badge.low {{
            background: #eeeeee !important;

            color: #2563EB; !important;
        }}


        .dashboard .badge.high,
        .dashboard .badge.medium,
        .dashboard .badge.low {{
            color: #2563EB !important;
        }}


        /* ==========================================
           WHY LEARN
        ========================================== */

        .dashboard .why {{
            margin-top: 14px !important;

            color: #202020 !important;

            font-size: 13px !important;
        }}


        .dashboard .why strong {{
            color: #8B0000 !important;

            font-weight: 800 !important;
        }}


        .dashboard .why p {{
            color: #202020 !important;

            margin: 5px 0 !important;

            line-height: 1.6 !important;
        }}


        /* ==========================================
           PRACTICE
        ========================================== */

        .dashboard .practice {{
            margin-top: 12px !important;

            color: #202020 !important;

            font-size: 13px !important;
        }}


        .dashboard .practice strong {{
            color: #0F172A;  !important;

            font-weight: 800 !important;
        }}


        .dashboard .practice ul {{
            margin-top: 7px !important;

            padding-left: 22px !important;

            color: #202020 !important;
        }}


        .dashboard .practice li {{
            color: #202020 !important;

            margin-bottom: 6px !important;
        }}


        /* ==========================================
           PROJECTS
        ========================================== */

        .dashboard .projects {{
            display: grid !important;

            grid-template-columns:
                repeat(2, minmax(0, 1fr)) !important;

            gap: 16px !important;
        }}


        .dashboard .project-card {{
            background: #ffffff !important;

            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 18px !important;

            padding: 20px !important;

            display: flex !important;

            gap: 15px !important;
        }}


        .dashboard .project-icon {{
            width: 55px !important;

            height: 55px !important;

            border-radius: 14px !important;

            background: #f4eaea !important;

            border:
                0.1px solid #8B0000 !important;

            display: flex !important;

            align-items: center !important;

            justify-content: center !important;

            font-size: 27px !important;

            flex-shrink: 0 !important;
        }}


        .dashboard .project-content {{
            flex: 1 !important;

            color: #202020 !important;
        }}


        .dashboard .project-card h3 {{
            color: #2563EB !important;

            margin: 0 0 8px 0 !important;

            font-size: 18px !important;

            font-weight: 800 !important;
        }}


        .dashboard .project-level {{
            background: #f4eaea !important;

            color: #0F172A;  !important;

            border:
                0.1px solid #8B0000 !important;

            padding: 4px 8px !important;

            border-radius: 6px !important;

            font-size: 10px !important;

            font-weight: 700 !important;
        }}


        .dashboard .project-card p {{
            color: #202020 !important;

            font-size: 13px !important;

            line-height: 1.6 !important;
        }}


        .dashboard .project-card small {{
            color: #202020 !important;

            font-size: 11px !important;
        }}


        /* ==========================================
           SKILLS
        ========================================== */

        .dashboard .skills {{
            display: flex !important;

            flex-wrap: wrap !important;

            gap: 9px !important;
        }}


        .dashboard .skill {{
            background: #ffffff !important;

            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            padding: 9px 13px !important;

            border-radius: 10px !important;

            font-size: 12px !important;

            font-weight: 600 !important;
        }}


        .dashboard .skill {{
            color: #202020 !important;
        }}


        /* ==========================================
           BOTTOM GRID
        ========================================== */

        .dashboard .bottom-grid {{
            display: grid !important;

            grid-template-columns:
                repeat(2, minmax(0, 1fr)) !important;

            gap: 18px !important;

            margin-top: 20px !important;
        }}


        .dashboard .info-card {{
            background: #ffffff !important;

            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 20px !important;

            padding: 24px !important;
        }}


        .dashboard .info-card h2 {{
            color: #0F172A;  !important;

            margin-top: 0 !important;

            font-size: 20px !important;

            font-weight: 800 !important;
        }}


        /* ==========================================
           POSTPONED TOPICS
        ========================================== */

        .dashboard .postponed {{
            color: #202020 !important;

            border:
                0.1px solid #8B0000 !important;

            border-radius: 10px !important;

            padding: 12px !important;

            margin-top: 10px !important;

            background: #fcfcfc !important;
        }}


        .dashboard .postponed strong {{
            color: #0F172A;  !important;

            font-weight: 800 !important;
        }}


        .dashboard .postponed p {{
            color: #202020 !important;

            font-size: 13px !important;

            line-height: 1.6 !important;

            margin-bottom: 0 !important;
        }}


        /* ==========================================
           AI ADVICE
        ========================================== */

        .dashboard .advice {{
            background: #f8eeee !important;

            color: #100020 !important;

            border:
                0.1px solid #8B0000 !important;
        }}


        .dashboard .advice h2 {{
            color: #0F172A;  !important;

            font-weight: 800 !important;
        }}


        .dashboard .advice p {{
            color: #102000 !important;

            line-height: 1.8 !important;

            font-size: 14px !important;
        }}


        /* ==========================================
           RESPONSIVE
        ========================================== */

        @media (max-width: 800px) {{

            .dashboard {{
                padding: 15px !important;
            }}


            .dashboard .stats {{
                grid-template-columns:
                    repeat(2, 1fr) !important;
            }}


            .dashboard .projects,
            .dashboard .bottom-grid {{
                grid-template-columns: 1fr !important;
            }}


            .dashboard .hero h1 {{
                font-size: 28px !important;
            }}


            .dashboard .phase-card {{
                flex-direction: column !important;
            }}


            .dashboard .phase-title-row {{
                flex-direction: column !important;
            }}


            .dashboard .topic-header {{
                align-items: flex-start !important;
            }}

        }}

    </style>


    <div class="dashboard">


        <!-- =========================
             HERO
        ========================== -->

        <div class="hero">

            <div class="hero-label">
                Your Learning Roadmap
            </div>


            <h1>
                {roadmap["domain"].title()}
            </h1>


            <p>
                {roadmap["overview"]}
            </p>


            <div class="tags">

                <span class="tag">
                    🎓 {roadmap["level"].title()} Level
                </span>


                <span class="tag">
                    ⏱ {roadmap["available_time"]}
                </span>


                <span class="tag">
                    📅 {roadmap["deadline"]}
                </span>

            </div>

        </div>


        <!-- =========================
             STATISTICS
        ========================== -->

        <div class="stats">


            <div class="stat">

                <div class="stat-icon">
                    📚
                </div>

                <div class="stat-number">
                    {total_phases}
                </div>

                <div class="stat-label">
                    Learning Phases
                </div>

            </div>


            <div class="stat">

                <div class="stat-icon">
                    📖
                </div>

                <div class="stat-number">
                    {total_topics}
                </div>

                <div class="stat-label">
                    Topics
                </div>

            </div>


            <div class="stat">

                <div class="stat-icon">
                    🚀
                </div>

                <div class="stat-number">
                    {total_projects}
                </div>

                <div class="stat-label">
                    Hands-on Projects
                </div>

            </div>


            <div class="stat">

                <div class="stat-icon">
                    🎯
                </div>

                <div class="stat-number">
                    {total_skills}
                </div>

                <div class="stat-label">
                    Skills to Master
                </div>

            </div>


        </div>


        <!-- =========================
             LEARNING JOURNEY
        ========================== -->

        <h2 class="section-title">
            🗺️ Your Learning Journey
        </h2>


        {phases_html}


        <!-- =========================
             PROJECTS
        ========================== -->

        <h2 class="section-title">
            🚀 Hands-on Projects
        </h2>


        <div class="projects">

            {projects_html}

        </div>


        <!-- =========================
             SKILLS
        ========================== -->

        <h2 class="section-title">
            🎯 Skills You'll Master
        </h2>


        <div class="skills">

            {skills_html}

        </div>


        <!-- =========================
             BOTTOM INFORMATION
        ========================== -->

        <div class="bottom-grid">


            <div class="info-card">

                <h2>
                    ⏸️ Topics to Postpone
                </h2>

                {postponed_html}

            </div>


            <div class="info-card advice">

                <h2>
                    💡 AI Advice
                </h2>

                <p>
                    {roadmap["final_advice"]}
                </p>

            </div>


        </div>


    </div>

    """

    return html


# ==========================================
# GRADIO DASHBOARD
# ==========================================


# ============================================================
# STREAMLIT UI
# ============================================================


st.markdown(
    """
    <div class="app-title">
        <h1>🎓 AI Learning Architect</h1>
        <p>Build a personalized learning roadmap powered by AI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.container():
    st.markdown(
        """
        <div class="input-panel">
            <h2>🧑‍🎓 Tell us about your learning goal</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        domain_input = st.text_input(
            "📚 Domain / Subject",
            placeholder="Example: Machine Learning",
        )

    with col2:
        level_input = st.selectbox(
            "🎯 Current Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=0,
        )

    goal_input = st.text_area(
        "🚀 Learning Goal",
        placeholder=(
            "Example: Reach intermediate level and build practical projects"
        ),
        height=100,
    )

    col3, col4 = st.columns(2)

    with col3:
        available_time_input = st.text_input(
            "⏱ Available Time",
            placeholder="Example: 4 hours per day",
        )

    with col4:
        deadline_input = st.text_input(
            "📅 Deadline",
            placeholder="Example: 60 days",
        )

    generate_button = st.button(
        "🚀 Generate My Roadmap",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# GENERATE + RENDER
# ============================================================

if generate_button:
    domain = str(domain_input).strip()
    goal = str(goal_input).strip()
    available_time = str(available_time_input).strip()
    deadline = str(deadline_input).strip()

    if not domain:
        st.warning("Please enter the subject or domain you want to learn.")
        st.stop()

    if not goal:
        st.warning("Please describe your learning goal.")
        st.stop()

    if not available_time:
        st.warning("Please enter how much time you can study.")
        st.stop()

    if not deadline:
        st.warning("Please enter your target deadline.")
        st.stop()

    if available_time.isdigit():
        available_time = f"{available_time} hours per day"

    if deadline.isdigit():
        deadline = f"{deadline} days"

    try:
        with st.spinner("Generating your personalized roadmap..."):
            roadmap = generate_roadmap(
                domain=domain,
                level=level_input,
                goal=goal,
                available_time=available_time,
                deadline=deadline,
            )

        valid, message = validate_roadmap(roadmap)

        if not valid:
            raise ValueError(message)

        st.session_state["roadmap"] = roadmap
        st.session_state["generation_inputs"] = {
            "domain": domain,
            "level": level_input,
            "goal": goal,
            "available_time": available_time,
            "deadline": deadline,
        }

    except Exception as exc:
        st.error("Roadmap generation failed.")
        st.exception(exc)


# ============================================================
# OUTPUT
# ============================================================

roadmap = st.session_state.get("roadmap")

if roadmap:
    st.markdown("## 🗺️ Your Personalized Roadmap")
    dashboard_html = render_dashboard(roadmap)
    st.markdown(dashboard_html, unsafe_allow_html=True)
else:
    st.markdown("## 🗺️ Your Personalized Roadmap")
    st.markdown(
        """
        <div class="dashboard-container empty-state">
            <div class="empty-icon">🧠</div>
            <h3>Your roadmap is waiting</h3>
            <p>Enter your learning details above and click Generate My Roadmap.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="footer-text">
        AI Learning Architect • Personalized learning, structured by AI.
    </div>
    """,
    unsafe_allow_html=True,
)
