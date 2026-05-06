function ResourceCard({ item, meta, actionLabel, onAction, actionDisabled = false }) {
    return (
        <li className="resource-item">
            <h4>{item.title}</h4>
            <div className="resource-meta">{meta}</div>
            <p>{item.reason}</p>
            <div className="tag-row">
                {item.tags.map((tag) => (
                    <span key={tag} className="tag">{tag}</span>
                ))}
            </div>
            {actionLabel ? (
                <button type="button" className="resource-action-btn" onClick={onAction} disabled={actionDisabled}>
                    {actionLabel}
                </button>
            ) : null}
        </li>
    );
}

export default ResourceCard;
