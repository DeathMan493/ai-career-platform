const LEVEL_PROGRESS = {
    Beginner: 35,
    Intermediate: 60,
    Advanced: 85
};

const COURSE_SKILL_BOOST = 22;
const PAPER_SKILL_BOOST = 14;
const AUTO_ADD_THRESHOLD = 25;

function normalizeSkillName(value) {
    return (value || "").trim();
}

function progressToLevel(progress) {
    if (progress >= 80) {
        return "Advanced";
    }
    if (progress >= 55) {
        return "Intermediate";
    }
    return "Beginner";
}

function buildCompletedSkillBoosts(completedItems) {
    const progressMap = new Map();

    for (const course of completedItems.courses || []) {
        for (const tag of course.tags || []) {
            const skill = normalizeSkillName(tag);
            if (!skill) {
                continue;
            }
            progressMap.set(skill, Math.min(100, (progressMap.get(skill) || 0) + COURSE_SKILL_BOOST));
        }
    }

    for (const paper of completedItems.papers || []) {
        for (const tag of paper.tags || []) {
            const skill = normalizeSkillName(tag);
            if (!skill) {
                continue;
            }
            progressMap.set(skill, Math.min(100, (progressMap.get(skill) || 0) + PAPER_SKILL_BOOST));
        }
    }

    return progressMap;
}

export function deriveSkillState(baseProfile, completedItems) {
    const manualSkills = Array.isArray(baseProfile?.skills) ? baseProfile.skills : [];
    const progressMap = buildCompletedSkillBoosts(completedItems);
    const manualSkillNames = new Set();

    const mergedSkills = manualSkills.map((item) => {
        const skill = normalizeSkillName(item.skill);
        if (!skill) {
            return item;
        }

        manualSkillNames.add(skill);
        const baseProgress = LEVEL_PROGRESS[item.level] || LEVEL_PROGRESS.Beginner;
        const completionBoost = progressMap.get(skill) || 0;
        const totalProgress = Math.min(100, Math.max(baseProgress, completionBoost));

        progressMap.set(skill, totalProgress);

        return {
            ...item,
            skill,
            level: progressToLevel(totalProgress),
            source: "manual",
            progress: totalProgress
        };
    });

    const derivedSkills = [];

    for (const [skill, progress] of progressMap.entries()) {
        if (manualSkillNames.has(skill) || progress < AUTO_ADD_THRESHOLD) {
            continue;
        }

        derivedSkills.push({
            skill,
            level: progressToLevel(progress),
            source: "derived",
            progress
        });
    }

    const profileSkills = [
        ...mergedSkills.map(({ skill, level }) => ({ skill, level })),
        ...derivedSkills.map(({ skill, level }) => ({ skill, level }))
    ];

    return {
        profile: {
            ...baseProfile,
            skills: profileSkills
        },
        manualSkills: mergedSkills,
        derivedSkills,
        progressMap
    };
}

export function applySkillProgressToGapList(missingSkills, progressMap) {
    return (missingSkills || [])
        .map((item) => {
            const trackedProgress = progressMap.get(item.name);
            const progress = trackedProgress ? Math.max(item.progress, trackedProgress) : item.progress;
            const priority = progress >= 80 ? "Resolved" : item.priority;

            return {
                ...item,
                priority,
                progress
            };
        })
        .filter((item) => item.progress < 90);
}
