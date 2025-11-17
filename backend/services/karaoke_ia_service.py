"""
Servicio de IA para evaluar karaoke usando OpenAI Whisper + GPT
"""
import base64
import tempfile
import os
import logging
from openai import OpenAI
from ..config.settings import settings

logger = logging.getLogger(__name__)


class KaraokeIAService:
    """Servicio para evaluar karaoke con IA"""

    @staticmethod
    def evaluar_karaoke(audio_base64: str, titulo_cancion: str, artista: str, letra_oficial: str = None) -> dict:
        """
        Evalúa el karaoke usando:
        1. Whisper para transcribir el audio
        2. GPT-4 para evaluar precisión de letra y ritmo

        Args:
            audio_base64: Audio en base64 (sin prefijo data:audio/...)
            titulo_cancion: Título de la canción
            artista: Artista de la canción
            letra_oficial: Letra oficial (opcional, si no se proporciona GPT la busca)

        Returns:
            dict: {
                'puntos': int (0-20),
                'desglose': {
                    'letra': int (0-10),
                    'ritmo': int (0-10)
                },
                'transcripcion': str,
                'feedback': str
            }
        """
        try:
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY no configurada")
                return {
                    'puntos': 10,  # Puntos por defecto
                    'error': 'API de OpenAI no configurada',
                    'feedback': 'No se pudo evaluar el karaoke automáticamente. Se otorgan 10 puntos por defecto.'
                }

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # 1. Guardar audio temporalmente
            audio_path = KaraokeIAService._guardar_audio_temporal(audio_base64)

            if not audio_path:
                return {
                    'puntos': 10,
                    'error': 'Error al procesar audio',
                    'feedback': 'No se pudo procesar el audio. Se otorgan 10 puntos por defecto.'
                }

            # 2. Transcribir con Whisper
            logger.info(f"Transcribiendo audio para: {titulo_cancion} - {artista}")

            with open(audio_path, 'rb') as audio_file:
                transcripcion_result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"  # Español
                )

            transcripcion = transcripcion_result.text
            logger.info(f"Transcripción: {transcripcion[:100]}...")

            # 3. Evaluar con GPT-4
            prompt = f"""Eres un juez de karaoke experto. Evalúa esta interpretación:

**Canción:** {titulo_cancion}
**Artista:** {artista}
**Transcripción del usuario:** {transcripcion}

{"**Letra oficial:** " + letra_oficial if letra_oficial else ""}

Evalúa en una escala de 0-20 puntos:
- **Letra (0-10):** Precisión de las palabras cantadas vs letra oficial
- **Ritmo (0-10):** Fluidez, timing, coherencia al cantar

Responde ÚNICAMENTE en este formato JSON:
{{
    "puntos_letra": <número 0-10>,
    "puntos_ritmo": <número 0-10>,
    "feedback": "<breve comentario positivo y constructivo>"
}}
"""

            logger.info("Enviando evaluación a GPT-4...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Más económico y rápido
                messages=[
                    {"role": "system", "content": "Eres un juez de karaoke justo y motivador."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            resultado_texto = response.choices[0].message.content.strip()
            logger.info(f"Respuesta GPT: {resultado_texto}")

            # Parsear respuesta JSON
            import json
            resultado = json.loads(resultado_texto)

            puntos_letra = max(0, min(10, resultado.get('puntos_letra', 5)))
            puntos_ritmo = max(0, min(10, resultado.get('puntos_ritmo', 5)))
            puntos_totales = puntos_letra + puntos_ritmo

            # Limpiar archivo temporal
            os.unlink(audio_path)

            return {
                'puntos': puntos_totales,
                'desglose': {
                    'letra': puntos_letra,
                    'ritmo': puntos_ritmo
                },
                'transcripcion': transcripcion,
                'feedback': resultado.get('feedback', '¡Buen intento!')
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta GPT: {e}")
            return {
                'puntos': 10,
                'error': 'Error al procesar evaluación',
                'feedback': 'No se pudo evaluar correctamente. Se otorgan 10 puntos por defecto.'
            }

        except Exception as e:
            logger.error(f"Error evaluando karaoke: {e}")
            return {
                'puntos': 10,
                'error': str(e),
                'feedback': 'Hubo un error al evaluar. Se otorgan 10 puntos por defecto.'
            }

    @staticmethod
    def _guardar_audio_temporal(audio_base64: str) -> str:
        """
        Guarda el audio en un archivo temporal

        Args:
            audio_base64: Audio en base64 (puede incluir prefijo data:audio/...)

        Returns:
            str: Path del archivo temporal o None si falla
        """
        try:
            # Remover prefijo data:audio/... si existe
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',', 1)[1]

            # Decodificar base64
            audio_bytes = base64.b64decode(audio_base64)

            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
            temp_file.write(audio_bytes)
            temp_file.close()

            logger.info(f"Audio guardado temporalmente en: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Error guardando audio temporal: {e}")
            return None