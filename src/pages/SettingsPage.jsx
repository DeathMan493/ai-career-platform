import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import { useAppData } from "../context/AppContext";

function SettingsPage() {
    const navigate = useNavigate();
    const {
        profile,
        session,
        settings,
        updateSettings,
        resetSettings,
        logout
    } = useAppData();
    const [message, setMessage] = useState("");

    function handleThemeChange(event) {
        updateSettings({ theme: event.target.value });
        setMessage("Theme preference saved locally.");
    }

    function handleToggle(key) {
        updateSettings({ [key]: !settings[key] });
        setMessage("Settings updated for this browser.");
    }

    function handleReset() {
        resetSettings();
        setMessage("Preferences reset to default settings.");
    }

    function handleLogout() {
        logout();
        navigate("/");
    }

    return (
        <AppLayout currentPath="/settings" title="Settings" badge="Customize your workspace">
            <p className="profile-lead">
                Control how the platform looks and behaves while we keep the backend-focused features for the next phase.
            </p>

            <section className="settings-grid">
                <article className="card settings-card">
                    <span className="section-label">Appearance</span>
                    <h3>Workspace preferences</h3>

                    <label className="settings-field">
                        <span>Theme mode</span>
                        <select value={settings.theme} onChange={handleThemeChange}>
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                        </select>
                    </label>

                    <label className="toggle-row">
                        <div>
                            <strong>Compact layout</strong>
                            <p>Reduce spacing to fit more cards and content on screen.</p>
                        </div>
                        <button
                            type="button"
                            className={`toggle-switch${settings.compactMode ? " on" : ""}`}
                            onClick={() => handleToggle("compactMode")}
                            aria-pressed={settings.compactMode}
                        >
                            <span></span>
                        </button>
                    </label>
                </article>

                <article className="card settings-card">
                    <span className="section-label">Recommendations</span>
                    <h3>Insight controls</h3>

                    <label className="toggle-row">
                        <div>
                            <strong>Show explainable paths</strong>
                            <p>Display the reasoning chains behind graph and dashboard recommendations.</p>
                        </div>
                        <button
                            type="button"
                            className={`toggle-switch${settings.showExplainablePaths ? " on" : ""}`}
                            onClick={() => handleToggle("showExplainablePaths")}
                            aria-pressed={settings.showExplainablePaths}
                        >
                            <span></span>
                        </button>
                    </label>

                    <label className="toggle-row">
                        <div>
                            <strong>Email roadmap digest</strong>
                            <p>Keep this on as a future-ready preference for progress reminders and milestone summaries.</p>
                        </div>
                        <button
                            type="button"
                            className={`toggle-switch${settings.emailDigest ? " on" : ""}`}
                            onClick={() => handleToggle("emailDigest")}
                            aria-pressed={settings.emailDigest}
                        >
                            <span></span>
                        </button>
                    </label>
                </article>
            </section>

            <section className="settings-grid">
                <article className="card settings-card">
                    <span className="section-label">Account</span>
                    <h3>Current session</h3>
                    <div className="settings-summary">
                        <div>
                            <span>Name</span>
                            <strong>{session?.user?.name || profile.name}</strong>
                        </div>
                        <div>
                            <span>Email</span>
                            <strong>{session?.user?.email || "Signed in session available"}</strong>
                        </div>
                        <div>
                            <span>Career goal</span>
                            <strong>{profile.careerGoal}</strong>
                        </div>
                    </div>
                </article>

                <article className="card settings-card danger-card">
                    <span className="section-label">Session</span>
                    <h3>Account actions</h3>
                    <p>Use logout to return to the auth screen. Your local preferences stay saved unless you reset them.</p>
                    <div className="settings-actions">
                        <button type="button" className="secondary-btn" onClick={handleReset}>Reset Preferences</button>
                        <button type="button" className="danger-btn" onClick={handleLogout}>Logout</button>
                    </div>
                    {message ? <p className="profile-message">{message}</p> : null}
                </article>
            </section>
        </AppLayout>
    );
}

export default SettingsPage;
