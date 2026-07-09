"use client";

import dynamic from "next/dynamic";
import { useTrailPlanner } from "../hooks/useTrailPlanner";
import { formatTrail } from "../lib/utils/formatTrail";
import Header from "./Header";
import SearchPanel from "./SearchPanel";
import ItineraryCard from "./ItineraryCard";


const MapPanel = dynamic(() => import("./MapPanel"), {
  ssr: false,
  loading: () => <div className="tt-map-wrap" />,
});

const UNITS = "mi";

export default function TrackAndTrailApp() {
  const {
    query, setQuery,
    difficulty, setDifficulty,
    shortOnly, setShortOnly,
    trail, loading, error, plan,
  } = useTrailPlanner();

  const formatted = formatTrail(trail, UNITS);

  return (
    <div className="tt-page">
      <div className="tt-app">
        <div className="tt-card">
          <Header />
          <div className="tt-body">
            <div className="tt-panel">
              <SearchPanel
                query={query}
                onQueryChange={setQuery}
                difficulty={difficulty}
                onDifficultyChange={setDifficulty}
                shortOnly={shortOnly}
                onToggleShort={() => setShortOnly((v) => !v)}
                onPlan={() => plan(false)}
                onSurprise={() => plan(true)}
                loading={loading}
              />
              {error && <div className="tt-error">{error}</div>}
              <ItineraryCard trail={formatted} />
            </div>
            <MapPanel trail={trail} />
          </div>
        </div>
      </div>
    </div>
  );
}
