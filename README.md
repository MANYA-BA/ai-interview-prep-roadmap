> 📝 **Submission for:** Isaii GenAI Internship - Technical Task
> 📅 **Date:** 28-10-2025
> 👤 **Candidate:** Manya B A

# AI Interview Preparation Roadmap Generator

This project generates a structured interview preparation roadmap for a given company, role, and job description using a small multi-agent system.

## Overview

The tool combines three agents:
- JDParserAgent: Extracts key skills and maps them to high-level topics using a keyword mapping.
- InterviewResearchAgent: Uses DuckDuckGo to infer common interview rounds and estimated difficulty.
- RoadmapBuilderAgent: Combines the parsed JD and interview research into a JSON roadmap with recommended study order and a crude timeline.

An `AgentOrchestrator` wires the agents together and optionally initializes the Gemini (Google Generative AI) LLM for enhanced prompts/reasoning.

## Project structure

- `research_agent.py` - Main multi-agent implementation and CLI
- `config.py` - Loads `GOOGLE_API_KEY` from `.env`
- `test_run.py` - Example runner with a sample SDE-1 job description
- `requirements.txt` - Python dependencies
- `.env.example` - Template for environment variables
- `README.md` - This document

## Installation

1. Create and activate a Python 3.9+ virtual environment.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Google Gemini API key if you want LLM-assisted features:

```text
GOOGLE_API_KEY=AIza...your_key_here
```

## Getting a Gemini / Google Generative AI API Key

1. Visit https://ai.google.dev or Google AI Studio and sign in.
2. Create an API key in the credentials or API Keys section.
3. Add the key to your `.env` file as `GOOGLE_API_KEY`.

Note: Google may change how API keys are issued; consult their docs if the steps differ.

## Usage

CLI example:

```powershell
python research_agent.py --company "Google" --role "SDE-1" --jd "path/to/jd.txt"
```

Or provide the JD as a string:

```powershell
python research_agent.py --company "Acme" --role "Backend Engineer" --jd "Experienced in REST APIs, Python, and AWS"
```

Python import example:

```python
from research_agent import AgentOrchestrator
orchestrator = AgentOrchestrator()
roadmap = orchestrator.run("Acme", "Backend Engineer", "JD text here")
print(roadmap)
```

## Web UI (Streamlit)

A simple local web UI is provided using Streamlit. It allows you to paste or upload a job description, set company and role, then generate and download the roadmap JSON.

Run the Streamlit app:

```powershell
streamlit run app.py
```

The UI will open in your browser (or show a local URL). After generating, the JSON is shown on-screen and a download button is provided. The roadmap is also saved to the `output/` directory with a timestamp.

## Example output format

```json
{
  "company": "string",
  "role": "string",
  "rounds": [
    {"type": "string", "topics": ["string"], "estimated_prep_time": "string"}
  ],
  "difficulty": "Easy/Medium/Hard",
  "recommended_order": ["DSA", "System Design", "Backend"],
  "key_skills": ["python", "rest api", "aws"],
  "preparation_timeline": "1-3 months"
}
```

## Notes & Next steps

- This implementation uses keyword heuristics and DuckDuckGo scraping; it's intentionally lightweight.
- For better topic extraction consider adding an NLP parser (spaCy, HuggingFace) or LLM prompts.
- For richer interview research, integrate other sources (Glassdoor, Blind) and rate trustworthiness.

## License

MIT
