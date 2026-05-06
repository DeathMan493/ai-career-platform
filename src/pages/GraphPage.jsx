import { useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import SectionIntro from "../components/SectionIntro";
import { useAppData } from "../context/AppContext";
import { fetchGraph } from "../lib/api";

const lanePositions = {
    user: [{ x: 8, y: 50 }],
    skill: [{ x: 28, y: 28 }, { x: 28, y: 72 }],
    course: [{ x: 48, y: 28 }, { x: 48, y: 72 }],
    paper: [{ x: 69, y: 28 }, { x: 69, y: 72 }],
    job: [{ x: 90, y: 50 }]
};

function getEdgeLabelPosition(edge, nodesById) {
    const start = nodesById[edge.from];
    const end = nodesById[edge.to];
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const length = Math.sqrt((dx * dx) + (dy * dy)) || 1;

    return {
        x: (start.x + end.x) / 2 + ((-dy / length) * 3.1),
        y: (start.y + end.y) / 2 + ((dx / length) * 3.1)
    };
}

function shortenLabel(label, maxLength = 24) {
    if (label.length <= maxLength) {
        return label;
    }

    const cleaned = label
        .replace(/[^a-zA-Z0-9+/#\-\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
    const words = cleaned.split(" ").filter(Boolean);

    if (words.length > 3) {
        const compact = words.slice(0, 3).join(" ");
        return compact.length <= maxLength ? compact : `${compact.slice(0, maxLength - 3).trim()}...`;
    }

    return `${cleaned.slice(0, maxLength - 3).trim()}...`;
}

function buildDisplayNodes(nodes) {
    const counts = {
        user: 0,
        skill: 0,
        course: 0,
        paper: 0,
        job: 0
    };

    return nodes.map((node) => {
        const preset = lanePositions[node.type]?.[counts[node.type]];
        counts[node.type] = (counts[node.type] || 0) + 1;

        return {
            ...node,
            label: shortenLabel(node.label),
            fullLabel: node.label,
            x: preset?.x ?? node.x,
            y: preset?.y ?? node.y
        };
    });
}

function GraphPage() {
    const lanes = [
        { title: "User", left: "6%" },
        { title: "Skills", left: "24%" },
        { title: "Courses", left: "44%" },
        { title: "Papers", left: "65%" },
        { title: "Career", left: "86%" }
    ];
    const { profile, settings, knowledgeData: fallbackData } = useAppData();
    const [graphData, setGraphData] = useState(null);
    const [graphError, setGraphError] = useState("");

    useEffect(() => {
        async function loadGraph() {
            try {
                const response = await fetchGraph();
                setGraphData(response.data);
                setGraphError("");
            } catch {
                setGraphError("Using local graph fallback because backend graph fetch is unavailable.");
            }
        }

        loadGraph();
    }, []);

    const data = graphData || {
        career_goal: profile.careerGoal || fallbackData.roleSummary.title,
        nodes: fallbackData.graph.nodes,
        edges: fallbackData.graph.edges.map((edge) => ({ from: edge.from, to: edge.to, label: edge.label })),
        recommendation_paths: fallbackData.recommendationPaths
    };
    const displayNodes = buildDisplayNodes(data.nodes);
    const nodesById = Object.fromEntries(displayNodes.map((node) => [node.id, node]));

    return (
        <AppLayout currentPath="/graph" title="Graph View" badge="Explainable relationships">
            <SectionIntro title="Knowledge graph view" description="This view shows how users, skills, courses, papers, and jobs connect through one recommendation graph." />
            {graphError ? <p className="profile-message">{graphError}</p> : null}

            <section className="graph-layout">
                <div className="graph-stage">
                    <div className="graph-lanes">
                        {lanes.map((lane) => (
                            <span key={lane.title} className="graph-lane" style={{ left: lane.left }}>
                                {lane.title}
                            </span>
                        ))}
                    </div>
                    <svg className="graph-svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
                        {data.edges.map((edge) => (
                            <line
                                key={`${edge.from}-${edge.to}`}
                                x1={`${nodesById[edge.from].x}%`}
                                y1={`${nodesById[edge.from].y}%`}
                                x2={`${nodesById[edge.to].x}%`}
                                y2={`${nodesById[edge.to].y}%`}
                            />
                        ))}
                    </svg>

                    {settings.showExplainablePaths ? (
                        <div className="graph-label-layer">
                            {data.edges.map((edge) => {
                                const position = getEdgeLabelPosition(edge, nodesById);

                                return (
                                    <div key={`${edge.from}-${edge.to}-label`} className="edge-label" style={{ left: `${position.x}%`, top: `${position.y}%` }}>
                                        {edge.label}
                                    </div>
                                );
                            })}
                        </div>
                    ) : null}

                    <div className="graph-canvas">
                        {displayNodes.map((node) => (
                            <div
                                key={node.id}
                                className={`graph-node node-${node.type}`}
                                style={{ left: `${node.x}%`, top: `${node.y}%` }}
                                title={node.fullLabel}
                            >
                                <span>{node.label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="side-column">
                    <article className="card">
                        <h3>Node legend</h3>
                        <ul className="graph-legend">
                            <li><span className="legend-dot user-dot"></span>User profile: {data.career_goal || profile.careerGoal || "Goal not set"}</li>
                            <li><span className="legend-dot skill-dot"></span>Skills connect current capability to learning needs</li>
                            <li><span className="legend-dot course-dot"></span>Courses build readiness for papers and jobs</li>
                            <li><span className="legend-dot paper-dot"></span>Papers deepen research and domain understanding</li>
                            <li><span className="legend-dot job-dot"></span>Jobs represent practical end-goals and role alignment</li>
                        </ul>
                    </article>

                    {settings.showExplainablePaths ? (
                        <article className="card path-panel">
                            <h3>Explainable paths</h3>
                            <ul>
                                {data.recommendation_paths.map((path) => (
                                    <li key={path}>{path}</li>
                                ))}
                            </ul>
                        </article>
                    ) : (
                        <article className="card path-panel subdued-panel">
                            <h3>Explainable paths hidden</h3>
                            <p>Turn this back on in Settings whenever you want to inspect relationship labels and recommendation reasoning.</p>
                        </article>
                    )}
                </div>
            </section>
        </AppLayout>
    );
}

export default GraphPage;
