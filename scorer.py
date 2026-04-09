def calculate_score(skills):
    weights = {
        "python": 20,
        "java": 15,
        "sql": 15,
        "machine learning": 25,
        "html": 10,
        "css": 5,
        "javascript": 10
    }

    score = 0
    for s in skills:
        score += weights.get(s, 0)

    return min(score, 100)


def suggest_roles(skills):
    if "machine learning" in skills:
        return "Data Scientist"
    elif "javascript" in skills:
        return "Web Developer"
    elif "sql" in skills:
        return "Data Analyst"
    return "Software Developer"


def missing_skills(skills):
    required = ["python", "sql", "machine learning"]
    return [r for r in required if r not in skills]