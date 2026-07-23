// Calls the FastAPI backend
export async function planTrail({ query, difficulty, shortOnly, surprise }) {
  const res = await fetch("/api/trails/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      difficulty,
      short_only: shortOnly,
      surprise,
    }),
  })

  if (res.status === 404) return null // no trail matches
  if (!res.ok) throw new Error(`Trail request failed (${res.status})`)
  return res.json()
}
