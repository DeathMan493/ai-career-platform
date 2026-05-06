import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppData } from "../context/AppContext";
import { exchangeFirebaseToken } from "../lib/api";
import { signInWithFirebase, signInWithGoogle, signUpWithFirebase } from "../lib/firebase";

function GoogleMark() {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" className="google-mark">
            <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.7 3.9-5.5 3.9-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.6-2.5C16.8 3.4 14.6 2.5 12 2.5 6.8 2.5 2.5 6.8 2.5 12S6.8 21.5 12 21.5c6.9 0 9.2-4.8 9.2-7.3 0-.5-.1-.9-.1-1.3H12z" />
            <path fill="#34A853" d="M2.5 7.8l3.2 2.3C6.6 7.6 9.1 5.9 12 5.9c1.9 0 3.2.8 3.9 1.5l2.6-2.5C16.8 3.4 14.6 2.5 12 2.5 8.2 2.5 4.9 4.6 2.5 7.8z" />
            <path fill="#FBBC05" d="M12 21.5c2.5 0 4.7-.8 6.3-2.3l-2.9-2.4c-.8.6-1.9 1.1-3.4 1.1-3.7 0-5.2-2.5-5.5-3.8l-3.2 2.5c2.3 4.3 6 4.9 8.7 4.9z" />
            <path fill="#4285F4" d="M21.2 14.2c.1-.4.1-.8.1-1.3s0-.9-.1-1.3H12v3.9h5.5c-.3 1.2-1.2 2.2-2.3 2.9l2.9 2.4c1.7-1.5 3.1-3.8 3.1-6.6z" />
        </svg>
    );
}

function AuthPage() {
    const [mode, setMode] = useState("login");
    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const { startSession } = useAppData();

    async function completeAuth(authResult) {
        const response = await exchangeFirebaseToken(authResult.idToken);
        startSession({
            token: authResult.idToken,
            user: response.data.user
        });
        setError("");
        navigate("/dashboard");
    }

    async function handleSubmit(event) {
        event.preventDefault();

        let authResult;
        try {
            authResult = mode === "login"
                ? await signInWithFirebase({
                    email: form.email,
                    password: form.password
                })
                : await signUpWithFirebase({
                    name: form.name,
                    email: form.email,
                    password: form.password
                });
        } catch {
            setError("Authentication failed. Check your email, password, or provider setup.");
            return;
        }

        try {
            await completeAuth(authResult);
        } catch {
            setError("Sign-in worked, but backend session sync failed. Restart the backend and check allowed origins.");
        }
    }

    async function handleGoogleSignIn() {
        let authResult;
        try {
            authResult = await signInWithGoogle();
        } catch {
            setError("Google sign-in failed. Check that Google provider is enabled and this domain is allowed in Firebase.");
            return;
        }

        try {
            await completeAuth(authResult);
        } catch {
            setError("Google sign-in worked, but backend session sync failed. Restart the backend and check allowed origins.");
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-shell">
                <section className="auth-showcase">
                    <div className="eyebrow">Career OS</div>
                    <h1>Shape your path into AI with clarity.</h1>
                    <p>
                        Track goals, identify missing skills, and stay focused with a dashboard built for
                        steady progress across learning, research, and career growth.
                    </p>

                    <div className="feature-list">
                        <div className="feature-item">
                            <strong>Personalized guidance</strong>
                            <span>Set a target role and keep your learning aligned.</span>
                        </div>
                        <div className="feature-item">
                            <strong>Skill gap visibility</strong>
                            <span>See which skills and resources deserve attention next.</span>
                        </div>
                        <div className="feature-item">
                            <strong>Progress with structure</strong>
                            <span>Bring courses, papers, jobs, and planning into one place.</span>
                        </div>
                    </div>
                </section>

                <section className="form-container">
                    <form className="form active" onSubmit={handleSubmit}>
                        <div className="form-heading">
                            <h2>{mode === "login" ? "Welcome back" : "Create account"}</h2>
                            <p>
                                {mode === "login"
                                    ? "Log in to continue building your roadmap."
                                    : "Start your personalized learning and career dashboard."}
                            </p>
                        </div>

                        {mode === "signup" ? (
                            <input
                                type="text"
                                placeholder="Full Name"
                                required
                                value={form.name}
                                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                            />
                        ) : null}
                        <input
                            type="email"
                            placeholder="Email"
                            required
                            value={form.email}
                            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            required
                            value={form.password}
                            onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                        />
                        <button type="submit">{mode === "login" ? "Login" : "Sign Up"}</button>

                        <p className="auth-switch">
                            {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
                            <button
                                type="button"
                                className="inline-action"
                                onClick={() => setMode(mode === "login" ? "signup" : "login")}
                            >
                                {mode === "login" ? "Sign up" : "Login"}
                            </button>
                        </p>

                        <div className="auth-divider">
                            <span>or continue with</span>
                        </div>

                        <button type="button" className="social-btn google-btn" onClick={handleGoogleSignIn}>
                            <GoogleMark />
                            <span>Continue with Google</span>
                        </button>

                        {error ? <p className="profile-message">{error}</p> : null}
                    </form>
                </section>
            </div>
        </div>
    );
}

export default AuthPage;
