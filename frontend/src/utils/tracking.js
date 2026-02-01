// tracking.js - Sistema de tracking simplificado

/**
 * Detecta el origen del tráfico basándose en referrer y user agent
 */
function detectTrafficSource() {
  const referrer = document.referrer.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();

  // 1. LinkedIn (incluye app móvil Android)
  if (referrer.includes('linkedin.com') ||
      referrer.includes('lnkd.in') ||
      referrer.includes('android-app://com.linkedin.android')) {
    return 'linkedin';
  }

  // 2. Instagram
  if (referrer.includes('instagram.com') ||
      referrer.includes('ig.me')) {
    return 'instagram';
  }

  // 3. TikTok
  if (referrer.includes('tiktok.com') ||
      referrer.includes('tiktokv.com')) {
    return 'tiktok';
  }

  // 4. YouTube
  if (referrer.includes('youtube.com') ||
      referrer.includes('m.youtube.com') ||
      referrer.includes('youtu.be')) {
    return 'youtube';
  }

  // 5. Facebook
  if (referrer.includes('facebook.com') ||
      referrer.includes('fb.com') ||
      referrer.includes('m.facebook.com')) {
    return 'facebook';
  }

  // 6. Twitter/X
  if (referrer.includes('twitter.com') ||
      referrer.includes('t.co') ||
      referrer.includes('x.com')) {
    return 'twitter';
  }

  // 7. BÚSQUEDA ORGÁNICA (Google, Bing, etc)
  if (referrer.includes('google.com') ||
      referrer.includes('google.es') ||
      referrer.includes('bing.com') ||
      referrer.includes('yahoo.com') ||
      referrer.includes('duckduckgo.com') ||
      referrer.includes('baidu.com') ||
      referrer.includes('android-app://com.google.android.googlequicksearchbox') ||
      referrer.includes('googlequicksearchbox')) {
    return 'organic_search';
  }

  // 8. TRÁFICO INTERNO (de tu propia web)
  if (referrer.includes('petrucalistenia.com') ||
      referrer.includes(window.location.hostname)) {
    return 'internal';
  }

  // 9. Fallback a User-Agent para apps móviles sin referrer
  if (!referrer || referrer === '') {
    if (userAgent.includes('instagram')) {
      return 'instagram';
    }
    if (userAgent.includes('tiktok')) {
      return 'tiktok';
    }
    if (userAgent.includes('linkedin')) {
      return 'linkedin';
    }
    if (userAgent.includes('fban') || userAgent.includes('fbav')) {
      return 'facebook';
    }
    if (userAgent.includes('twitter')) {
      return 'twitter';
    }
  }

  // 10. TRÁFICO DIRECTO (usuario escribió la URL o bookmark)
  if (!referrer || referrer === '') {
    return 'direct';
  }

  // 11. OTRO REFERRER EXTERNO
  if (referrer && !referrer.includes(window.location.hostname)) {
    try {
      const refUrl = new URL(document.referrer);
      const domain = refUrl.hostname.replace('www.', '').split('.')[0];
      return `referral_${domain}`;
    } catch (e) {
      return 'referral';
    }
  }

  // 12. DESCONOCIDO
  return 'unknown';
}

/**
 * Obtiene o crea un ID de sesión único
 */
function getOrCreateSessionId() {
  const SESSION_KEY = 'petru_session_id';
  let sessionId = sessionStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }

  return sessionId;
}

/**
 * Guarda el origen del tráfico en la sesión
 */
function saveTrafficSourceToSession(source) {
  const TRAFFIC_SOURCE_KEY = 'petru_traffic_source';
  const existingSource = sessionStorage.getItem(TRAFFIC_SOURCE_KEY);

  if (!existingSource) {
    sessionStorage.setItem(TRAFFIC_SOURCE_KEY, source);
  }

  return existingSource || source;
}

/**
 * Obtiene el origen del tráfico de la sesión
 */
function getTrafficSourceFromSession() {
  const TRAFFIC_SOURCE_KEY = 'petru_traffic_source';
  return sessionStorage.getItem(TRAFFIC_SOURCE_KEY) || detectTrafficSource();
}

/**
 * Registra una visita a la página
 */
async function trackPageVisit() {
  try {
    const sessionId = getOrCreateSessionId();
    const trafficSource = detectTrafficSource();
    const savedSource = saveTrafficSourceToSession(trafficSource);

    const visitData = {
      session_id: sessionId,
      traffic_source: savedSource,
      referrer_url: document.referrer || null,
      user_agent: navigator.userAgent,
      landing_page: window.location.pathname + window.location.search
    };

    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/visit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(visitData)
    });

    if (!response.ok) {
      console.error('Error al registrar visita:', await response.text());
    } else {
      console.log('Visita registrada - Source:', savedSource);
    }
  } catch (error) {
    console.error('Error al trackear visita:', error);
  }
}

/**
 * Registra un click en botón de Calendly
 */
async function trackCalendlyClick(buttonId, buttonLocation) {
  try {
    const sessionId = getOrCreateSessionId();
    const trafficSource = getTrafficSourceFromSession();

    const clickData = {
      session_id: sessionId,
      traffic_source: trafficSource,
      button_id: buttonId || 'unknown',
      button_location: buttonLocation || 'unknown',
      page_url: window.location.pathname
    };

    const response = await fetch('https://petruworkout-production.up.railway.app/api/tracking/click', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(clickData)
    });

    if (!response.ok) {
      console.error('Error al registrar click:', await response.text());
    } else {
      console.log('Click Calendly registrado');
    }
  } catch (error) {
    console.error('Error al trackear click:', error);
  }
}

/**
 * Inicializa el sistema de tracking
 */
function initTracking() {
  trackPageVisit();

  console.log('Tracking inicializado');
  console.log('Session ID:', getOrCreateSessionId());
  console.log('Traffic Source:', getTrafficSourceFromSession());
  console.log('Referrer:', document.referrer || 'ninguno');
}

export {
  detectTrafficSource,
  getOrCreateSessionId,
  getTrafficSourceFromSession,
  trackPageVisit,
  trackCalendlyClick,
  initTracking
};
