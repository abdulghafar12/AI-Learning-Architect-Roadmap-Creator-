# 🎓 AI Learning Architect

An AI-powered personalized learning roadmap generator built with **Streamlit** and **Groq**.

## Features

- Personalized roadmap generation
- Beginner / Intermediate / Advanced levels
- Deadline-aware planning
- Time-aware study planning
- 3–5 learning phases
- Topics with importance, estimated time, rationale, and practice
- Hands-on projects
- Skills to master
- Topics to postpone
- Final learning advice
- Responsive dashboard-style presentation
- No PDF/download functionality

## Project structure

```text
AI-Learning-Architect/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── W2-_Ai_Learning_Architect.ipynb
```

## 1. Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Groq API key. On Windows PowerShell:

```powershell
$env:GROQ_API_KEY="YOUR_API_KEY"
```

On Linux/macOS:

```bash
export GROQ_API_KEY="YOUR_API_KEY"
```

Then run:

```bash
streamlit run app.py
```

## 2. Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, `.gitignore`, `README.md`, and optionally the notebook to GitHub.
2. Create a new app in Streamlit Community Cloud.
3. Select your GitHub repository and branch.
4. Set the main file to `app.py`.
5. In the app's **Secrets** settings, add:

```toml
GROQ_API_KEY = "YOUR_API_KEY"
```

6. Deploy the app.

**Never commit your API key to GitHub.** The `.gitignore` already excludes `.streamlit/secrets.toml`.

## 3. Colab notebook

`W2-_Ai_Learning_Architect.ipynb` is retained as the original development/notebook version. The deployable Streamlit application is `app.py`.

## Notes

The Streamlit version keeps the roadmap-generation prompt and dashboard renderer from the project while replacing the Gradio event system with Streamlit's execution model. PDF generation, PDF dependencies, download buttons, and Gradio launch code are intentionally excluded from the deployment app.
