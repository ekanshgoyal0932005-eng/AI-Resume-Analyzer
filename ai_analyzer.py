
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def analyze_resume(resume_text, job_description=""):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found. Check your .env file.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert AI resume analyzer and career advisor.

    Analyze the following resume carefully.

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description if job_description else "Not provided"}

    Evaluate:
    1. Resume ATS compatibility score out of 100.
    2. Important skills found in the resume.
    3. Missing or recommended skills.
    4. Resume strengths.
    5. Resume weaknesses.
    6. Actionable improvement suggestions.
    7. Job match percentage (if job description is provided).

    Return ONLY valid JSON with these keys:

    {{
        "ats_score": 0,
        "summary": "",
        "matched_skills": [],
        "missing_skills": [],
        "strengths": [],
        "weaknesses": [],
        "recommendations": [],
        "job_match_percentage": 0,
        "job_match_summary": ""
    }}

    Be realistic. Never invent qualifications or experience.
    """

    response = client.models.generate_content(
       model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = json.loads(response.text)

    result["ats_score"] = max(
        0, min(100, int(result["ats_score"]))
    )

    return result
