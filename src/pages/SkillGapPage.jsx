import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import SectionIntro from "../components/SectionIntro";
import { useAppData } from "../context/AppContext";
import { fetchSkillGap } from "../lib/api";
import { applySkillProgressToGapList } from "../lib/skillProgress";

function SkillGapPage() {
    const { profile, completedItems, skillProgressMap, knowledgeData: fallbackData } = useAppData();
    const [skillGapData, setSkillGapData] = useState(null);
    const [skillGapError, setSkillGapError] = useState("");

    useEffect(() => {
        async function loadSkillGap() {
            try {
                const response = await fetchSkillGap();
                setSkillGapData(response.data);
                setSkillGapError("");
            } catch {
                setSkillGapError("Using local skill-gap fallback because backend skill-gap fetch is unavailable.");
            }
        }

        loadSkillGap();
    }, []);

    const data = skillGapData || {
        career_goal: profile.careerGoal || fallbackData.roleSummary.title,
        summary: fallbackData.roleSummary.mission,
        focus_areas: fallbackData.roleSummary.focusAreas,
        current_skill_count: profile.skills.length,
        gap_count: fallbackData.missingSkills.length,
        missing_skills: fallbackData.missingSkills,
        roadmap: fallbackData.roadmap,
        bridges: {
            courses: fallbackData.courses.slice(0, 2),
            papers: fallbackData.papers.slice(0, 2),
            jobs: fallbackData.jobs.slice(0, 2)
        }
    };
    const adjustedMissingSkills = applySkillProgressToGapList(data.missing_skills, skillProgressMap);
    const completionCount = (completedItems.courses || []).length + (completedItems.papers || []).length;

    return (
        <AppLayout currentPath="/skill-gap" title="Skill Gap Analysis" badge="Roadmap intelligence">
            {skillGapError ? <p className="profile-message">{skillGapError}</p> : null}
            <section className="card overview-card">
                <div>
                    <h3>{data.career_goal}</h3>
                    <p>{data.summary}</p>
                    <div className="focus-pills">
                        {data.focus_areas.map((area) => (
                            <span className="pill" key={area}>{area}</span>
                        ))}
                    </div>
                </div>

                <div className="score-panel">
                    <div className="score-tile">
                        <strong>{profile.skills.length}</strong>
                        <span>Current profile skills</span>
                    </div>
                    <div className="score-tile">
                        <strong>{adjustedMissingSkills.length}</strong>
                        <span>Priority gaps to close</span>
                    </div>
                    <div className="score-tile">
                        <strong>{completionCount}</strong>
                        <span>Completed learning items</span>
                    </div>
                </div>
            </section>

            <SectionIntro title="Missing skills by recommendation impact" description="These gaps affect how well courses, papers, and jobs align with your current path." />

            <section className="gap-grid">
                {adjustedMissingSkills.map((skill) => (
                    <article className="gap-card" key={skill.name}>
                        <div className="gap-card-top">
                            <div>
                                <p className="eyebrow-label">{skill.priority} Priority</p>
                                <h3>{skill.name}</h3>
                            </div>
                            <span className="progress-value">{skill.progress}%</span>
                        </div>
                        <div className="progress-track">
                            <span style={{ width: `${skill.progress}%` }}></span>
                        </div>
                        <p>{skill.reason}</p>
                    </article>
                ))}
            </section>

            <SectionIntro title="Progression roadmap" description="A simple frontend view of how the graph can guide a user from current skills to target opportunities." />

            <section className="card">
                <div className="timeline-list">
                    {data.roadmap.map((item) => (
                        <div className="timeline-step" key={item.phase}>
                            <span>{item.timeline}</span>
                            <h4>{item.phase}</h4>
                            <p>{item.action}</p>
                        </div>
                    ))}
                </div>
            </section>

            <SectionIntro title="Cross-domain bridge" description="The same missing skills can influence what you should learn, read, and apply for next." />

            <section className="bridge-grid">
                <article className="card bridge-card">
                    <h3>Courses that close gaps</h3>
                    <ul>
                        {data.bridges.courses.map((course) => (
                            <li key={course.title}>
                                <strong>{course.title}</strong>
                                <span>{course.reason}</span>
                            </li>
                        ))}
                    </ul>
                </article>

                <article className="card bridge-card">
                    <h3>Papers that deepen understanding</h3>
                    <ul>
                        {data.bridges.papers.map((paper) => (
                            <li key={paper.title}>
                                <strong>{paper.title}</strong>
                                <span>{paper.reason}</span>
                            </li>
                        ))}
                    </ul>
                </article>

                <article className="card bridge-card">
                    <h3>Jobs unlocked by improvement</h3>
                    <ul>
                        {data.bridges.jobs.map((job) => (
                            <li key={job.title}>
                                <strong>{job.title}</strong>
                                <span>{job.reason}</span>
                            </li>
                        ))}
                    </ul>
                </article>
            </section>
        </AppLayout>
    );
}

export default SkillGapPage;
