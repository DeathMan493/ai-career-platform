from app.schemas.auth import AuthPayload, AuthUser
from app.schemas.dashboard import (
    CourseItem,
    DashboardMetrics,
    DashboardPayload,
    JobItem,
    MissingSkillItem,
    PaperItem,
    RoleSummary,
)
from app.schemas.evaluation import EvaluationMetricsPayload, RecommendationExplanation
from app.schemas.graph import GraphEdge, GraphLegend, GraphNode, GraphPayload
from app.schemas.profile import ProfilePayload, SkillItem
from app.schemas.skill_gap import FocusBridgeItem, MissingSkillItem as SkillGapMissingSkillItem, RoadmapStep, SkillGapBridges, SkillGapPayload


def get_auth_payload() -> AuthPayload:
    return AuthPayload(
        user=AuthUser(id="user_001", name="Amrita User", email="amrita@example.com"),
        token="jwt-token",
    )


def get_profile_payload() -> ProfilePayload:
    return ProfilePayload(
        id="user_001",
        name="Amrita User",
        career_goal="AI Researcher",
        skills=[
            SkillItem(skill="Python", level="Advanced"),
            SkillItem(skill="Machine Learning", level="Advanced"),
            SkillItem(skill="Data Structures", level="Intermediate"),
            SkillItem(skill="Deep Learning", level="Intermediate"),
        ],
    )


def get_dashboard_payload() -> DashboardPayload:
    return DashboardPayload(
        role_summary=RoleSummary(
            title="AI Researcher",
            mission="Blend advanced learning, research depth, and real-world problem solving into a focused AI career path.",
            focus_areas=["Representation learning", "Research communication", "Model deployment awareness"],
        ),
        metrics=DashboardMetrics(
            profile_skill_count=4,
            course_count=3,
            paper_count=3,
            job_count=3,
            high_priority_gap_count=2,
            readiness_score=48,
        ),
        courses=[
            CourseItem(
                id="course_001",
                title="Advanced Deep Learning Systems",
                provider="Coursera",
                level="Advanced",
                duration="8 weeks",
                reason="Builds stronger model design intuition for your research-focused goal.",
                tags=["Neural Networks", "Optimization", "PyTorch"],
            ),
            CourseItem(
                id="course_002",
                title="Graph Neural Networks in Practice",
                provider="edX",
                level="Intermediate",
                duration="6 weeks",
                reason="Directly supports graph-based recommendation and knowledge representation work.",
                tags=["GNN", "Knowledge Graphs", "Applications"],
            ),
            CourseItem(
                id="course_003",
                title="Scientific Writing for AI",
                provider="FutureLearn",
                level="Intermediate",
                duration="4 weeks",
                reason="Helps turn experiments into strong papers and reproducible research output.",
                tags=["Research", "Writing", "Evaluation"],
            ),
        ],
        papers=[
            PaperItem(
                id="paper_001",
                title="Attention Is All You Need",
                venue="NeurIPS",
                year=2017,
                reason="Essential for understanding transformer-based architectures and current model design.",
                tags=["Transformers", "Sequence Modeling"],
            ),
            PaperItem(
                id="paper_002",
                title="Graph Attention Networks",
                venue="ICLR",
                year=2018,
                reason="Relevant to your graph-driven recommendation direction.",
                tags=["Graphs", "Attention", "Embeddings"],
            ),
            PaperItem(
                id="paper_003",
                title="A Survey on Knowledge Graph Embeddings",
                venue="IEEE",
                year=2022,
                reason="Connects directly to your proposed recommendation engine and graph learning setup.",
                tags=["Knowledge Graph", "Embeddings", "Survey"],
            ),
        ],
        jobs=[
            JobItem(
                id="job_001",
                title="Machine Learning Engineer Intern",
                company="Nexa Labs",
                fit="Strong fit",
                reason="Good bridge role while you deepen graph learning and research communication.",
                tags=["Python", "ML Ops", "Experimentation"],
            ),
            JobItem(
                id="job_002",
                title="Applied AI Research Assistant",
                company="Insight AI Lab",
                fit="Target fit",
                reason="Aligns closely with your goal.",
                tags=["Research", "Evaluation", "Deep Learning"],
            ),
            JobItem(
                id="job_003",
                title="Knowledge Graph Engineer",
                company="DataWeave",
                fit="Emerging fit",
                reason="Great long-term match if you strengthen graph databases and semantic modeling.",
                tags=["Neo4j", "Graphs", "Semantic Search"],
            ),
        ],
        recommendation_paths=[
            "Python -> Machine Learning -> Deep Learning Systems Course -> Applied AI Research Assistant",
            "Machine Learning -> Graph Theory -> Graph Attention Networks -> Knowledge Graph Engineer",
            "Deep Learning -> Research Methodology -> Scientific Writing for AI -> Publishable Project Direction",
        ],
        missing_skills=[
            MissingSkillItem(name="Graph Theory", priority="High", progress=38, reason="Needed for graph traversal and graph learning."),
            MissingSkillItem(name="Research Methodology", priority="High", progress=44, reason="Improves experiment design and evaluation quality."),
            MissingSkillItem(name="Neo4j Cypher", priority="Medium", progress=51, reason="Important for graph querying and explainable recommendation paths."),
            MissingSkillItem(name="Model Evaluation", priority="Medium", progress=58, reason="Supports precision, recall, diversity, and cross-domain comparison work."),
        ],
    )


def get_skill_gap_payload() -> SkillGapPayload:
    return SkillGapPayload(
        career_goal="AI Researcher",
        summary="Blend advanced learning, research depth, and real-world problem solving into a focused AI career path.",
        focus_areas=["Representation learning", "Research communication", "Model deployment awareness"],
        current_skill_count=4,
        gap_count=4,
        missing_skills=[
            SkillGapMissingSkillItem(name="Graph Theory", priority="High", progress=38, reason="Needed for understanding graph traversal, graph learning, and relationship modeling."),
            SkillGapMissingSkillItem(name="Research Methodology", priority="High", progress=44, reason="Improves experiment design and publishable evaluation."),
            SkillGapMissingSkillItem(name="Neo4j Cypher", priority="Medium", progress=51, reason="Important for graph querying and recommendation explainability."),
            SkillGapMissingSkillItem(name="Model Evaluation", priority="Medium", progress=58, reason="Supports precision, recall, and diversity analysis."),
        ],
        roadmap=[
            RoadmapStep(phase="Strengthen foundations", timeline="Weeks 1-3", action="Focus on graph theory, ranking metrics, and graph queries."),
            RoadmapStep(phase="Build cross-domain understanding", timeline="Weeks 4-6", action="Link courses, papers, and jobs through shared skills and recommendation signals."),
            RoadmapStep(phase="Prototype recommendation logic", timeline="Weeks 7-9", action="Implement path-based explanation and embedding-driven similarity ranking."),
        ],
        bridges=SkillGapBridges(
            courses=[
                FocusBridgeItem(id="course_002", title="Graph Neural Networks in Practice", reason="Supports graph-based recommendation work."),
                FocusBridgeItem(id="course_003", title="Scientific Writing for AI", reason="Improves research communication and publication readiness."),
            ],
            papers=[
                FocusBridgeItem(id="paper_003", title="A Survey on Knowledge Graph Embeddings", reason="Connects directly to graph learning setup."),
                FocusBridgeItem(id="paper_002", title="Graph Attention Networks", reason="Strengthens graph-based research understanding."),
            ],
            jobs=[
                FocusBridgeItem(id="job_003", title="Knowledge Graph Engineer", reason="Great long-term fit if graph skills improve."),
                FocusBridgeItem(id="job_002", title="Applied AI Research Assistant", reason="Aligns with deeper research and evaluation skills."),
            ],
        ),
    )


def get_graph_payload() -> GraphPayload:
    return GraphPayload(
        career_goal="AI Researcher",
        nodes=[
            GraphNode(id="user", label="User", type="user", x=10, y=50),
            GraphNode(id="python", label="Python", type="skill", x=28, y=28),
            GraphNode(id="ml", label="Machine Learning", type="skill", x=28, y=72),
            GraphNode(id="gnnCourse", label="GNN Course", type="course", x=48, y=24),
            GraphNode(id="dlCourse", label="Deep Learning Course", type="course", x=48, y=76),
            GraphNode(id="gatPaper", label="GAT Paper", type="paper", x=68, y=34),
            GraphNode(id="kgSurvey", label="KG Embeddings Survey", type="paper", x=68, y=74),
            GraphNode(id="researchJob", label="AI Research Assistant", type="job", x=88, y=50),
        ],
        edges=[
            GraphEdge(from_="user", to="python", label="has skill"),
            GraphEdge(from_="user", to="ml", label="has skill"),
            GraphEdge(from_="python", to="gnnCourse", label="prerequisite for"),
            GraphEdge(from_="ml", to="dlCourse", label="strengthens"),
            GraphEdge(from_="gnnCourse", to="gatPaper", label="leads to"),
            GraphEdge(from_="dlCourse", to="kgSurvey", label="supports"),
            GraphEdge(from_="gatPaper", to="researchJob", label="relevant to"),
            GraphEdge(from_="kgSurvey", to="researchJob", label="builds toward"),
        ],
        recommendation_paths=[
            "Python -> Machine Learning -> Deep Learning Systems Course -> Applied AI Research Assistant",
            "Machine Learning -> Graph Theory -> Graph Attention Networks -> Knowledge Graph Engineer",
        ],
        legend=GraphLegend(
            user="User profile and goal",
            skill="Current or missing skill",
            course="Recommended learning content",
            paper="Relevant research material",
            job="Career outcome or role match",
        ),
    )


def get_evaluation_metrics() -> EvaluationMetricsPayload:
    return EvaluationMetricsPayload(
        precision_at_k=0.78,
        recall_at_k=0.71,
        diversity_score=0.66,
        cross_domain_alignment=0.74,
    )


def get_recommendation_explanations() -> list[RecommendationExplanation]:
    return [
        RecommendationExplanation(
            target_id="job_002",
            target_type="job",
            explanation_path=["Python", "Machine Learning", "Deep Learning Systems", "Applied AI Research Assistant"],
        )
    ]
