import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import ResourceCard from "../components/ResourceCard";
import SectionIntro from "../components/SectionIntro";
import { useAppData } from "../context/AppContext";
import { fetchCourseRecommendations } from "../lib/api";
import { rankItemsForProfile } from "../lib/recommendationRanking";

function CoursesPage() {
    const { profile, completedItems, markItemCompleted, unmarkItemCompleted, knowledgeData: fallbackData } = useAppData();
    const [courses, setCourses] = useState(fallbackData.courses);
    const [pageError, setPageError] = useState("");

    useEffect(() => {
        async function loadCourses() {
            try {
                const response = await fetchCourseRecommendations(10);
                setCourses(response.data.items);
                setPageError("");
            } catch {
                setPageError("Using local course fallback because backend course fetch is unavailable.");
            }
        }

        loadCourses();
    }, [fallbackData.courses]);

    const completedCourseIds = new Set((completedItems.courses || []).map((item) => item.id));
    const unreadCourses = rankItemsForProfile(courses.filter((course) => !completedCourseIds.has(course.id)), profile);
    const completedCourses = completedItems.courses || [];

    return (
        <AppLayout currentPath="/courses" title="Courses" badge={`${unreadCourses.length} active recommendations`}>
            <SectionIntro
                title="Recommended courses"
                description="Mark a course as completed once you finish or review it. The dashboard will stop showing completed items and surface the next strongest match."
            />
            {pageError ? <p className="profile-message">{pageError}</p> : null}

            <section className="card">
                <h3>Active course list</h3>
                <ul className="resource-list">
                    {unreadCourses.map((course) => (
                        <ResourceCard
                            key={course.id}
                            item={course}
                            meta={`${course.provider} | ${course.level} | ${course.duration}`}
                            actionLabel="Mark as Completed"
                            onAction={() => markItemCompleted("courses", course)}
                        />
                    ))}
                </ul>
            </section>

            {completedCourses.length ? (
                <section className="card">
                    <h3>Completed courses</h3>
                    <ul className="resource-list">
                        {completedCourses.map((course) => (
                            <ResourceCard
                            key={course.id}
                            item={course}
                            meta={`${course.provider} | ${course.level} | ${course.duration}`}
                            actionLabel="Move Back to Active"
                            onAction={() => unmarkItemCompleted("courses", course.id)}
                            />
                        ))}
                    </ul>
                </section>
            ) : null}
        </AppLayout>
    );
}

export default CoursesPage;
