"""
Basic test runner for AgentOrchestrator. This creates a sample SDE-1 job
description and runs the orchestrator to produce and print a roadmap JSON.

Note: To run this locally you need to install packages from requirements.txt
and set GOOGLE_API_KEY in a `.env` file if you want live research/LLM features.
"""
from research_agent import AgentOrchestrator, save_roadmap

SAMPLE_JD = '''
We are looking for a Software Development Engineer I. You will work on backend services and APIs.
Requirements:
- Strong programming skills in Python or Java
- Data Structures and Algorithms experience (arrays, hashing, dynamic programming)
- Experience building REST APIs and microservices
- Familiarity with AWS (S3, EC2), Docker, and CI/CD
- Good communication and collaboration skills
'''

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    roadmap = orchestrator.run(company="Google", role="SDE-1", jd_text=SAMPLE_JD)
    print("Roadmap summary:\n")
    print(roadmap)
    path = save_roadmap(roadmap, "Google", "SDE-1")
    print(f"Saved sample roadmap to: {path}")
