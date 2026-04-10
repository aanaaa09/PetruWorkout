function detectTrafficSource() {
  const params = new URLSearchParams(window.location.search);

  // UTM params tienen prioridad
  const utm = params.get('utm_source');
  if (utm) return utm;

  const ref = document.referrer.toLowerCase();
  const ua = navigator.userAgent.toLowerCase();

  const patterns = {
    instagram: [/instagram\.com/, /ig\.me/, /com\.instagram/],
    facebook:  [/facebook\.com/, /fb\.com/, /fban/, /fbav/],
    youtube:   [/youtube\.com/, /youtu\.be/],
    linkedin:  [/linkedin\.com/],
    tiktok:    [/tiktok\.com/],
    twitter:   [/twitter\.com/, /t\.co/, /x\.com/],
  };

  const searchPatterns = [/google\./, /bing\.com/, /yahoo\.com/, /duckduckgo\.com/];

  if (ref) {
    for (const [source, pats] of Object.entries(patterns)) {
      if (pats.some(p => p.test(ref))) return source;
    }
    if (searchPatterns.some(p => p.test(ref))) return 'organic_search';
  }

  // Fallback a user-agent (in-app browsers)
  for (const [source, pats] of Object.entries(patterns)) {
    if (pats.some(p => p.test(ua))) return source;
  }

  return ref ? 'unknown' : 'direct';
}

function getOrCreateSessionId() {
  const KEY = 'petru_session_id';
  let id = sessionStorage.getItem(KEY);
  if (!id) {
    id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    sessionStorage.setItem(KEY, id);
  }
  return id;
}

function getTrafficSourceFromSession() {
  const KEY = 'petru_traffic_source';
  let source = sessionStorage.getItem(KEY);
  if (!source) {
    source = detectTrafficSource();
    sessionStorage.setItem(KEY, source);
  }
  return source;
}

async function trackPageVisit() {
  try {
    const sessionId = getOrCreateSessionId();
    const trafficSource = getTrafficSourceFromSession(); // detectado en cliente
    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        traffic_source: trafficSource,
        referrer_url: document.referrer || null,
        user_agent: navigator.userAgent,
        landing_page: window.location.pathname + window.location.search
      })
    });
    if (!response.ok) console.error('Error registrando visita:', await response.text());
  } catch (e) {
    console.error('Error tracking visita:', e);
  }
}

async function trackCalendlyClick(buttonId, buttonLocation) {
  try {
    const sessionId = getOrCreateSessionId();
    const trafficSource = getTrafficSourceFromSession();
    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        traffic_source: trafficSource,
        button_id: buttonId || 'unknown',
        button_location: buttonLocation || 'unknown',
        page_url: window.location.pathname
      })
    });
    if (!response.ok) console.error('Error registrando click:', await response.text());
  } catch (e) {
    console.error('Error tracking click:', e);
  }
}

function initTracking() {
  trackPageVisit();
}

export {
  getOrCreateSessionId,
  getTrafficSourceFromSession,
  trackPageVisit,
  trackCalendlyClick,
  initTracking
};
