import { useEffect, useRef, useState } from "react";
import AppLayout from "../components/AppLayout";
import { useAppData } from "../context/AppContext";
import { fetchSkillSuggestions } from "../lib/api";

const levels = ["Beginner", "Intermediate", "Advanced"];
let nextSkillDraftId = 0;

function createSkillDraft(skill = "", level = "Beginner") {
    nextSkillDraftId += 1;
    return {
        id: `skill-draft-${nextSkillDraftId}`,
        skill,
        level,
    };
}

function mapProfileSkillsToDrafts(skillItems) {
    return (skillItems || []).map((item) => createSkillDraft(item.skill, item.level));
}

function ProfilePage() {
    const { profile, editableProfile, derivedSkills, profileError, profileLoading, updateProfile } = useAppData();
    const [careerGoal, setCareerGoal] = useState(editableProfile.careerGoal);
    const [skills, setSkills] = useState(() => mapProfileSkillsToDrafts(editableProfile.skills));
    const [activeSkillId, setActiveSkillId] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [suggestionsLoading, setSuggestionsLoading] = useState(false);
    const [message, setMessage] = useState("");
    const latestSuggestionRequest = useRef(0);

    useEffect(() => {
        setCareerGoal(editableProfile.careerGoal);
        setSkills(mapProfileSkillsToDrafts(editableProfile.skills));
    }, [editableProfile]);

    useEffect(() => {
        const activeSkill = skills.find((item) => item.id === activeSkillId);
        const query = activeSkill?.skill?.trim() || "";

        if (!activeSkillId || query.length < 1) {
            setSuggestions([]);
            setSuggestionsLoading(false);
            return;
        }

        const requestId = latestSuggestionRequest.current + 1;
        latestSuggestionRequest.current = requestId;

        const timerId = window.setTimeout(async () => {
            try {
                setSuggestionsLoading(true);
                const response = await fetchSkillSuggestions(query);
                if (latestSuggestionRequest.current !== requestId) {
                    return;
                }

                const selectedSkills = new Set(
                    skills
                        .filter((item) => item.id !== activeSkillId)
                        .map((item) => item.skill.trim().toLowerCase())
                        .filter(Boolean)
                );

                setSuggestions(
                    response.data.items.filter((name) => !selectedSkills.has(name.toLowerCase()))
                );
            } catch {
                if (latestSuggestionRequest.current === requestId) {
                    setSuggestions([]);
                }
            } finally {
                if (latestSuggestionRequest.current === requestId) {
                    setSuggestionsLoading(false);
                }
            }
        }, 180);

        return () => window.clearTimeout(timerId);
    }, [activeSkillId, skills]);

    function handleSkillChange(index, field, value) {
        setSkills((currentSkills) => currentSkills.map((skill, currentIndex) => (
            currentIndex === index ? { ...skill, [field]: value } : skill
        )));
        setMessage("");
    }

    function addSkill() {
        const draft = createSkillDraft("", "Beginner");
        setSkills((currentSkills) => [...currentSkills, draft]);
        setActiveSkillId(draft.id);
    }

    function removeSkill(index) {
        setSkills((currentSkills) => {
            const target = currentSkills[index];
            if (target?.id === activeSkillId) {
                setActiveSkillId(null);
                setSuggestions([]);
            }
            return currentSkills.filter((_, currentIndex) => currentIndex !== index);
        });
    }

    function applySuggestion(index, value) {
        handleSkillChange(index, "skill", value);
        setActiveSkillId(null);
        setSuggestions([]);
    }

    async function handleSave() {
        const result = await updateProfile({
            ...editableProfile,
            careerGoal,
            skills: skills
                .filter((skill) => skill.skill.trim())
                .map(({ skill, level }) => ({ skill, level }))
        });
        setMessage(result.message);
    }

    return (
        <AppLayout currentPath="/profile" title="Profile" badge="Build your direction">
            <p className="profile-lead">
                Define your target role and current strengths so the platform can point you toward
                better courses, jobs, and missing skills.
            </p>
            {profileLoading ? <p className="profile-message">Loading profile from backend...</p> : null}
            {!profileLoading && profileError ? <p className="profile-message">{profileError}</p> : null}

            <section className="profile-grid">
                <div>
                    <article className="card intro-card">
                        <span className="section-label">Career Direction</span>
                        <h3>Career Goal</h3>
                        <input
                            type="text"
                            value={careerGoal}
                            onChange={(event) => setCareerGoal(event.target.value)}
                            placeholder="e.g. AI Researcher"
                        />
                        <p className="goal-helper">
                            Choose a role that reflects the kind of work you want to grow into.
                        </p>
                    </article>

                    <article className="card">
                        <span className="section-label">Skills Inventory</span>
                        <h3>Skills</h3>

                        <div className="skills-container">
                            {skills.map((item, index) => (
                                <div className="skill-row" key={item.id}>
                                    <div className="skill-input-stack">
                                        <input
                                            type="text"
                                            placeholder="Skill"
                                            value={item.skill}
                                            onFocus={() => setActiveSkillId(item.id)}
                                            onBlur={() => {
                                                window.setTimeout(() => {
                                                    setActiveSkillId((current) => (current === item.id ? null : current));
                                                    setSuggestions([]);
                                                }, 140);
                                            }}
                                            onChange={(event) => {
                                                setActiveSkillId(item.id);
                                                handleSkillChange(index, "skill", event.target.value);
                                            }}
                                        />

                                        {activeSkillId === item.id && (suggestionsLoading || suggestions.length > 0) ? (
                                            <div className="skill-suggestions">
                                                {suggestionsLoading ? (
                                                    <button type="button" className="skill-suggestion muted-suggestion" tabIndex={-1}>
                                                        Finding matching skills...
                                                    </button>
                                                ) : (
                                                    suggestions.map((suggestion) => (
                                                        <button
                                                            key={`${item.id}-${suggestion}`}
                                                            type="button"
                                                            className="skill-suggestion"
                                                            onMouseDown={(event) => {
                                                                event.preventDefault();
                                                                applySuggestion(index, suggestion);
                                                            }}
                                                        >
                                                            {suggestion}
                                                        </button>
                                                    ))
                                                )}
                                            </div>
                                        ) : null}
                                    </div>

                                    <select
                                        value={item.level}
                                        onChange={(event) => handleSkillChange(index, "level", event.target.value)}
                                    >
                                        {levels.map((level) => (
                                            <option key={level} value={level}>{level}</option>
                                        ))}
                                    </select>

                                    <button type="button" onClick={() => removeSkill(index)}>Remove</button>
                                </div>
                            ))}
                        </div>

                        <button type="button" className="add-skill-btn" onClick={addSkill}>+ Add Skill</button>
                    </article>
                </div>

                <article className="card">
                    <span className="section-label">Auto Progress</span>
                    <h3>Skills unlocked by completed work</h3>
                    {derivedSkills.length ? (
                        <div className="auto-skill-list">
                            {derivedSkills.map((skill) => (
                                <div className="auto-skill-card" key={skill.skill}>
                                    <strong>{skill.skill}</strong>
                                    <span>{skill.level}</span>
                                    <p>{skill.progress}% progress from completed courses and papers.</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="goal-helper">
                            Complete recommended courses or mark research papers as read to auto-surface new skills here.
                        </p>
                    )}
                </article>

                <article className="card">
                    <span className="section-label">Tips</span>
                    <h3>Make your profile sharper</h3>
                    <ul className="tip-list">
                        <li>Add the skills you can already use confidently.</li>
                        <li>Choose levels honestly so recommendations stay useful.</li>
                        <li>Update this as you complete projects and courses.</li>
                    </ul>
                    <button type="button" className="save-btn" onClick={handleSave}>Save Profile</button>
                    {message ? <p className="profile-message">{message}</p> : null}
                </article>
            </section>
        </AppLayout>
    );
}

export default ProfilePage;
