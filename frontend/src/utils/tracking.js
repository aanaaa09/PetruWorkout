function detectTrafficSource() {
  const referrer = document.referrer.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();

  if (referrer.includes('linkedin.com') || referrer.includes('lnkd.in') || referrer.includes('android-app://com.linkedin.android')) return 'linkedin';
  if (referrer.includes('instagram.com') || referrer.includes('ig.me')) return 'instagram';
  if (referrer.includes('tiktok.com') || referrer.includes('tiktokv.com')) return 'tiktok';
  if (referrer.includes('youtube.com') || referrer.includes('m.youtube.com') || referrer.includes('youtu.be')) return 'youtube';
  if (referrer.includes('facebook.com') || referrer.includes('fb.com') || referrer.includes('m.facebook.com')) return 'facebook';
  if (referrer.includes('twitter.com') || referrer.includes('t.co') || referrer.includes('x.com')) return 'twitter';
  if (referrer.includes('google.') || referrer.includes('bing.com') || referrer.includes('yahoo.com') || referrer.includes('duckduckgo.com') || referrer.includes('googlequicksearchbox')) return 'organic_search';
  if (referrer.includes('petrucalistenia.com') || referrer.includes(window.location.hostname)) return 'internal';

  if (!referrer) {
    if (userAgent.includes('instagram')) return 'instagram';
    if (userAgent.includes('tiktok')) return 'tiktok';
    if (userAgent.includes('linkedin')) return 'linkedin';
    if (userAgent.includes('fban') || userAgent.includes('fbav')) return 'facebook';
    if (userAgent.includes('twitter')) return 'twitter';
    return 'direct';
  }

  return 'unknown';
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
  return sessionStorage.getItem(KEY) || 'unknown';
}

function saveTrafficSourceToSession(source) {
  const KEY = 'petru_traffic_source';
  if (!sessionStorage.getItem(KEY)) {
    sessionStorage.setItem(KEY, source);
  }
  return sessionStorage.getItem(KEY);
}

async function trackPageVisit() {
  try {
    const sessionId = getOrCreateSessionId();
    const trafficSource = saveTrafficSourceToSession(detectTrafficSource());

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
  detectTrafficSource,
  getOrCreateSessionId,
  getTrafficSourceFromSession,
  trackPageVisit,
  trackCalendlyClick,
  initTracking
};
