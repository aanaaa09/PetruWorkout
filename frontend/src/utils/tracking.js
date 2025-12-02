// tracking.js - Sistema de tracking unificado para conversión

/**
 * Detecta el origen del tráfico basándose en referrer y user agent
 */
function detectTrafficSource() {
  const referrer = document.referrer.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();

  // 1. Revisar referrer primero (más confiable)
  if (referrer.includes('instagram.com')) {
    return 'instagram';
  }
  if (referrer.includes('tiktok.com')) {
    return 'tiktok';
  }
  if (referrer.includes('youtube.com') || referrer.includes('m.youtube.com')) {
    return 'youtube';
  }
  if (referrer.includes('youtu.be')) {
    return 'youtube';
  }
  if (referrer.includes('linkedin.com')) {
    return 'linkedin';
  }

  // 2. Búsqueda orgánica
  if (referrer.includes('google.com') ||
      referrer.includes('bing.com') ||
      referrer.includes('yahoo.com') ||
      referrer.includes('duckduckgo.com') ||
      referrer.includes('baidu.com')) {
    // Si viene de búsqueda de video en Google
    if (referrer.includes('tbm=vid') || referrer.includes('/videosearch')) {
      return 'youtube'; // Organic video
    }
    return 'organic_search';
  }

  // 3. Fallback a User-Agent para apps móviles (cuando no hay referrer)
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
      return 'facebook'; // Por si acaso
    }
  }

  // 4. Tráfico directo
  if (!referrer || referrer === '' || referrer.includes(window.location.hostname)) {
    return 'direct';
  }

  // 5. Desconocido
  return 'unknown';
}

/**
 * Obtiene o crea un ID de sesión único
 */
function getOrCreateSessionId() {
  const SESSION_KEY = 'petru_session_id';
  let sessionId = sessionStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    // Generar UUID v4
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

  // Solo guardar si no existe (mantener el origen inicial)
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

    const response = await fetch('http://localhost:5000/api/tracking/visit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(visitData)
    });

    if (!response.ok) {
      console.error('Error al registrar visita:', await response.text());
    } else {
      console.log('Visita registrada correctamente desde:', savedSource);
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

    const response = await fetch('https://petruworkout.up.railway.app/api/tracking/click', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(clickData)
    });

    if (!response.ok) {
      console.error('Error al registrar click:', await response.text());
    } else {
      console.log('Click registrado en:', buttonLocation);
    }
  } catch (error) {
    console.error('Error al trackear click:', error);
  }
}

/**
 * Inicializa el sistema de tracking
 */
function initTracking() {
  // Registrar visita al cargar la página
  trackPageVisit();

  // Opcional: Log en consola para debugging
  console.log('Tracking inicializado');
  console.log('Session ID:', getOrCreateSessionId());
  console.log('Traffic Source:', getTrafficSourceFromSession());
}

// Exportar funciones
export {
  detectTrafficSource,
  getOrCreateSessionId,
  getTrafficSourceFromSession,
  trackPageVisit,
  trackCalendlyClick,
  initTracking
};
