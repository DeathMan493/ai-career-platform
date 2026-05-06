function SectionIntro({ title, description }) {
    return (
        <div className="section-intro">
            <div>
                <h3>{title}</h3>
                {description ? <p>{description}</p> : null}
            </div>
        </div>
    );
}

export default SectionIntro;
