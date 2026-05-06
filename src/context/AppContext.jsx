import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { defaultProfile, knowledgeData } from "../data/mockData";
import {
    completeCourse,
    completePaper,
    exchangeFirebaseToken,
    fetchProfile as fetchProfileRequest,
    fetchProgress as fetchProgressRequest,
    removeCompletedCourse,
    removeCompletedPaper,
    updateProfile as updateProfileRequest
} from "../lib/api";
import { signOutFirebase, subscribeToAuthChanges } from "../lib/firebase";
import { deriveSkillState } from "../lib/skillProgress";

const PROFILE_STORAGE_KEY = "ai-platform-profile";
const SETTINGS_STORAGE_KEY = "ai-platform-settings";
const SESSION_STORAGE_KEY = "ai-platform-session";
const COMPLETION_STORAGE_KEY = "ai-platform-completed-items";

const defaultSettings = {
    theme: "light",
    compactMode: false,
    showExplainablePaths: true,
    emailDigest: true
};

const AppContext = createContext(null);

function loadJson(key, fallback) {
    const savedValue = localStorage.getItem(key);

    if (!savedValue) {
        return fallback;
    }

    try {
        return JSON.parse(savedValue);
    } catch {
        return fallback;
    }
}

function loadProfile() {
    const parsedProfile = loadJson(PROFILE_STORAGE_KEY, defaultProfile);

    return {
        ...defaultProfile,
        ...parsedProfile,
        skills: Array.isArray(parsedProfile.skills)
            ? parsedProfile.skills
            : defaultProfile.skills
    };
}

function loadSettings() {
    return {
        ...defaultSettings,
        ...loadJson(SETTINGS_STORAGE_KEY, {})
    };
}

function loadSession() {
    return loadJson(SESSION_STORAGE_KEY, null);
}

function loadCompletionState() {
    const parsed = loadJson(COMPLETION_STORAGE_KEY, {});
    return {
        courses: Array.isArray(parsed.courses) ? parsed.courses.filter((item) => item && typeof item === "object" && item.id) : [],
        papers: Array.isArray(parsed.papers) ? parsed.papers.filter((item) => item && typeof item === "object" && item.id) : []
    };
}

function normalizeProgressPayload(payload) {
    return {
        courses: payload?.completed_courses || [],
        papers: payload?.completed_papers || []
    };
}

export function AppProvider({ children }) {
    const [baseProfile, setBaseProfile] = useState(loadProfile);
    const [settings, setSettings] = useState(loadSettings);
    const [session, setSession] = useState(loadSession);
    const [completedItems, setCompletedItems] = useState(loadCompletionState);
    const [authReady, setAuthReady] = useState(false);
    const [profileLoading, setProfileLoading] = useState(true);
    const [profileError, setProfileError] = useState("");

    useEffect(() => {
        const unsubscribe = subscribeToAuthChanges(async (firebaseUser) => {
            if (!firebaseUser) {
                setSession(null);
                setBaseProfile(defaultProfile);
                localStorage.removeItem(SESSION_STORAGE_KEY);
                localStorage.removeItem(PROFILE_STORAGE_KEY);
                setProfileLoading(false);
                setAuthReady(true);
                return;
            }

            try {
                const idToken = await firebaseUser.getIdToken();
                const response = await exchangeFirebaseToken(idToken);
                const nextSession = {
                    token: idToken,
                    user: response.data.user
                };

                setSession(nextSession);
                localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(nextSession));
                setProfileError("");
            } catch {
                setProfileError("Signed in with Firebase, but backend session sync failed.");
            } finally {
                setAuthReady(true);
            }
        });

        return () => unsubscribe();
    }, []);

    useEffect(() => {
        async function syncProfile() {
            if (!session?.token) {
                setProfileLoading(false);
                return;
            }

            setProfileLoading(true);
            try {
                const [profileResponse, progressResponse] = await Promise.all([
                    fetchProfileRequest(),
                    fetchProgressRequest()
                ]);
                const apiProfile = profileResponse.data;
                const normalizedProfile = {
                    id: apiProfile.id,
                    name: apiProfile.name,
                    careerGoal: apiProfile.career_goal,
                    skills: apiProfile.skills
                };

                setBaseProfile(normalizedProfile);
                setCompletedItems(normalizeProgressPayload(progressResponse.data));
                localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(normalizedProfile));
                setProfileError("");
            } catch {
                setProfileError("Using local profile fallback because backend profile fetch is unavailable.");
            } finally {
                setProfileLoading(false);
            }
        }

        syncProfile();
    }, [session?.token]);

    useEffect(() => {
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
        document.documentElement.dataset.theme = settings.theme;
        document.body.classList.toggle("compact-ui", settings.compactMode);
    }, [settings]);

    useEffect(() => {
        localStorage.setItem(COMPLETION_STORAGE_KEY, JSON.stringify(completedItems));
    }, [completedItems]);

    const derivedSkillState = useMemo(
        () => deriveSkillState(baseProfile, completedItems),
        [baseProfile, completedItems]
    );

    const profile = derivedSkillState.profile;

    const value = useMemo(() => ({
        profile,
        editableProfile: baseProfile,
        derivedSkills: derivedSkillState.derivedSkills,
        skillProgressMap: derivedSkillState.progressMap,
        settings,
        session,
        completedItems,
        authReady,
        isAuthenticated: Boolean(session?.token),
        profileLoading,
        profileError,
        knowledgeData,
        updateSettings(patch) {
            setSettings((current) => ({ ...current, ...patch }));
        },
        resetSettings() {
            setSettings(defaultSettings);
        },
        async markItemCompleted(kind, item) {
            try {
                const response = kind === "courses"
                    ? await completeCourse(item)
                    : await completePaper(item);
                setCompletedItems(normalizeProgressPayload(response.data));
                return { ok: true };
            } catch {
                setCompletedItems((current) => {
                    const nextValues = current[kind] || [];
                    if (nextValues.some((entry) => entry.id === item.id)) {
                        return current;
                    }
                    return {
                        ...current,
                        [kind]: [...nextValues, item]
                    };
                });
                return { ok: false };
            }
        },
        async unmarkItemCompleted(kind, itemId) {
            try {
                const response = kind === "courses"
                    ? await removeCompletedCourse(itemId)
                    : await removeCompletedPaper(itemId);
                setCompletedItems(normalizeProgressPayload(response.data));
                return { ok: true };
            } catch {
                setCompletedItems((current) => ({
                    ...current,
                    [kind]: (current[kind] || []).filter((value) => value.id !== itemId)
                }));
                return { ok: false };
            }
        },
        startSession(authPayload) {
            const nextSession = {
                token: authPayload?.token || "session-token",
                user: authPayload?.user || null
            };

            setSession(nextSession);
            localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(nextSession));
        },
        logout() {
            signOutFirebase().catch(() => undefined);
            setSession(null);
            setBaseProfile(defaultProfile);
            setCompletedItems({ courses: [], papers: [] });
            localStorage.removeItem(SESSION_STORAGE_KEY);
            localStorage.removeItem(PROFILE_STORAGE_KEY);
            localStorage.removeItem(COMPLETION_STORAGE_KEY);
            setProfileLoading(false);
        },
        async updateProfile(nextProfile) {
            const normalizedPayload = {
                career_goal: nextProfile.careerGoal,
                skills: nextProfile.skills
            };

            try {
                const response = await updateProfileRequest(normalizedPayload);
                const apiProfile = response.data;
                const normalizedProfile = {
                    id: apiProfile.id,
                    name: apiProfile.name,
                    careerGoal: apiProfile.career_goal,
                    skills: apiProfile.skills
                };

                setBaseProfile(normalizedProfile);
                localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(normalizedProfile));
                setProfileError("");
                return { ok: true, message: response.message || "Profile updated" };
            } catch {
                setBaseProfile(nextProfile);
                localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(nextProfile));
                setProfileError("Backend profile update failed, so local state was saved instead.");
                return { ok: false, message: "Saved locally because backend update failed." };
            }
        }
    }), [profile, baseProfile, derivedSkillState, settings, session, completedItems, authReady, profileLoading, profileError]);

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppData() {
    const context = useContext(AppContext);

    if (!context) {
        throw new Error("useAppData must be used within AppProvider");
    }

    return context;
}
