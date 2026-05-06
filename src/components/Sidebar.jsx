import { NavLink } from "react-router-dom";

const navItems = [
    { label: "Dashboard", to: "/dashboard" },
    { label: "Profile", to: "/profile" },
    { label: "Courses", to: "/courses" },
    { label: "Papers", to: "/papers" },
    { label: "Skill Gap", to: "/skill-gap" },
    { label: "Graph View", to: "/graph" },
    { label: "Settings", to: "/settings" }
];

function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <h2>AI Platform</h2>
                <p>Learning, research, and career intelligence in one flow.</p>
            </div>

            <nav>
                <ul className="sidebar-nav">
                    {navItems.map((item) => (
                        <li key={item.to}>
                            <NavLink
                                to={item.to}
                                className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
                            >
                                {item.label}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
        </aside>
    );
}

export default Sidebar;
