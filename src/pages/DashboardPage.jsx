import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import ResourceCard from "../components/ResourceCard";
import SectionIntro from "../components/SectionIntro";
import { useAppData } from "../context/AppContext";
import { fetchCourseRecommendations, fetchDashboard, fetchPaperRecommendations } from "../lib/api";
import { rankItemsForProfile } from "../lib/recommendationRanking";

function DashboardPage() {
    const { profile, settings, completedItems, knowledgeData: fallbackData } = useAppData();
    const [dashboardData, setDashboardData] = useState(fallbackData);
    const [coursePool, setCoursePool] = useState(fallbackData.courses);
    const [paperPool, setPaperPool] = useState(fallbackData.papers);
    const [dashboardError, setDashboardError] = useState("");

    useEffect(() => {
        async function loadDashboard() {
            try {
                const [dashboardResponse, courseResponse, paperResponse] = await Promise.all([
                    fetchDashboard(),
                    fetchCourseRecommendations(10),
                    fetchPaperRecommendations(10)
                ]);
                setDashboardData(dashboardResponse.data);
                setCoursePool(courseResponse.data.items);
                setPaperPool(paperResponse.data.items);
                setDashboardError("");
            } catch {
                setDashboardError("Using local dashboard fallback because backend dashboard fetch is unavailable.");
            }
        }

        loadDashboard();
    }, [fallbackData]);

    const completedCourseIds = new Set((completedItems.courses || []).map((item) => item.id));
    const completedPaperIds = new Set((completedItems.papers || []).map((item) => item.id));
    const courses = rankItemsForProfile(
        (coursePool || fallbackData.courses).filter((course) => !completedCourseIds.has(course.id)),
        profile
    )
        .slice(0, 3);
    const papers = rankItemsForProfile(
        (paperPool || fallbackData.papers).filter((paper) => !completedPaperIds.has(paper.id)),
        profile
    )
        .slice(0, 3);
    const jobs = dashboardData.jobs || fallbackData.jobs;
    const missingSkills = dashboardData.missing_skills || fallbackData.missingSkills;
    const recommendationPaths = dashboardData.recommendation_paths || fallbackData.recommendationPaths;
    const roleSummary = dashboardData.role_summary || fallbackData.roleSummary;
    const averageProgress = dashboardData.metrics?.readiness_score ?? Math.round(
        missingSkills.reduce((total, skill) => total + skill.progress, 0) / Math.max(missingSkills.length, 1)
    );

    return (
        <AppLayout currentPath="/dashboard" title="Dashboard" badge={`Welcome, ${profile.name}`}>
            {dashboardError ? <p className="profile-message">{dashboardError}</p> : null}
            <section className="card hero-card">
                <div className="hero-copy">
                    <h3>Your AI roadmap is taking shape</h3>
                    <p>{roleSummary.mission}</p>
                    <div className="goal-badge">
                        Career Goal: <strong>{profile.careerGoal || roleSummary.title}</strong>
                    </div>
                </div>

                <div className="hero-stats">
                    <div className="stat-tile">
                        <strong>{courses.length}</strong>
                        <span>Recommended courses</span>
                    </div>
                    <div className="stat-tile">
                        <strong>{missingSkills.filter((skill) => skill.priority === "High").length}</strong>
                        <span>Priority skill gaps</span>
                    </div>
                </div>
            </section>

            <section className="metrics-grid">
                <div className="metric-card">
                    <strong>{profile.skills.length}</strong>
                    <span>Current skills in profile</span>
                </div>
                <div className="metric-card">
                    <strong>{papers.length}</strong>
                    <span>Research papers selected</span>
                </div>
                <div className="metric-card">
                    <strong>{jobs.length}</strong>
                    <span>Career roles matched</span>
                </div>
                <div className="metric-card">
                    <strong>{averageProgress}%</strong>
                    <span>Estimated roadmap readiness</span>
                </div>
            </section>

            <SectionIntro
                title="Cross-domain recommendations"
                description="These suggestions are connected through your current skills and future role direction."
            />

            <section className="grid">
                <article className="card">
                    <h3>Courses</h3>
                    <ul className="resource-list">
                        {courses.map((course) => (
                            <ResourceCard
                                key={course.title}
                                item={course}
                                meta={`${course.provider} | ${course.level} | ${course.duration}`}
                            />
                        ))}
                    </ul>
                </article>

                <article className="card">
                    <h3>Papers</h3>
                    <ul className="resource-list">
                        {papers.map((paper) => (
                            <ResourceCard
                                key={paper.title}
                                item={paper}
                                meta={`${paper.venue} | ${paper.year}`}
                            />
                        ))}
                    </ul>
                </article>

                <article className="card">
                    <h3>Jobs</h3>
                    <ul className="resource-list">
                        {jobs.map((job) => (
                            <ResourceCard
                                key={job.title}
                                item={job}
                                meta={`${job.company} | ${job.fit}`}
                            />
                        ))}
                    </ul>
                </article>
            </section>

            {settings.showExplainablePaths ? (
                <>
                    <SectionIntro
                        title="Why these recommendations make sense"
                        description="The graph model can trace how your current strengths connect to missing skills, resources, and career outcomes."
                    />

                    <section className="card insight-card insight-layout">
                        <div>
                            <h3>Explainable recommendation paths</h3>
                            <ul className="path-list">
                                {recommendationPaths.map((path) => (
                                    <li key={path}>{path}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="readiness-panel">
                            <h4>Missing Skills</h4>
                            <p>These are the most important areas to strengthen for better cross-domain alignment.</p>
                            <ul className="skill-bars">
                                {missingSkills.map((skill) => (
                                    <li key={skill.name}>
                                        <strong>
                                            {skill.name}
                                            <span>{skill.progress}%</span>
                                        </strong>
                                        <div className="bar">
                                            <span style={{ width: `${skill.progress}%` }}></span>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </section>
                </>
            ) : (
                <section className="card readiness-only-card">
                    <div className="readiness-panel standalone-readiness">
                        <h4>Missing Skills</h4>
                        <p>Explainable paths are hidden in settings, but your roadmap gaps still stay visible here.</p>
                        <ul className="skill-bars">
                            {missingSkills.map((skill) => (
                                <li key={skill.name}>
                                    <strong>
                                        {skill.name}
                                        <span>{skill.progress}%</span>
                                    </strong>
                                    <div className="bar">
                                        <span style={{ width: `${skill.progress}%` }}></span>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                </section>
            )}
        </AppLayout>
    );
}

export default DashboardPage;
