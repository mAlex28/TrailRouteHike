import { haversineKm } from "./haversine"

const DIFFICULTY_PALETTE = {
  Easy: { bg: "#e3efe4", fg: "#2f7a4d" },
  Moderate: { bg: "#f4ecd8", fg: "#9a7320" },
  Hard: { bg: "#f3e2dc", fg: "#a8432a" },
}

export function formatTrail(trail, units = "mi") {
  if (!trail) return null

  const useKm = units === "km"
  const distance = useKm
    ? `${trail.distanceKm.toFixed(trail.distanceKm < 100 ? 1 : 0)} km`
    : `${trail.distanceMi} mi`

  const gapKmRaw = haversineKm(trail.stationCoords, trail.trailCoords)
  const gap = useKm
    ? `${gapKmRaw.toFixed(1)} km`
    : `${(gapKmRaw * 0.621371).toFixed(1)} mi`

  const time =
    trail.distanceMi > 25
      ? `${Math.ceil(trail.distanceMi / 15)}-day route`
      : `${Math.max(1, Math.round(trail.distanceMi / 2.4))} hr walk`

  const palette =
    DIFFICULTY_PALETTE[trail.difficulty] || DIFFICULTY_PALETTE.Moderate

  return {
    ...trail,
    distance,
    time,
    gap,
    chipBg: palette.bg,
    chipFg: palette.fg,
  }
}
