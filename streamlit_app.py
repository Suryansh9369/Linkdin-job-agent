import streamlit as st
import asyncio
import pandas as pd

from scraper.linkedin_scraper import LinkedInScraper
from ai.job_filter import JobFilter

st.set_page_config(
    page_title="AI LinkedIn Job Hunter",
    layout="wide"
)

st.title("🤖 AI LinkedIn Job Hunter")

# ---------------- SIDEBAR ----------------

st.sidebar.header("LinkedIn Login")

linkedin_email = st.sidebar.text_input(
    "LinkedIn Email"
)

linkedin_password = st.sidebar.text_input(
    "LinkedIn Password",
    type="password"
)

st.sidebar.header("Job Preferences")

keywords = st.sidebar.text_input(
    "Job Keywords (comma separated)",
    "AI Engineer, ML Engineer, Python Developer"
)

location = st.sidebar.text_input(
    "Location",
    "Remote"
)

max_jobs = st.sidebar.slider(
    "Maximum Jobs",
    1,
    100,
    30
)

must_have = st.sidebar.text_input(
    "Must Have Skills",
    "Python, AI, Machine Learning"
)

nice_to_have = st.sidebar.text_input(
    "Nice To Have",
    "FastAPI, AWS"
)

avoid = st.sidebar.text_input(
    "Avoid Keywords",
    "Internship, Unpaid"
)

# ---------------- BUTTON ----------------

if st.button("🚀 Start Job Hunt"):

    async def run_pipeline():

        scraper = LinkedInScraper()
        job_filter = JobFilter()

        # SCRAPE JOBS
        raw_jobs = await scraper.search_jobs(
            email=linkedin_email,
            password=linkedin_password,
            keywords=[k.strip() for k in keywords.split(",")],
            location=location,
            max_results=max_jobs
        )

        st.info(f"Scraped {len(raw_jobs)} jobs")

        preferences = {
            "must_have": [x.strip() for x in must_have.split(",")],
            "nice_to_have": [x.strip() for x in nice_to_have.split(",")],
            "avoid": [x.strip() for x in avoid.split(",")],
        }

        # AI FILTER
        matched_jobs = await job_filter.filter_jobs(
            raw_jobs,
            preferences
        )

        return matched_jobs

    with st.spinner("Running AI Job Agent..."):

        jobs = asyncio.run(run_pipeline())

    st.success(f"Found {len(jobs)} matched jobs")

    # DISPLAY RESULTS

    if jobs:

        for job in jobs:

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.subheader(job["title"])
                    st.write(f"🏢 {job['company']}")
                    st.write(f"📍 {job['location']}")

                with col2:
                    st.metric(
                        "Match",
                        f"{job['match_score']}/10"
                    )

                st.write(job["match_reason"])

                if job.get("description"):
                    with st.expander("Job Description"):
                        st.write(job["description"][:2000])

                st.link_button(
                    "Open Job",
                    job["url"]
                )

        # EXPORT CSV

        df = pd.DataFrame(jobs)

        csv = df.to_csv(index=False)

        st.download_button(
            "⬇ Download Results",
            csv,
            file_name="matched_jobs.csv",
            mime="text/csv"
        )