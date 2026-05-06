import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import ResourceCard from "../components/ResourceCard";
import SectionIntro from "../components/SectionIntro";
import { useAppData } from "../context/AppContext";
import { fetchPaperRecommendations } from "../lib/api";
import { rankItemsForProfile } from "../lib/recommendationRanking";

function PapersPage() {
    const { profile, completedItems, markItemCompleted, unmarkItemCompleted, knowledgeData: fallbackData } = useAppData();
    const [papers, setPapers] = useState(fallbackData.papers);
    const [pageError, setPageError] = useState("");

    useEffect(() => {
        async function loadPapers() {
            try {
                const response = await fetchPaperRecommendations(10);
                setPapers(response.data.items);
                setPageError("");
            } catch {
                setPageError("Using local paper fallback because backend paper fetch is unavailable.");
            }
        }

        loadPapers();
    }, [fallbackData.papers]);

    const completedPaperIds = new Set((completedItems.papers || []).map((item) => item.id));
    const unreadPapers = rankItemsForProfile(papers.filter((paper) => !completedPaperIds.has(paper.id)), profile);
    const completedPapers = completedItems.papers || [];

    return (
        <AppLayout currentPath="/papers" title="Research Papers" badge={`${unreadPapers.length} active recommendations`}>
            <SectionIntro
                title="Recommended papers"
                description="Track the papers you have already read so the dashboard can keep introducing fresh research instead of repeating the same list."
            />
            {pageError ? <p className="profile-message">{pageError}</p> : null}

            <section className="card">
                <h3>Active paper list</h3>
                <ul className="resource-list">
                    {unreadPapers.map((paper) => (
                        <ResourceCard
                            key={paper.id}
                            item={paper}
                            meta={`${paper.venue} | ${paper.year}`}
                            actionLabel="Mark as Read"
                            onAction={() => markItemCompleted("papers", paper)}
                        />
                    ))}
                </ul>
            </section>

            {completedPapers.length ? (
                <section className="card">
                    <h3>Read papers</h3>
                    <ul className="resource-list">
                        {completedPapers.map((paper) => (
                            <ResourceCard
                                key={paper.id}
                                item={paper}
                                meta={`${paper.venue} | ${paper.year}`}
                                actionLabel="Move Back to Active"
                                onAction={() => unmarkItemCompleted("papers", paper.id)}
                            />
                        ))}
                    </ul>
                </section>
            ) : null}
        </AppLayout>
    );
}

export default PapersPage;
