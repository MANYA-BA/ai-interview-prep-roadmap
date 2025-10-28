import streamlit as st
import json
from research_agent import AgentOrchestrator, save_roadmap

st.set_page_config(page_title="Interview Roadmap Builder", layout="wide")

st.title("AI Interview Preparation Roadmap Generator")
st.markdown(
    "Use this UI to paste a job description or upload a JD file, then generate a study roadmap."
)

with st.form("jd_form"):
    company = st.text_input("Company", value="Acme")
    role = st.text_input("Role", value="Backend Engineer")
    jd_file = st.file_uploader("Upload job description (optional)", type=["txt", "md", "json"])
    jd_text_area = st.text_area("Or paste the job description here", height=200)
    submit = st.form_submit_button("Generate Roadmap")

if submit:
    jd_text = ""
    if jd_file is not None:
        try:
            jd_text = jd_file.read().decode("utf-8")
        except Exception:
            jd_text = jd_file.getvalue().decode("utf-8")
    if not jd_text:
        jd_text = jd_text_area

    if not jd_text.strip():
        st.warning("Please provide a job description either by uploading a file or pasting text.")
    else:
        with st.spinner("Generating roadmap — this may take a few seconds..."):
            orchestrator = AgentOrchestrator()
            roadmap = orchestrator.run(company=company, role=role, jd_text=jd_text)
            saved_path = save_roadmap(roadmap, company, role)

        st.success("Roadmap generated successfully")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Roadmap JSON")
            st.json(roadmap)

            # Provide download
            json_str = json.dumps(roadmap, indent=2)
            filename = saved_path.split("\\")[-1]
            st.download_button(label="Download JSON", data=json_str, file_name=filename, mime="application/json")

        with col2:
            st.subheader("Summary")
            st.write(f"**Company:** {roadmap.get('company')}")
            st.write(f"**Role:** {roadmap.get('role')}")
            st.write(f"**Difficulty:** {roadmap.get('difficulty')}")
            st.write(f"**Preparation timeline:** {roadmap.get('preparation_timeline')}")

            st.markdown("**Recommended study order**")
            for idx, item in enumerate(roadmap.get("recommended_order", []), 1):
                st.write(f"{idx}. {item}")

            st.markdown("**Rounds**")
            for r in roadmap.get("rounds", []):
                st.markdown(f"- **{r.get('type')}** — Topics: {', '.join(r.get('topics', []))} — Est. prep: {r.get('estimated_prep_time')}")

        st.write("\n")
        st.info(f"Saved roadmap file: {saved_path}")
