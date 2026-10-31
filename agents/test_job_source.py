from agents.job_sources import JobData


def get_test_jobs():

    return [

        JobData(
            title="Python Developer",
            company_name="Demo Technologies",
            location="Bangalore",
            job_type="full_time",
            description=(
                "Looking for a Python Developer to build "
                "backend applications and REST APIs."
            ),
            requirements=(
                "Python, Django, REST API, SQL. "
                "0-2 years experience."
            ),
            skills=(
                "Python, Django, REST API, SQL, Git"
            ),
            salary="₹4-8 LPA",
            source="Demo Source",
            source_url="https://example.com/jobs/python-developer-demo",
        ),

        JobData(
            title="AI Engineer",
            company_name="Demo AI Labs",
            location="Remote",
            job_type="remote",
            description=(
                "Work on machine learning and AI applications."
            ),
            requirements=(
                "Python, Machine Learning, Deep Learning, "
                "LLMs and APIs."
            ),
            skills=(
                "Python, Machine Learning, Deep Learning, "
                "LLM, FastAPI"
            ),
            salary="₹6-12 LPA",
            source="Demo Source",
            source_url="https://example.com/jobs/ai-engineer-demo",
        ),

    ]