# backend/services/email_sequence_service.py
"""
Secuencia de emails para leads del Test de FUERZA REAL.

  Día 0 → Se llama desde el router de fuerza justo tras register_and_calculate
           (los datos del test están en memoria, no hace falta guardarlos)
  Día 1 → GitHub Action diario
  Día 3 → GitHub Action diario
  Día 4 → GitHub Action diario
  Día 5 → GitHub Action diario

lead_service NO se modifica — el flujo de newsletter sigue igual.
"""

import logging
from .email_service import email_service

logger = logging.getLogger(__name__)

WHATSAPP_GROUP   = "https://chat.whatsapp.com/EPtwBr6DqUk0Y9kfUF0YB1"
WHATSAPP_DIRECTO = "https://wa.me/34642662849?text=FUERTE"

NIVEL_ES = {
    "principiante": "Principiante",
    "novato":       "Novato",
    "intermedio":   "Intermedio",
    "avanzado":     "Avanzado",
    "elite":        "Élite",
}


def _wrap(body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:#fff;color:#333;">
  <div style="max-width:600px;margin:0 auto;padding:30px 20px;">
    {body}
    <hr style="border:none;border-top:1px solid #eee;margin:30px 0;">
    <p style="font-size:12px;color:#999;line-height:1.5;margin:0;">
      PetruWorkout · Entrenador Personal de Calistenia<br>
      📧 petruworkout@gmail.com · 🌐 petrucalistenia.com
    </p>
  </div>
</body>
</html>"""


# ── DÍA 0 ────────────────────────────────────────────────────────
# Llamado desde fuerza router con los datos que ya tiene en memoria

def send_day0(
    to_email: str,
    nombre:   str,
    score:    int,
    level:    str,
    scores:   dict,   # {pull, dips, push, squat} en %
    reps:     dict,   # {pull, dips, push, squat} repeticiones
) -> bool:
    nivel = NIVEL_ES.get(level, level.capitalize())

    nombres_ejercicio = {
        "pull":  "dominadas",
        "dips":  "fondos",
        "push":  "flexiones",
        "squat": "sentadillas",
    }
    # Ejemplo práctico personalizado con su ejercicio más fuerte
    mejor = max(reps, key=reps.get)
    mejor_reps = reps[mejor]
    ejemplo_70 = round(mejor_reps * 0.7)
    ej_nombre = nombres_ejercicio[mejor]

    body = _wrap(f"""
    <p style="font-size:16px;line-height:1.6;margin:0 0 15px 0;">Hola {nombre},</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Acabas de usar el <strong>Test de FUERZA REAL</strong> y estos son tus números:
    </p>

    <div style="background:#f8f8f8;border-left:4px solid #06d6a0;border-radius:6px;
                padding:18px 20px;margin:20px 0;">
      <p style="margin:0 0 12px 0;font-size:18px;font-weight:700;color:#222;">
        🏆 Puntuación: <span style="color:#06d6a0;">{score}/100</span> — Nivel {nivel}
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr>
          <td style="padding:5px 12px 5px 0;color:#555;width:110px;">Dominadas</td>
          <td style="padding:5px 8px 5px 0;font-weight:600;">{reps['pull']} reps</td>
          <td style="padding:5px 0;color:#06d6a0;font-weight:700;">{scores['pull']}%</td>
        </tr>
        <tr>
          <td style="padding:5px 12px 5px 0;color:#555;">Fondos</td>
          <td style="padding:5px 8px 5px 0;font-weight:600;">{reps['dips']} reps</td>
          <td style="padding:5px 0;color:#06d6a0;font-weight:700;">{scores['dips']}%</td>
        </tr>
        <tr>
          <td style="padding:5px 12px 5px 0;color:#555;">Flexiones</td>
          <td style="padding:5px 8px 5px 0;font-weight:600;">{reps['push']} reps</td>
          <td style="padding:5px 0;color:#06d6a0;font-weight:700;">{scores['push']}%</td>
        </tr>
        <tr>
          <td style="padding:5px 12px 5px 0;color:#555;">Sentadillas</td>
          <td style="padding:5px 8px 5px 0;font-weight:600;">{reps['squat']} reps</td>
          <td style="padding:5px 0;color:#06d6a0;font-weight:700;">{scores['squat']}%</td>
        </tr>
      </table>
    </div>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      La mayoría de personas que quieren mejorar su fuerza además de un cuerpo funcional
      y atlético, se quedan con los números y no hacen nada con ellos. No seas uno de esos.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 10px 0;">
      <strong>Un consejo rápido que puedes aplicar HOY MISMO con estos datos:</strong>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Elige 1 ejercicio básico (flexiones, dominadas o sentadillas) y haz 1 sola serie
      al 70% de tu máximo.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;">Sin calentar perfecto.</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;">Sin rutina.</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">Sin pensarlo.</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;"><strong>Solo hazlo.</strong></p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;color:#555;font-style:italic;">
      (Con tus {mejor_reps} {ej_nombre}, prueba a hacer {ejemplo_70} con la mejor técnica posible)
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Te vas a quedar con la sensación de que podrías hacer más. Perfecto. Ese es el punto.
      Guárdate ese número para hacerlas en todas tus rutinas porque ahí es donde empieza
      la fuerza de verdad.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;">
      Mañana te cuento cómo perdí parte de mi fuerza que había construido durante años…
      sin darme cuenta.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0;"><strong>Petru</strong></p>
    """)

    return email_service.send_plain_email(
        to_email=to_email,
        to_name=nombre,
        subject=f"Tu resultado del Test de Fuerza Real ({score}/100) + un consejo que nadie te da",
        html_content=body,
    )


# ── DÍA 1 ────────────────────────────────────────────────────────

def send_day1(to_email: str, nombre: str) -> bool:
    body = _wrap(f"""
    <p style="font-size:16px;line-height:1.6;margin:0 0 15px 0;">Hola {nombre},</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Hace unos meses me pasó algo que he visto en muchos de mis clientes.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Gente que antes entrenaba bien, tenía fuerza… pero por trabajo, familia y
      responsabilidades dejó de tener una rutina clara.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;color:#555;font-style:italic;">"Entreno cuando puedo."</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;color:#555;font-style:italic;">"Ya me organizaré."</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">Y así pasan semanas…</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Yo mismo lo viví. Entrenaba en casa, pero sin estructura. Flexiones, fondos, pino…
      lo de siempre. Pero como que algo no cuadraba...
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Las repeticiones que antes hacía fácil, ahora me costaban.
      Y lo peor fue pensar: <strong>"Antes esto ni lo notaba."</strong>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Pasé de hacer 50 fondos a hacer 20 y sufriendo mucho.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Me había dejado… no solo perdí fuerza. También me noté con menos energía en el día
      a día. Menos ganas. Menos "chispa".
    </p>

    <div style="background:#f8f8f8;border-left:4px solid #e63946;border-radius:6px;
                padding:16px 20px;margin:20px 0;">
      <p style="margin:0;font-size:15px;line-height:1.7;">
        Si no tienes una estructura mínima, aunque entrenes "a veces", tu progreso desaparece.
        No te sientes realizado ni a gusto contigo mismo.
      </p>
    </div>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Si te suena algo de esto, no estás solo. Le pasa al 90% de hombres entre 25–50 años
      que antes estaban en forma… y ahora sienten que han bajado de nivel sin saber cuándo pasó.
      Pero tiene solución.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      En el próximo email te voy a poner delante un número que probablemente no has calculado
      nunca. Y cuando lo veas, vas a entender por qué sigues dónde estás.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      P.D.: Estoy compartiendo algo extra cada día en un grupo de WhatsApp para los que
      quieren ir más rápido. Si quieres entrar,
      <a href="{WHATSAPP_GROUP}" style="color:#06d6a0;font-weight:600;text-decoration:none;">haz clic aquí</a>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0;"><strong>Petru</strong></p>
    """)

    return email_service.send_plain_email(
        to_email=to_email,
        to_name=nombre,
        subject="El error donde casi pierdo toda mi fuerza en un par de meses",
        html_content=body,
    )


# ── DÍA 3 ────────────────────────────────────────────────────────

def send_day3(to_email: str, nombre: str) -> bool:
    body = _wrap(f"""
    <p style="font-size:16px;line-height:1.6;margin:0 0 15px 0;">Hola {nombre},</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Hace 3 días usaste el <strong>Test de FUERZA REAL</strong> y obtuviste tus números.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      La pregunta es: ¿qué has hecho con ellos?
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Porque si la respuesta es "nada", quiero que sepas una cosa.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 10px 0;">
      Cada semana que pasa sin una estructura clara de entrenamiento, esto es lo que ocurre:
    </p>

    <div style="background:#f8f8f8;border-radius:6px;padding:16px 20px;margin:15px 0;">
      <p style="margin:0 0 8px 0;font-size:15px;line-height:1.7;">
        — Pierdes fuerza real (menos repeticiones, menos control, menos nivel)
      </p>
      <p style="margin:0 0 8px 0;font-size:15px;line-height:1.7;">
        — Te sientes más flojo, con menos energía y frustrado contigo mismo
      </p>
      <p style="margin:0;font-size:15px;line-height:1.7;">
        — Y empiezas a normalizar no priorizarte (trabajo, familia, todo antes que tú)
      </p>
    </div>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      No es para asustarte. Es para que dejes de pensar que "no decidir" es gratis.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;">
      <strong>No decidir también tiene un coste. Y normalmente es más alto que decidir.</strong>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;">
      Mañana te voy a presentar a alguien que estaba exactamente donde tú estás ahora.
      Y lo que hizo.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0;"><strong>Petru</strong></p>
    """)

    return email_service.send_plain_email(
        to_email=to_email,
        to_name=nombre,
        subject="Lo que te cuesta NO decidir",
        html_content=body,
    )


# ── DÍA 4 ────────────────────────────────────────────────────────

def send_day4(to_email: str, nombre: str) -> bool:
    body = _wrap(f"""
    <p style="font-size:16px;line-height:1.6;margin:0 0 15px 0;">Hola {nombre},</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">Te quiero presentar a Carlos.</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Hace 3 meses, Carlos estaba como muchos: trabajando todo el día sentado, con dolor
      de cuello, molestias en las articulaciones y sintiéndose cada vez peor físicamente.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Intentaba entrenar en casa sin una rutina… pero seguía igual. Sin progreso. Sin cambios.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;color:#555;font-style:italic;">
      "Sé que podría estar mejor, pero no sé cómo hacerlo… cada vez me noto más flojo
      y con más molestias."
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      No tenía tiempo. Trabajo, responsabilidades… y él siempre el último.
      Pero sabía que tenía que hacer algo sí o sí.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Lo que cambió para Carlos no fue entrenar más horas ni matarse a rutinas complicadas.
      <strong>Fue tener una estructura clara y saber exactamente qué hacer cada día sin pensar.</strong>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 10px 0;"><strong>Resultado:</strong></p>

    <div style="background:#f8f8f8;border-left:4px solid #06d6a0;border-radius:6px;
                padding:16px 20px;margin:15px 0;">
      <p style="margin:0 0 8px 0;font-size:15px;line-height:1.7;">
        — Recuperó su cuerpo funcional (más movilidad, más fuerza, más energía)
      </p>
      <p style="margin:0 0 8px 0;font-size:15px;line-height:1.7;">
        — Sin dolor de cuello, ya no le chasquea el codo al hacer ejercicio
      </p>
      <p style="margin:0;font-size:15px;line-height:1.7;">
        — Pasó de hacer 4 flexiones a 12 de seguido y consiguió sus primeras dominadas
      </p>
    </div>

    <p style="font-size:15px;line-height:1.7;margin:20px 0 25px 0;">
      La diferencia entre donde estaba Carlos y donde está ahora no fue talento, ni suerte,
      ni motivación. <strong>Fue tener un sistema simple, claro y ejecutable.</strong>
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;">
      Mañana te voy a contar cómo puedes hacer lo mismo. Sin rodeos.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0;"><strong>Petru</strong></p>
    """)

    return email_service.send_plain_email(
        to_email=to_email,
        to_name=nombre,
        subject="Carlos pasó de 4 flexiones a volver a dominar su cuerpo",
        html_content=body,
    )


# ── DÍA 5 ────────────────────────────────────────────────────────

def send_day5(to_email: str, nombre: str) -> bool:
    body = _wrap(f"""
    <p style="font-size:16px;line-height:1.6;margin:0 0 15px 0;">Hola {nombre},</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Llevo 4 días hablándote de cómo recuperar tu fuerza y dejar de sentirte flojo.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;">✅ Te he dado tus números con el Test de FUERZA REAL</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;">✅ Te he contado lo que me pasó a mí</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 4px 0;">✅ Te he puesto delante lo que te cuesta no actuar</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 20px 0;">✅ Te he presentado a Carlos que lo consiguió</p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 20px 0;"><strong>Ahora te toca a ti.</strong></p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      Si quieres volver a sentirte fuerte, con energía y recuperar tu nivel físico en menos
      de 3 meses, sin gimnasio y sin material, tengo un programa donde te llevo paso a paso.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 15px 0;">
      El sistema se llama <strong>"FUERZA REAL"</strong>
    </p>

    <div style="background:#f8f8f8;border-radius:6px;padding:16px 20px;margin:20px 0;">
      <p style="margin:0 0 8px 0;font-size:15px;line-height:1.7;font-weight:600;">Incluye:</p>
      <p style="margin:0 0 6px 0;font-size:15px;line-height:1.7;">— Rutinas exactas con tu propio peso (abres y haces, sin pensar)</p>
      <p style="margin:0 0 6px 0;font-size:15px;line-height:1.7;">— Plan semanal cerrado (sabes qué hacer cada día sin improvisar)</p>
      <p style="margin:0 0 6px 0;font-size:15px;line-height:1.7;">— Progresión clara para recuperar fuerza real paso a paso</p>
      <p style="margin:0;font-size:15px;line-height:1.7;">— Seguimiento para que no abandones a mitad como siempre</p>
    </div>

    <p style="font-size:15px;line-height:1.7;margin:0 0 20px 0;"><strong>Inversión: 100€/mes</strong></p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 20px 0;">
      No es para todo el mundo. Es para quien tiene los datos, ha visto que es posible
      y está dispuesto a pasar a la acción.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;">
      Si eso eres tú: escríbeme <strong>"FUERTE"</strong> al WhatsApp
      <a href="{WHATSAPP_DIRECTO}" style="color:#06d6a0;font-weight:600;text-decoration:none;">
        haciendo clic aquí
      </a>
      y te explico cómo empezar.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0 0 25px 0;color:#555;">
      Si no es para ti ahora, no pasa nada. Pero no te cuentes la historia de que no es
      el momento. El momento es cuando decides que lo es.
    </p>

    <p style="font-size:15px;line-height:1.7;margin:0;"><strong>Petru</strong></p>
    """)

    return email_service.send_plain_email(
        to_email=to_email,
        to_name=nombre,
        subject="Esto es para ti (o no)",
        html_content=body,
    )


# ── Mapa día → función (para el script del GH Action) ────────────

SEQUENCE = {
    1: send_day1,
    3: send_day3,
    4: send_day4,
    5: send_day5,
}