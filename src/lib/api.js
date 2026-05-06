const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const SESSION_STORAGE_KEY = "ai-platform-session";

function getStoredSessionToken() {
    try {
        const savedValue = localStorage.getItem(SESSION_STORAGE_KEY);
        if (!savedValue) {
            return null;
        }
        const session = JSON.parse(savedValue);
        return session?.token || null;
    } catch {
        return null;
    }
}

async function request(path, options = {}) {
    const sessionToken = getStoredSessionToken();
    const headers = {
        "Content-Type": "application/json",
        ...(sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {}),
        ...(options.headers || {})
    };

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        throw new Error("Request failed");
    }

    return response.json();
}

function buildPaginationQuery(page = 1, limit = 10) {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("limit", String(limit));
    return params;
}

export async function exchangeFirebaseToken(idToken) {
    return request("/auth/firebase", {
        method: "POST",
        body: JSON.stringify({ id_token: idToken })
    });
}

export async function fetchProfile() {
    return request("/profile/me");
}

export async function fetchProgress() {
    return request("/progress");
}

export async function fetchSkillSuggestions(query, page = 1, limit = 8) {
    const params = buildPaginationQuery(page, limit);
    if (query) {
        params.set("q", query);
    }
    return request(`/skills/suggest?${params.toString()}`);
}

export async function updateProfile(payload) {
    return request("/profile/me", {
        method: "PUT",
        body: JSON.stringify(payload)
    });
}

export async function completeCourse(payload) {
    return request("/progress/courses/complete", {
        method: "POST",
        body: JSON.stringify(payload)
    });
}

export async function removeCompletedCourse(itemId) {
    return request("/progress/courses/remove", {
        method: "POST",
        body: JSON.stringify({ item_id: itemId })
    });
}

export async function completePaper(payload) {
    return request("/progress/papers/complete", {
        method: "POST",
        body: JSON.stringify(payload)
    });
}

export async function removeCompletedPaper(itemId) {
    return request("/progress/papers/remove", {
        method: "POST",
        body: JSON.stringify({ item_id: itemId })
    });
}

export async function fetchDashboard() {
    return request("/dashboard");
}

export async function fetchCourseRecommendations(limit = 10, page = 1) {
    return request(`/courses?${buildPaginationQuery(page, limit).toString()}`);
}

export async function fetchPaperRecommendations(limit = 10, page = 1) {
    return request(`/papers?${buildPaginationQuery(page, limit).toString()}`);
}

export async function fetchSkillGap() {
    return request("/skill-gap");
}

export async function fetchGraph() {
    return request("/graph");
}

export { API_BASE_URL };
