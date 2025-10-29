import base64
from openai import OpenAI
import cv2


def generate_ergonomic_report(client, image_url, angles, angle_details, recommendations, is_good_posture):

    try:

        angles_summary = "\n".join([
            f"- {detail['segment']}: {detail['current_angle']}° (óptimo: {detail['optimal_range']}) - {detail['status'].upper()}"
            for detail in angle_details
        ])
        basic_recommendations = "\n".join([
            f"- [{rec['type']}] {rec['area']}: {rec['message']}"
            for rec in recommendations
        ])
        prompt = f"""Eres un experto en ergonomía ocupacional y salud laboral. Analiza esta imagen de una persona en su estación de trabajo junto con los datos ergonómicos calculados.

**ANÁLISIS BIOMECÁNICO CALCULADO:**
{angles_summary}

**ESTADO GENERAL DE POSTURA:** {"✓ CORRECTA" if is_good_posture else "✗ REQUIERE MEJORAS"}

**RECOMENDACIONES BÁSICAS DETECTADAS:**
{basic_recommendations}

**TU TAREA:**
1. **Analizar la imagen** para identificar elementos del lugar de trabajo (silla, escritorio, monitor, iluminación, etc.)
2. **Evaluar la ergonomía del espacio de trabajo** (altura del monitor, posición del teclado, apoyo lumbar, etc.)
3. **Proporcionar recomendaciones específicas** para mejorar:
   - Configuración del mobiliario
   - Posicionamiento de equipos
   - Ajustes posturales inmediatos
   - Mejoras a largo plazo
4. **Identificar riesgos** de lesiones por esfuerzo repetitivo o malas posturas
5. **Sugerir ejercicios o pausas** para prevenir fatiga muscular

**FORMATO DE RESPUESTA (en JSON):**
{{
  "resumen_ejecutivo": "Breve resumen del estado ergonómico general (2-3 líneas)",
  "analisis_espacio_trabajo": {{
    "mobiliario": "Descripción del mobiliario visible y su adecuación",
    "equipamiento": "Análisis de la posición de monitor, teclado, mouse, etc.",
    "iluminacion_entorno": "Observaciones sobre iluminación y entorno"
  }},
  "puntos_criticos": [
    "Lista de los 3-5 problemas más urgentes detectados"
  ],
  "recomendaciones_inmediatas": [
    "Acciones que se pueden tomar de inmediato (5-7 recomendaciones específicas)"
  ],
  "recomendaciones_largo_plazo": [
    "Mejoras que requieren inversión o cambios mayores (3-5 sugerencias)"
  ],
  "riesgos_identificados": [
    "Posibles lesiones o problemas de salud si no se corrige (3-4 riesgos)"
  ],
  "ejercicios_recomendados": [
    "3-5 ejercicios o estiramientos para realizar durante la jornada"
  ],
  "puntuacion_ergonomica": {{
    "total": "X/100",
    "postura": "X/25",
    "mobiliario": "X/25",
    "equipamiento": "X/25",
    "entorno": "X/25"
  }}
}}

Sé específico, práctico y profesional. Usa lenguaje claro y accesible."""

        response = client.chat.completions.create(
            model="gpt-4o",  # Modelo con capacidad de visión
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.7,
            response_format={"type": "json_object"}
        )


        ai_report = response.choices[0].message.content


        import json
        try:
            ai_report_json = json.loads(ai_report)
        except:
            ai_report_json = {"raw_response": ai_report}

        return {
            'success': True,
            'report': ai_report_json,
            'tokens_used': response.usage.total_tokens
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error al generar reporte con IA: {str(e)}'
        }

