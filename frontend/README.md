# TrackAndTrail — frontend

```bash
npm install
npm run dev
```

## Project structure

```
app/
  layout.js           root layout: next/font setup (Spectral, Hanken Grotesk,
                       IBM Plex Mono) + metadata
  page.js             renders <TrackAndTrailApp />
  globals.css         theme variables + all component styles
components/
  TrackAndTrailApp.jsx  top-level client component; dynamic ssr:false Leaflet import
  Header.jsx, SearchPanel.jsx, DifficultyPills.jsx, ShortHikeToggle.jsx,
  ItineraryCard.jsx, MapPanel.jsx (plain Leaflet, not react-leaflet)
hooks/
  useTrailPlanner.js  form state + plan()/surprise() against the dummy data
lib/
  trails.js           dummy trail dataset + matching logic
  utils/haversine.js  station→trailhead great-circle distance
  utils/formatTrail.js distance/time/station-gap/difficulty-chip display strings
  theme.js            accent/dark colors (kept in sync with the CSS vars in globals.css)
```
