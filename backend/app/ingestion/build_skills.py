from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from typing import Any

from pymongo import UpdateOne

from app.ingestion.mongo import get_database
from app.ingestion.normalizers import compact_text


ACRONYMS = {
    "ai": "AI",
    "api": "API",
    "aws": "AWS",
    "cnn": "CNN",
    "cpu": "CPU",
    "css": "CSS",
    "etl": "ETL",
    "gcp": "GCP",
    "gnn": "GNN",
    "gpu": "GPU",
    "html": "HTML",
    "json": "JSON",
    "kpi": "KPI",
    "llm": "LLM",
    "ml": "ML",
    "mlops": "MLOps",
    "nlp": "NLP",
    "nosql": "NoSQL",
    "pdf": "PDF",
    "rag": "RAG",
    "rest": "REST",
    "sql": "SQL",
    "ui": "UI",
    "ux": "UX",
}

CANONICAL_ALIASES = {
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "applications of artificial intelligence": "Artificial Intelligence",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "machine learning": "Machine Learning",
    "machine learning algorithms": "Machine Learning",
    "statistical machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",
    "graph neural networks": "Graph Neural Networks",
    "gnn": "Graph Neural Networks",
    "large language models": "Large Language Models",
    "llm": "Large Language Models",
    "knowledge graphs": "Knowledge Graphs",
    "knowledge graph": "Knowledge Graphs",
    "knowledge graph enhanced recommendation": "Knowledge Graphs",
    "knowledge representation and reasoning": "Knowledge Representation and Reasoning",
    "knowledge based systems": "Knowledge-Based Systems",
    "recommender system": "Recommendation Systems",
    "recommendation": "Recommendation Systems",
    "collaborative filtering": "Collaborative Filtering",
    "feature learning": "Feature Learning",
    "reinforcement learning": "Reinforcement Learning",
    "representation learning": "Representation Learning",
    "computer vision": "Computer Vision",
    "information retrieval": "Information Retrieval",
    "data mining": "Data Mining",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",
    "data visualization software": "Data Visualization",
    "probability statistics": "Probability and Statistics",
    "probability & statistics": "Probability and Statistics",
    "general statistics": "Statistics",
    "regression": "Regression Analysis",
    "path computing": "Graph Paths",
    "cypher": "Neo4j Cypher",
    "neo4j": "Neo4j",
    "neo4j cypher": "Neo4j Cypher",
    "python programming": "Python",
    "python": "Python",
    "r programming": "R",
    "java programming": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "c plus plus": "C++",
    "c++": "C++",
    "c sharp": "C#",
    "c#": "C#",
    "structured query language": "SQL",
    "sql": "SQL",
    "nosql": "NoSQL",
    "mongodb": "MongoDB",
    "pytorch": "PyTorch",
    "tensor flow": "TensorFlow",
    "tensorflow": "TensorFlow",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "data structures and algorithms": "Data Structures and Algorithms",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "computer programming": "Programming",
    "programming language": "Programming",
    "software engineering": "Software Engineering",
    "agile software development": "Agile Software Development",
    "web development tools": "Web Development",
    "web development": "Web Development",
    "web design": "Web Design",
    "database administration": "Database Administration",
    "database application": "Databases",
    "database theory": "Databases",
    "databases": "Databases",
    "data model": "Data Modeling",
    "extract transform load": "ETL",
    "computer security incident management": "Cybersecurity",
    "network security": "Network Security",
    "cryptography": "Cryptography",
    "network architecture": "Network Architecture",
    "risk management": "Risk Analysis",
    "cloud computing": "Cloud Computing",
    "ibm cloud": "Cloud Computing",
    "research methodology": "Research Methodology",
    "model evaluation": "Model Evaluation",
    "computer science": "Computer Science",
    "theoretical computer science": "Computer Science Theory",
}

SEED_JOB_SKILLS = {
    "Python",
    "R",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "Computer Vision",
    "Graph Neural Networks",
    "Knowledge Graphs",
    "Knowledge Representation and Reasoning",
    "Recommendation Systems",
    "Collaborative Filtering",
    "Neo4j",
    "Neo4j Cypher",
    "SQL",
    "NoSQL",
    "MongoDB",
    "Data Science",
    "Data Analysis",
    "Data Visualization",
    "Data Mining",
    "PyTorch",
    "TensorFlow",
    "Scikit-learn",
    "Research Methodology",
    "Model Evaluation",
    "Statistics",
    "Probability and Statistics",
    "Linear Algebra",
    "Probability",
    "Algorithms",
    "Data Structures",
    "Data Structures and Algorithms",
    "Software Engineering",
    "Agile Software Development",
    "MLOps",
    "REST APIs",
    "Cloud Computing",
    "AWS",
    "Docker",
    "Kubernetes",
    "Git",
    "Network Security",
    "Cryptography",
    "ETL",
    "Information Retrieval",
}

STOPWORDS = {
    "a", "an", "and", "for", "of", "the", "to", "with", "in", "on", "by", "from", "using", "use",
    "applications", "application", "systems", "system", "methods", "method", "based", "introduction",
    "fundamentals", "fundamental", "advanced", "beginner", "beginners", "intermediate", "specialization",
    "professional", "certificate", "course", "courses", "project", "projects", "practical", "practice",
    "complete", "guide", "essentials", "concepts", "concept", "theory", "research", "study",
}

GENERIC_BLACKLIST = {
    "Advertising",
    "Business Analysis",
    "Business Communication",
    "Change Management",
    "Collaboration",
    "Communication",
    "Culture",
    "Economics",
    "Emotional Intelligence",
    "Entrepreneurship",
    "Finance",
    "Focus",
    "Geography",
    "Granularity",
    "Human Learning",
    "Influencing",
    "Leadership",
    "Linguistics",
    "Logistics",
    "Management",
    "Marketing",
    "Marketing Management",
    "Media Strategy Planning",
    "Microeconomics",
    "Operations",
    "Organizational Development",
    "People Management",
    "Persona Research",
    "Philosophy",
    "Planning",
    "Preference",
    "Problem Solving",
    "Procurement",
    "Product Management",
    "Sales",
    "Small Data",
    "Social Media",
    "Strategy",
    "Supply Chain",
    "Task",
    "Transfer Of Learning",
    "Writing",
}

TECHNICAL_KEYWORDS = {
    "ai", "algorithm", "analytics", "api", "artificial", "cloud", "code", "coding", "computer", "crypto",
    "cyber", "cypher", "data", "database", "deep", "docker", "embedding", "etl", "evaluation", "feature",
    "filtering", "framework", "generative", "git", "graph", "information", "intelligence", "java", "javascript",
    "json", "knowledge", "kubernetes", "language", "learn", "learning", "linear", "llm", "machine", "mining",
    "ml", "mlops", "model", "mongodb", "natural", "network", "neo4j", "nlp", "nosql", "probability",
    "programming", "python", "pytorch", "rag", "reasoning", "recommendation", "regression", "representation",
    "research", "retrieval", "scikit", "science", "security", "software", "sql", "statistic", "survey",
    "system", "tensorflow", "theory", "vision", "visualization", "web",
}

SPLIT_PATTERN = re.compile(r"[|,/;]+")
WHITESPACE_PATTERN = re.compile(r"\s+")
NON_ALNUM_PATTERN = re.compile(r"[^a-zA-Z0-9+#./\-\s]")


def slugify(value: str) -> str:
    cleaned = NON_ALNUM_PATTERN.sub(" ", value)
    cleaned = cleaned.replace("_", " ")
    cleaned = cleaned.replace("-", " ")
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip().casefold()
    return cleaned


def prettify_token(token: str) -> str:
    lowered = token.casefold()
    if lowered in ACRONYMS:
        return ACRONYMS[lowered]
    if token in {"C++", "C#", "Scikit-learn", "PyTorch", "TensorFlow", "Neo4j"}:
        return token
    return token.capitalize()


def prettify_skill(value: str) -> str:
    if value in {"C++", "C#", "Scikit-learn", "PyTorch", "TensorFlow", "Neo4j", "Neo4j Cypher", "REST APIs", "MLOps", "ETL"}:
        return value
    return " ".join(prettify_token(token) for token in value.split())


def is_relevant_skill(candidate: str) -> bool:
    if candidate in GENERIC_BLACKLIST:
        return False

    lowered = candidate.casefold()
    if lowered in {item.casefold() for item in GENERIC_BLACKLIST}:
        return False

    if candidate in SEED_JOB_SKILLS:
        return True

    if any(symbol in candidate for symbol in ["+", "#"]):
        return True

    tokens = lowered.split()
    return any(any(keyword in token for keyword in TECHNICAL_KEYWORDS) for token in tokens)


def canonicalize_skill(raw_value: str | None) -> str | None:
    value = compact_text(raw_value)
    if not value:
        return None

    for part in SPLIT_PATTERN.split(value):
        candidate = compact_text(part)
        if not candidate:
            continue

        normalized = slugify(candidate)
        if not normalized or normalized in STOPWORDS:
            continue

        canonical = CANONICAL_ALIASES.get(normalized, prettify_skill(normalized))
        if len(canonical) < 2:
            continue
        if not is_relevant_skill(canonical):
            continue
        return canonical

    return None


def iter_course_skills(document: dict[str, Any]) -> set[str]:
    normalized: set[str] = set()
    for skill in document.get("skills") or []:
        canonical = canonicalize_skill(skill)
        if canonical:
            normalized.add(canonical)
    return normalized


def iter_paper_skills(document: dict[str, Any]) -> set[str]:
    normalized: set[str] = set()
    for keyword in document.get("keywords") or []:
        canonical = canonicalize_skill(keyword)
        if canonical:
            normalized.add(canonical)
    for concept in document.get("concepts") or []:
        canonical = canonicalize_skill((concept or {}).get("name"))
        if canonical:
            normalized.add(canonical)
    return normalized


def build_job_vocab(courses: list[dict[str, Any]], papers: list[dict[str, Any]]) -> list[str]:
    vocabulary = set(SEED_JOB_SKILLS)
    for course in courses:
        vocabulary.update(iter_course_skills(course))
    for paper in papers:
        vocabulary.update(iter_paper_skills(paper))
    return sorted(vocabulary, key=lambda item: (-len(item), item))


def extract_job_skills(document: dict[str, Any], vocabulary: list[str]) -> set[str]:
    text_parts = [
        document.get("title") or "",
        document.get("qualification_summary") or "",
        document.get("requirements") or "",
    ]
    haystack = " ".join(text_parts).casefold()
    normalized: set[str] = set()

    for skill in vocabulary:
        pattern = rf"(?<!\w){re.escape(skill.casefold())}(?!\w)"
        if re.search(pattern, haystack):
            normalized.add(skill)

    return normalized


def build_skill_documents(course_docs: list[dict[str, Any]], paper_docs: list[dict[str, Any]], job_docs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    skill_index: dict[str, dict[str, Any]] = {}
    course_matches: dict[str, list[str]] = {}
    paper_matches: dict[str, list[str]] = {}
    job_matches: dict[str, list[str]] = {}

    def register_skill(name: str, alias: str | None, source_tag: str, example_title: str | None) -> None:
        entry = skill_index.setdefault(name, {
            "name": name,
            "aliases": set(),
            "source_tags": set(),
            "source_counts": Counter(),
            "occurrence_count": 0,
            "examples": defaultdict(list),
            "category": None,
            "description": None,
            "onet_code": None,
        })
        if alias and alias.casefold() != name.casefold():
            entry["aliases"].add(alias)
        entry["source_tags"].add(source_tag)
        entry["source_counts"][source_tag] += 1
        entry["occurrence_count"] += 1
        if example_title and len(entry["examples"][source_tag]) < 3 and example_title not in entry["examples"][source_tag]:
            entry["examples"][source_tag].append(example_title)

    for course in course_docs:
        skills = sorted(iter_course_skills(course))
        course_matches[str(course["_id"])] = skills
        for skill in skills:
            register_skill(skill, None, "course", course.get("title"))

    for paper in paper_docs:
        skills = sorted(iter_paper_skills(paper))
        paper_matches[str(paper["_id"])] = skills
        for skill in skills:
            register_skill(skill, None, "paper", paper.get("title"))

    job_vocabulary = build_job_vocab(course_docs, paper_docs)
    for job in job_docs:
        skills = sorted(extract_job_skills(job, job_vocabulary))
        job_matches[str(job["_id"])] = skills
        for skill in skills:
            register_skill(skill, None, "job", job.get("title"))

    documents: list[dict[str, Any]] = []
    for name, entry in sorted(skill_index.items()):
        documents.append({
            "name": name,
            "aliases": sorted(entry["aliases"]),
            "source_tags": sorted(entry["source_tags"]),
            "source_counts": dict(entry["source_counts"]),
            "occurrence_count": entry["occurrence_count"],
            "examples": dict(entry["examples"]),
            "category": entry["category"],
            "description": entry["description"],
            "onet_code": entry["onet_code"],
        })

    return documents, course_matches, paper_matches, job_matches


def apply_normalized_skills(collection, match_map: dict[str, list[str]]) -> int:
    operations: list[UpdateOne] = []
    for document in collection.find({}, {"_id": 1}):
        document_id = str(document["_id"])
        operations.append(
            UpdateOne(
                {"_id": document["_id"]},
                {"$set": {"normalized_skills": match_map.get(document_id, [])}},
            )
        )

    if not operations:
        return 0

    result = collection.bulk_write(operations, ordered=False)
    return result.modified_count


def build_skills(min_occurrences: int, dry_run: bool) -> None:
    database = get_database()
    course_collection = database["courses"]
    paper_collection = database["papers"]
    job_collection = database["jobs"]
    skills_collection = database["skills"]

    course_docs = list(course_collection.find({}, {"title": 1, "skills": 1}))
    paper_docs = list(paper_collection.find({}, {"title": 1, "keywords": 1, "concepts": 1}))
    job_docs = list(job_collection.find({}, {"title": 1, "qualification_summary": 1, "requirements": 1}))

    skill_documents, course_matches, paper_matches, job_matches = build_skill_documents(course_docs, paper_docs, job_docs)
    filtered_documents = [doc for doc in skill_documents if doc["occurrence_count"] >= min_occurrences]
    allowed_names = {doc["name"] for doc in filtered_documents}

    course_matches = {key: [skill for skill in values if skill in allowed_names] for key, values in course_matches.items()}
    paper_matches = {key: [skill for skill in values if skill in allowed_names] for key, values in paper_matches.items()}
    job_matches = {key: [skill for skill in values if skill in allowed_names] for key, values in job_matches.items()}

    print(
        "Skill extraction summary:",
        {
            "course_documents": len(course_docs),
            "paper_documents": len(paper_docs),
            "job_documents": len(job_docs),
            "skills_ready": len(filtered_documents),
            "min_occurrences": min_occurrences,
        },
    )

    if dry_run:
        print("Top extracted skills preview:")
        for skill in sorted(filtered_documents, key=lambda item: (-item["occurrence_count"], item["name"]))[:15]:
            print(f"- {skill['name']} ({skill['occurrence_count']})")
        return

    skill_operations = [
        UpdateOne(
            {"name": document["name"]},
            {"$set": document},
            upsert=True,
        )
        for document in filtered_documents
    ]

    if skill_operations:
        result = skills_collection.bulk_write(skill_operations, ordered=False)
        skills_collection.create_index([("name", 1)], unique=True)
        skills_collection.create_index([("source_tags", 1)])
        print(
            "Skills collection write complete:",
            {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "matched": result.matched_count,
            },
        )

    course_updates = apply_normalized_skills(course_collection, course_matches)
    paper_updates = apply_normalized_skills(paper_collection, paper_matches)
    job_updates = apply_normalized_skills(job_collection, job_matches)

    print(
        "Source collections updated with normalized_skills:",
        {
            "courses_modified": course_updates,
            "papers_modified": paper_updates,
            "jobs_modified": job_updates,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a normalized skills collection from courses, papers, and jobs.")
    parser.add_argument("--min-occurrences", type=int, default=2, help="Only keep skills seen at least this many times.")
    parser.add_argument("--dry-run", action="store_true", help="Preview extracted skills without writing to MongoDB.")
    args = parser.parse_args()

    build_skills(min_occurrences=args.min_occurrences, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
