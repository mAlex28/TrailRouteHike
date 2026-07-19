"use client"

import { useCallback, useEffect, useState } from "react"
import { planTrail } from "../lib/api"

const DEFAULT_QUERY = "I'd like to hike near Bath"

export function useTrailPlanner() {
  const [query, setQuery] = useState(DEFAULT_QUERY)
  const [difficulty, setDifficulty] = useState("all")
  const [shortOnly, setShortOnly] = useState(false)
  const [trail, setTrail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const plan = useCallback(
    async (surprise = false) => {
      setLoading(true)
      setError(null)
      try {
        const result = await planTrail({
          query,
          difficulty,
          shortOnly,
          surprise,
        })
        setTrail(result)
      } catch (err) {
        console.error(err)
        setError(
          "Couldn't reach the trail planner. Make sure the backend is running.",
        )
      } finally {
        setLoading(false)
      }
    },
    [query, difficulty, shortOnly],
  )

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
    loading,
    error,
    plan,
  }
}
