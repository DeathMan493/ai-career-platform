import Sidebar from "./Sidebar";

function AppLayout({ currentPath, title, badge, children }) {
    return (
        <div className="app-shell">
            <Sidebar currentPath={currentPath} />
            <main className="main-panel">
                <header className="page-topbar">
                    <h1>{title}</h1>
                    {badge ? <span className="topbar-badge">{badge}</span> : null}
                </header>
                {children}
            </main>
        </div>
    );
}

export default AppLayout;
