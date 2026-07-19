function renderBold(text) {
  return (
    <>
      {text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i}>{part.slice(2, -2)}</strong>
        ) : (
          part
        )
      )}
    </>
  );
}

function splitNotice(itinerary) {
  if (!itinerary) return { notice: null, body: "" };
  const idx = itinerary.indexOf("Recommended trail:");
  if (idx > 0) {
    return {
      notice: itinerary.slice(0, idx).trim() || null,
      body: itinerary.slice(idx).trim(),
    };
  }
  return { notice: null, body: itinerary };
}

export default function ItineraryCard({ trail }) {
  if (!trail) return null;

  const { notice, body } = splitNotice(trail.itinerary);

  return (
    <div className="tt-itinerary">
       {notice && <div className="tt-notice">{notice}</div>}
      <div className="tt-itinerary-head">
        <div className="tt-itinerary-label">Suggested itinerary</div>
        <span className="tt-chip" style={{ background: trail.chipBg, color: trail.chipFg }}>
          {trail.difficulty}
        </span>
      </div>

      <div className="tt-trail-name">{trail.name}</div>
      <div className="tt-trail-location">{trail.location}</div>

      <div className="tt-stat-grid">
        <div>
          <div className="tt-stat-label">Distance</div>
          <div className="tt-stat-value">{trail.distance}</div>
        </div>
        <div>
          <div className="tt-stat-label">On foot</div>
          <div className="tt-stat-value">{trail.time}</div>
        </div>
      </div>

      <div className="tt-station-box">
        <div className="tt-station-icon" />
        <div>
          <div className="tt-station-name">{trail.station} station</div>
          <div className="tt-station-gap">{trail.gap} to the trailhead</div>
        </div>
      </div>

      <div className="tt-desc">{trail.description}</div>
      {body && (<div className="tt-desc tt-itinerary-text">{renderBold(body)}</div>)}
    </div>
  );
}
