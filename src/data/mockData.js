export const defaultProfile = {
    name: "Amrita User",
    careerGoal: "AI Researcher",
    skills: [
        { skill: "Python", level: "Advanced" },
        { skill: "Machine Learning", level: "Advanced" },
        { skill: "Data Structures", level: "Intermediate" },
        { skill: "Deep Learning", level: "Intermediate" }
    ]
};

export const knowledgeData = {
    roleSummary: {
        title: "AI Researcher",
        mission: "Blend advanced learning, research depth, and real-world problem solving into a focused AI career path.",
        focusAreas: ["Representation learning", "Research communication", "Model deployment awareness"]
    },
    courses: [
        {
            title: "Advanced Deep Learning Systems",
            provider: "Coursera",
            level: "Advanced",
            duration: "8 weeks",
            reason: "Builds stronger model design intuition for your research-focused goal.",
            tags: ["Neural Networks", "Optimization", "PyTorch"]
        },
        {
            title: "Graph Neural Networks in Practice",
            provider: "edX",
            level: "Intermediate",
            duration: "6 weeks",
            reason: "Directly supports graph-based recommendation and knowledge representation work.",
            tags: ["GNN", "Knowledge Graphs", "Applications"]
        },
        {
            title: "Scientific Writing for AI",
            provider: "FutureLearn",
            level: "Intermediate",
            duration: "4 weeks",
            reason: "Helps turn experiments into strong papers and reproducible research output.",
            tags: ["Research", "Writing", "Evaluation"]
        }
    ],
    papers: [
        {
            title: "Attention Is All You Need",
            venue: "NeurIPS",
            year: "2017",
            reason: "Essential for understanding transformer-based architectures and current model design.",
            tags: ["Transformers", "Sequence Modeling"]
        },
        {
            title: "Graph Attention Networks",
            venue: "ICLR",
            year: "2018",
            reason: "Relevant to your graph-driven recommendation and representation learning direction.",
            tags: ["Graphs", "Attention", "Embeddings"]
        },
        {
            title: "A Survey on Knowledge Graph Embeddings",
            venue: "IEEE",
            year: "2022",
            reason: "Connects directly to your proposed recommendation engine and graph learning setup.",
            tags: ["Knowledge Graph", "Embeddings", "Survey"]
        }
    ],
    jobs: [
        {
            title: "Machine Learning Engineer Intern",
            company: "Nexa Labs",
            fit: "Strong fit",
            reason: "Good bridge role while you deepen graph learning and research communication.",
            tags: ["Python", "ML Ops", "Experimentation"]
        },
        {
            title: "Applied AI Research Assistant",
            company: "Insight AI Lab",
            fit: "Target fit",
            reason: "Aligns closely with your goal and rewards paper reading plus experimentation discipline.",
            tags: ["Research", "Evaluation", "Deep Learning"]
        },
        {
            title: "Knowledge Graph Engineer",
            company: "DataWeave",
            fit: "Emerging fit",
            reason: "Great long-term match if you strengthen graph databases and semantic modeling.",
            tags: ["Neo4j", "Graphs", "Semantic Search"]
        }
    ],
    missingSkills: [
        {
            name: "Graph Theory",
            priority: "High",
            progress: 38,
            reason: "Needed for understanding graph traversal, graph learning, and relationship modeling."
        },
        {
            name: "Research Methodology",
            priority: "High",
            progress: 44,
            reason: "Improves experiment design, reproducibility, and publishable evaluation."
        },
        {
            name: "Neo4j Cypher",
            priority: "Medium",
            progress: 51,
            reason: "Important for graph querying and explainable recommendation paths."
        },
        {
            name: "Model Evaluation",
            priority: "Medium",
            progress: 58,
            reason: "Supports precision, recall, diversity, and cross-domain comparison work."
        }
    ],
    roadmap: [
        {
            phase: "Strengthen foundations",
            timeline: "Weeks 1-3",
            action: "Focus on graph theory, ranking metrics, and graph database querying."
        },
        {
            phase: "Build cross-domain understanding",
            timeline: "Weeks 4-6",
            action: "Link courses, papers, and jobs through common skills and recommendation signals."
        },
        {
            phase: "Prototype recommendation logic",
            timeline: "Weeks 7-9",
            action: "Implement path-based explanation and embedding-driven similarity ranking."
        }
    ],
    recommendationPaths: [
        "Python -> Machine Learning -> Deep Learning Systems Course -> Applied AI Research Assistant",
        "Machine Learning -> Graph Theory -> Graph Attention Networks -> Knowledge Graph Engineer",
        "Deep Learning -> Research Methodology -> Scientific Writing for AI -> Publishable Project Direction"
    ],
    graph: {
        nodes: [
            { id: "user", label: "User", type: "user", x: 10, y: 50 },
            { id: "python", label: "Python", type: "skill", x: 28, y: 28 },
            { id: "ml", label: "Machine Learning", type: "skill", x: 28, y: 72 },
            { id: "gnnCourse", label: "GNN Course", type: "course", x: 48, y: 24 },
            { id: "dlCourse", label: "Deep Learning Course", type: "course", x: 48, y: 76 },
            { id: "gatPaper", label: "GAT Paper", type: "paper", x: 68, y: 34 },
            { id: "kgSurvey", label: "KG Embeddings Survey", type: "paper", x: 68, y: 74 },
            { id: "researchJob", label: "AI Research Assistant", type: "job", x: 88, y: 50 }
        ],
        edges: [
            { from: "user", to: "python", label: "has skill" },
            { from: "user", to: "ml", label: "has skill" },
            { from: "python", to: "gnnCourse", label: "prerequisite for" },
            { from: "ml", to: "dlCourse", label: "strengthens" },
            { from: "gnnCourse", to: "gatPaper", label: "leads to" },
            { from: "dlCourse", to: "kgSurvey", label: "supports" },
            { from: "gatPaper", to: "researchJob", label: "relevant to" },
            { from: "kgSurvey", to: "researchJob", label: "builds toward" }
        ]
    }
};

