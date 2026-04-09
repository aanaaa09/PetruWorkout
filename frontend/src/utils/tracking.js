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
  return sessionStorage.getItem('petru_traffic_source') || 'unknown';
}

async function trackPageVisit() {
  try {
    const sessionId = getOrCreateSessionId();
    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        traffic_source: 'unknown',       // el servidor lo detecta
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
    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        traffic_source: 'unknown',       // el servidor hereda de la sesión
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
