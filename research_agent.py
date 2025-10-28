import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# External search and AI packages
import duckduckgo_search
import langchain
import langchain_google_genai
import google.generativeai as genai

"""
AI Interview Preparation Roadmap Generator

This module implements a small multi-agent system:
- JDParserAgent: extracts skills/tools from a job description and maps to topics
- InterviewResearchAgent: researches interview structure via DuckDuckGo
- RoadmapBuilderAgent: combines inputs into a JSON roadmap
- AgentOrchestrator: wires everything together and saves output

Note: This script uses the Gemini / Google Generative AI key configured via
`GOOGLE_API_KEY` (see `config.py` and `.env.example`). The actual LLM calls
are optional for offline use — the orchestration and heuristics work without
live LLM queries.
"""

load_dotenv()

from config import GOOGLE_API_KEY

# Keyword mapping: maps common JD keywords to high-level topics
KEYWORD_MAPPING = {
    "rest api": "Backend",
    "restful api": "Backend",
    "http": "Backend",
    "api": "Backend",
    "microservice": "Backend",
    "microservices": "Backend",
    "react": "Frontend",
    "vue": "Frontend",
    "angular": "Frontend",
    "javascript": "Frontend",
    "typescript": "Frontend",
    "python": "Programming",
    "java": "Programming",
    "c++": "Programming",
    "c#": "Programming",
    "data structures": "DSA",
    "algorithms": "DSA",
    "arrays": "DSA",
    "linked list": "DSA",
    "dp": "DSA",
    "dynamic programming": "DSA",
    "system design": "System Design",
    "scalability": "System Design",
    "distributed systems": "System Design",
    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "ci/cd": "DevOps",
    "sql": "Databases",
    "postgres": "Databases",
    "nosql": "Databases",
    "mongodb": "Databases",
    "machine learning": "ML",
    "nlp": "ML",
    "testing": "Quality",
    "unit test": "Quality",
    "pytest": "Quality",
}


class JDParserAgent:
    """Parse a job description and extract skills/tools mapped to topics."""

    def __init__(self, keyword_mapping=None):
        self.keyword_mapping = keyword_mapping or KEYWORD_MAPPING

    def parse(self, jd_text: str) -> dict:
        text = jd_text.lower()
        found_skills = set()
        topics = set()

        # Find explicit keywords
        for kw, topic in self.keyword_mapping.items():
            if kw in text:
                found_skills.add(kw)
                topics.add(topic)

        # Heuristic: look for common single-word skills
        single_word_keywords = [k for k in self.keyword_mapping.keys() if " " not in k]
        for w in single_word_keywords:
            if f"{w}" in text:
                found_skills.add(w)
                topics.add(self.keyword_mapping[w])

        # Fallback: attempt to extract capitalized tokens (simple heuristic)
        # Not relying on heavy NLP to keep dependencies small
        cap_tokens = [tok for tok in jd_text.split() if tok.istitle() and len(tok) > 1]
        for tok in cap_tokens:
            if tok.lower() in self.keyword_mapping:
                found_skills.add(tok.lower())
                topics.add(self.keyword_mapping[tok.lower()])

        return {
            "key_skills": sorted(found_skills),
            "topics": sorted(topics),
        }


class InterviewResearchAgent:
    """Use DuckDuckGo search to infer interview rounds and difficulty."""

    def __init__(self, max_results=6):
        self.max_results = max_results

    def search(self, company: str, role: str) -> dict:
        query = f"{company} {role} interview process"
        results = []
        try:
            results = duckduckgo_search.ddg(query, max_results=self.max_results) or []
        except Exception:
            # duckduckgo_search may throw in some environments; fallback to empty
            results = []

        snippets = []
        for r in results:
            if isinstance(r, dict):
                snippets.append((r.get("title", ""), r.get("body", "")))
            else:
                snippets.append((str(r), ""))

        rounds = []
        flags = {
            "coding": False,
            "system_design": False,
            "behavioral": False,
            "hr": False,
            "onsite": False,
            "phone": False,
        }

        for title, body in snippets:
            combined = f"{title} {body}".lower()
            if "coding" in combined or "technical" in combined or "leetcode" in combined:
                flags["coding"] = True
            if "system design" in combined or "design" in combined:
                flags["system_design"] = True
            if "behavioral" in combined or "culture" in combined:
                flags["behavioral"] = True
            if "hr" in combined or "recruiter" in combined:
                flags["hr"] = True
            if "onsite" in combined or "onsite" in title:
                flags["onsite"] = True
            if "phone" in combined or "phone screen" in combined:
                flags["phone"] = True

        # Build rounds heuristically
        if flags["phone"]:
            rounds.append({"type": "Phone Screen", "topics": ["Behavioral", "Basic Technical"], "estimated_prep_time": "2-4 hours"})
        if flags["coding"]:
            rounds.append({"type": "Coding/Online Assessment", "topics": ["DSA"], "estimated_prep_time": "2-4 weeks"})
        if flags["system_design"]:
            rounds.append({"type": "System Design", "topics": ["System Design"], "estimated_prep_time": "1-3 weeks"})
        if flags["behavioral"] or flags["hr"]:
            rounds.append({"type": "Behavioral/HR", "topics": ["Behavioral"], "estimated_prep_time": "1-3 days"})

        if not rounds:
            # Generic baseline
            rounds = [
                {"type": "Phone Screen", "topics": ["Basic Technical", "Behavioral"], "estimated_prep_time": "2-4 hours"},
                {"type": "Coding", "topics": ["DSA"], "estimated_prep_time": "2-4 weeks"},
                {"type": "Onsite/System Design", "topics": ["System Design", "Behavioral"], "estimated_prep_time": "1-3 weeks"},
            ]

        # Difficulty heuristic
        difficulty = "Medium"
        if flags["system_design"] and flags["coding"] and flags["onsite"]:
            difficulty = "Hard"
        elif flags["coding"] and not flags["system_design"]:
            difficulty = "Medium"
        elif not flags["coding"]:
            difficulty = "Easy"

        return {"rounds": rounds, "difficulty": difficulty, "raw_snippets": snippets}


class RoadmapBuilderAgent:
    """Combine JD parsing and interview research into a study roadmap."""

    STANDARD_ORDER = ["DSA", "System Design", "Backend", "Frontend", "Cloud", "Databases", "DevOps", "ML", "Quality", "Programming"]

    def build(self, company: str, role: str, parsed_jd: dict, interview_info: dict) -> dict:
        key_skills = parsed_jd.get("key_skills", [])
        topics = parsed_jd.get("topics", [])

        # Merge topics from interview rounds too
        rounds = interview_info.get("rounds", [])

        # Determine recommended order: put detected topics in STANDARD_ORDER precedence
        rank = {t: i for i, t in enumerate(self.STANDARD_ORDER)}
        unique_topics = list({*topics, *(t for r in rounds for t in r.get("topics", []))})
        recommended = sorted(unique_topics, key=lambda x: rank.get(x, len(self.STANDARD_ORDER)))

        # Estimate a preparation timeline (very coarse)
        num_topics = len(recommended)
        if num_topics <= 2:
            timeline = "2-4 weeks"
        elif num_topics <= 5:
            timeline = "1-3 months"
        else:
            timeline = "3-6 months"

        roadmap = {
            "company": company,
            "role": role,
            "rounds": rounds,
            "difficulty": interview_info.get("difficulty", "Medium"),
            "recommended_order": recommended,
            "key_skills": key_skills,
            "preparation_timeline": timeline,
        }

        return roadmap


class AgentOrchestrator:
    """Initialize LLM (Gemini) and run agents sequentially."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GOOGLE_API_KEY
        self._init_llm()
        self.jd_parser = JDParserAgent()
        self.research_agent = InterviewResearchAgent()
        self.builder = RoadmapBuilderAgent()

    def _init_llm(self):
        # Try to configure google.generativeai
        try:
            genai.configure(api_key=self.api_key)
            self.llm = genai
        except Exception:
            # If any failure, set to None; the orchestrator still works offline
            self.llm = None

    def run(self, company: str, role: str, jd_text: str) -> dict:
        parsed = self.jd_parser.parse(jd_text)
        interview_info = self.research_agent.search(company, role)
        roadmap = self.builder.build(company, role, parsed, interview_info)
        return roadmap


def save_roadmap(roadmap: dict, company: str, role: str) -> str:
    safe_company = company.replace(" ", "_") if company else "unknown"
    safe_role = role.replace(" ", "_") if role else "unknown"
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"roadmap_{safe_company}_{safe_role}_{ts}.json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(roadmap, f, indent=2)
    return path


def _read_jd_maybe_path(jd_arg: str) -> str:
    # If jd_arg is a path to an existing file, read it; otherwise treat as literal text
    if os.path.exists(jd_arg) and os.path.isfile(jd_arg):
        with open(jd_arg, "r", encoding="utf-8") as fh:
            return fh.read()
    return jd_arg


def main():
    parser = argparse.ArgumentParser(description="Generate an interview preparation roadmap")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Role name/title")
    parser.add_argument("--jd", required=True, help="Job description text or path to a JD file")
    args = parser.parse_args()

    jd_text = _read_jd_maybe_path(args.jd)

    orchestrator = AgentOrchestrator()
    roadmap = orchestrator.run(args.company, args.role, jd_text)

    out_path = save_roadmap(roadmap, args.company, args.role)
    print(f"Saved roadmap to: {out_path}")


if __name__ == "__main__":
    main()
