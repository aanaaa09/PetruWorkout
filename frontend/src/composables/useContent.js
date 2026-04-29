let cached = null
let cachedAt = 0
const TTL = 60_000

export async function useContent() {
  const now = Date.now()
  if (cached && (now - cachedAt) < TTL) return cached
  try {
    const r = await fetch('/content.json?v=' + now)
    cached = await r.json()
    cachedAt = now
  } catch {
    cached = cached || {}
  }
  return cached
}
