"use client"

import { useCallback, useEffect, useState } from "react"
import { planTrail } from "../lib/trails"

const DEFAULT_QUERY = "I'd like to hike near Bath"

// Drives the search form + itinerary result against the dummy trail dataset.
export function useTrailPlanner() {
  const [query, setQuery] = useState(DEFAULT_QUERY)
  const [difficulty, setDifficulty] = useState("all")
  const [shortOnly, setShortOnly] = useState(false)
  const [trail, setTrail] = useState(null)

  const plan = useCallback(
    (surprise = false) => {
      setTrail(planTrail({ query, difficulty, shortOnly, surprise }))
    },
    [query, difficulty, shortOnly],
  )

  // Show a default itinerary on first load.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    plan(false)
  }, [])

  return {
    query,
    setQuery,
    difficulty,
    setDifficulty,
    shortOnly,
    setShortOnly,
    trail,
    plan,
  }
}
