let cached = null

export async function useContent() {
  if (cached) return cached
  try {
    const r = await fetch('/content.json?v=' + Date.now())
    cached = await r.json()
  } catch {
    cached = {}
  }
  return cached
}
