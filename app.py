
import streamlit as st
import io
from pypdf import PdfReader
from docx import Document
from ai_analyzer import analyze_resume

st.set_page_config(
    page_title="ResumeIQ | AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0d0b16;
    color: #f4f0ff;
}
.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}
.hero {
    background: linear-gradient(120deg,#251c42,#17152b);
    padding: 32px;
    border: 1px solid #40345f;
    border-radius: 20px;
    margin-bottom: 28px;
}
.hero h1 {
    font-size: 38px;
    color: #ffffff;
    margin-bottom: 8px;
}
.hero p {
    color: #c4b9dc;
    font-size: 15px;
}
.section {
    color: #c7a9ff;
    font-size: 21px;
    font-weight: 700;
    margin: 24px 0 12px;
}
.result-card {
    background: #191529;
    border: 1px solid #38304e;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 14px;
}
.score {
    font-size: 48px;
    font-weight: 800;
    color: #b99aff;
}
.small {
    color: #aaa0c0;
    font-size: 13px;
}
div.stButton > button {
    background: linear-gradient(90deg,#8155df,#a36bea);
    color: white;
    border: none;
    border-radius: 10px;
    height: 48px;
    font-weight: 700;
}
div.stButton > button:hover {
    border: 1px solid #c8aaff;
    color: white;
}
[data-testid="stFileUploader"] {
    background: #191529;
    border: 1px dashed #66518c;
    border-radius: 14px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)


def extract_text(uploaded_file):
    file_bytes = uploaded_file.getvalue()

    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    elif uploaded_file.name.lower().endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join(
            paragraph.text for paragraph in doc.paragraphs
        )

    else:
        raise ValueError("Please upload a PDF or DOCX file.")

    if not text.strip():
        raise ValueError(
            "No readable text found. Please upload a text-based resume."
        )

    return text[:20000]


st.markdown("""
<div class="hero">
    <h1>✦ ResumeIQ</h1>
    <p>AI-powered resume intelligence. Analyze your resume,
    discover skill gaps and improve your career opportunities.</p>
</div>
""", unsafe_allow_html=True)


left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown('<div class="section">01 · Upload Resume</div>',
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF and DOCX"
    )

    st.markdown('<div class="section">02 · Target Job</div>',
                unsafe_allow_html=True)

    job_description = st.text_area(
        "Paste job description (optional)",
        placeholder="Paste the job requirements here...",
        height=190
    )

    analyze_button = st.button(
        "✦ Analyze My Resume",
        use_container_width=True
    )

with right:
    st.markdown('<div class="section">What You Get</div>',
                unsafe_allow_html=True)

    features = [
        ("🎯", "ATS Compatibility", "Resume score out of 100"),
        ("🧠", "AI Resume Review", "Personalized resume feedback"),
        ("💡", "Skills Analysis", "Matched and missing skills"),
        ("📊", "Job Matching", "Compare resume with job description"),
        ("🚀", "Career Suggestions", "Actionable improvement tips")
    ]

    for icon, title, description in features:
        st.markdown(f"""
        <div class="result-card">
            <h4>{icon} {title}</h4>
            <span class="small">{description}</span>
        </div>
        """, unsafe_allow_html=True)


if analyze_button:

    if uploaded_file is None:
        st.warning("Please upload your resume first.")

    else:
        try:
            with st.spinner("Reading your resume..."):
                resume_text = extract_text(uploaded_file)

            with st.spinner("Gemini AI is analyzing your resume..."):
                result = analyze_resume(
                    resume_text,
                    job_description
                )

            st.markdown("---")
            st.markdown(
                '<div class="section">03 · Your Analysis Results</div>',
                unsafe_allow_html=True
            )

            score = result.get("ats_score", 0)
            match = result.get("job_match_percentage", 0)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="small">ATS SCORE</div>
                    <div class="score">{score}/100</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="small">JOB MATCH</div>
                    <div class="score">{match}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="small">SKILLS FOUND</div>
                    <div class="score">{len(result.get("matched_skills", []))}</div>
                </div>
                """, unsafe_allow_html=True)

            st.progress(max(0, min(100, score)) / 100)

            st.markdown("### 📝 AI Summary")
            st.write(result.get("summary", "No summary available."))

            st.markdown("### 💪 Your Strengths")
            for item in result.get("strengths", []):
                st.success(item)

            st.markdown("### ⚠️ Areas to Improve")
            for item in result.get("weaknesses", []):
                st.warning(item)

            st.markdown("### ✅ Matched Skills")
            skills = result.get("matched_skills", [])
            if skills:
                st.write(" · ".join(skills))
            else:
                st.info("No matched skills identified.")

            st.markdown("### 📚 Missing / Recommended Skills")
            missing = result.get("missing_skills", [])
            if missing:
                for item in missing:
                    st.write("• " + item)
            else:
                st.info("No missing skills identified.")

            st.markdown("### 🚀 Improvement Recommendations")
            for item in result.get("recommendations", []):
                st.info(item)

            st.markdown("### 🎯 Job Match Feedback")
            st.write(
                result.get(
                    "job_match_summary",
                    "No job-specific feedback available."
                )
            )

            st.download_button(
                "⬇ Download Analysis Report",
                data=(
                    "RESUMEIQ - AI ANALYSIS REPORT\n\n"
                    + str(result)
                ),
                file_name="resume_analysis.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info(
                "Check your API key, internet connection and uploaded file."
            )


st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#817891;'>"
    "ResumeIQ · AI-Powered Career Assistant"
    "</p>",
    unsafe_allow_html=True
)
