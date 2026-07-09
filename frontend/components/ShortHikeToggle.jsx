export default function ShortHikeToggle({ on, onToggle }) {
  return (
    <button type="button" className="tt-short-toggle" onClick={onToggle}>
      <span className={`tt-track${on ? ' is-on' : ''}`}>
        <span className="tt-knob" />
      </span>
      <span className="tt-short-label">
        Only short hikes <span>(under 5 miles)</span>
      </span>
    </button>
  );
}
