def extract_skills(text):

    if not text:
        return ""

    text_lower = text.lower()

    matched_skills = []

    for skill in KNOWN_SKILLS:

        if skill.lower() in text_lower:

            matched_skills.append(skill)

    return ", ".join(
        matched_skills
    )

KNOWN_SKILLS = [
    "Python",
    "Django",
    "FastAPI",
    "Flask",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "Computer Vision",
    "PyTorch",
    "TensorFlow",
    "scikit-learn",
    "Pandas",
    "NumPy",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "REST API",
    "LLM",
    "Generative AI",
    "LangChain",
    "LlamaIndex",
]