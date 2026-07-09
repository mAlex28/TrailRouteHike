const DIFFICULTIES = [
  ['all', 'All'],
  ['Easy', 'Easy'],
  ['Moderate', 'Moderate'],
  ['Hard', 'Hard'],
];

export default function DifficultyPills({ active, onChange }) {
  return (
    <div className="tt-pill-row">
      {DIFFICULTIES.map(([key, label]) => (
        <button
          key={key}
          type="button"
          className={`tt-pill${active === key ? ' is-active' : ''}`}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
