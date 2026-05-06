const GOAL_KEYWORDS = {
    "AI Researcher": ["research", "evaluation", "knowledge graphs", "graph neural networks", "machine learning", "deep learning"],
    "Machine Learning Engineer": ["deployment", "mlops", "machine learning", "deep learning", "python", "cloud computing"],
    "Data Scientist": ["data science", "statistics", "data analysis", "visualization", "machine learning", "analytics"]
};

function normalize(value) {
    return (value || "").trim().toLowerCase();
}

export function rankItemsForProfile(items, profile) {
    const skillSet = new Set((profile.skills || []).map((item) => normalize(item.skill)).filter(Boolean));
    const goalKeywords = GOAL_KEYWORDS[profile.careerGoal || ""] || [];

    return [...items].sort((left, right) => {
        const leftTags = (left.tags || []).map(normalize);
        const rightTags = (right.tags || []).map(normalize);

        const leftSkillOverlap = leftTags.filter((tag) => skillSet.has(tag)).length;
        const rightSkillOverlap = rightTags.filter((tag) => skillSet.has(tag)).length;

        const leftGoalOverlap = leftTags.filter((tag) => goalKeywords.includes(tag)).length;
        const rightGoalOverlap = rightTags.filter((tag) => goalKeywords.includes(tag)).length;

        const leftScore = (leftSkillOverlap * 2) + leftGoalOverlap;
        const rightScore = (rightSkillOverlap * 2) + rightGoalOverlap;

        if (leftScore !== rightScore) {
            return rightScore - leftScore;
        }

        return (left.title || "").localeCompare(right.title || "");
    });
}
