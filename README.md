# PetruWorkout

Plataforma web de captación de clientes para un entrenador personal de calistenia, con sistema de tracking propio y dashboard analítico basado en Six Sigma.

🌐 **Producción:** [petrucalistenia.com](https://petrucalistenia.com)

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Vue.js 3 + Vite SSG |
| Backend | FastAPI + Python |
| Base de datos | PostgreSQL (Railway) |
| Despliegue | Vercel (frontend) · Railway (backend) |
| CI/CD | GitHub Actions |

---

## Funcionalidades principales

**Landing y captación**
- Landing page optimizada para conversión con CTA a Calendly
- Página informativa `/info` con servicios, reseñas (Elfsight) y formulario de contacto
- Suscripción a newsletter con acceso a grupo de WhatsApp y calculadora de calorías (token por email, 30 días de validez)

**Sistema de tracking propio**
- Detección del origen del tráfico (Instagram, YouTube, Facebook, LinkedIn, Organic Search)
- Registro de visitas, clics en Calendly y reservas confirmadas
- Sincronización diaria con la API de Calendly mediante GitHub Actions con matching temporal

**Dashboard administrativo**
- Embudo de conversión (visita → clic → reserva)
- Métricas Six Sigma: DPMO, Nivel Sigma, RTY, IC Wilson al 95%
- Distribución de clics por botón y por fuente de tráfico
- Gráfico de tendencia temporal (Plotly)
- Filtros por período y fuente

**Panel de administración**
- Editor de contenido de la landing (textos e imágenes) con commit automático a GitHub → redespliegue en Vercel en ~1 min
- Envío de newsletter con adjuntos opcionales (Brevo)
- Gestión de usuarios registrados


---

## Workflows automatizados

| Workflow | Frecuencia | Descripción |
|----------|-----------|-------------|
| `sync-calendly.yml` | Diario (00:00 UTC) | Sincroniza reservas de Calendly con la BD |
| `backup-railway.yml` | Mensual (día 1) | Backup incremental de PostgreSQL a GitHub |
| `ci.yml` | Cada push/PR | Ejecuta tests y genera reporte de cobertura |

---

## Autor

Desarrollado por **Ana Seseña Ferrero** como Trabajo Fin de Grado — Universidad Rey Juan Carlos, curso 2025-2026.
