import DifficultyPills from './DifficultyPills';
import ShortHikeToggle from './ShortHikeToggle';

export default function SearchPanel({
  query,
  onQueryChange,
  difficulty,
  onDifficultyChange,
  shortOnly,
  onToggleShort,
  onPlan,
  onSurprise,
  loading,
}) {
  return (
    <>
      <div className="tt-heading">
        Where do you
        <br />
        want to walk?
      </div>
      <div className="tt-subheading">Where is your next adventure?</div>

      <input
        type="text"
        className="tt-input"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="e.g. near Southampton"
      />

      <div className="tt-label-mono">Difficulty</div>
      <DifficultyPills active={difficulty} onChange={onDifficultyChange} />

      <ShortHikeToggle on={shortOnly} onToggle={onToggleShort} />

      <div className="tt-actions">
        <button type="button" className="tt-plan-btn" onClick={onPlan} disabled={loading}>
          {loading ? "Planning…" : "Plan my hike"}
        </button>
        <button type="button" className="tt-surprise-btn" onClick={onSurprise} disabled={loading}>
          Surprise me
        </button>
      </div>
    </>
  );
}
