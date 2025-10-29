from flask import Blueprint, request, jsonify, send_file
import os
import uuid
from app.utils.video_posture_helper import process_video_posture

analisis_postural_bp = Blueprint('analisis_postural', __name__)

UPLOAD_FOLDER = 'uploaded_videos'
OUTPUT_FOLDER = 'output_videos'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@analisis_postural_bp.route('/analizar-postura', methods=['POST'])
def analizar_postura():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo de video'}), 400

        video = request.files['video']

        if video.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400

        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{video.filename}")
        output_path = os.path.join(OUTPUT_FOLDER, f"{uid}_resultado.mp4")

        video.save(input_path)

        resumen = process_video_posture(input_path, output_path)

        if not resumen['success']:
            return jsonify({'error': resumen['error']}), 500

        return jsonify({
            'id': uid,
            'status': 'success',
            'message': 'Análisis de video completado exitosamente',
            'data': {
                'resumen': {
                    'total_frames': resumen['total_frames'],
                    'malas_posturas': resumen['malas_posturas'],
                    'porcentaje_malas_posturas': round(
                        (resumen['malas_posturas'] / resumen['total_frames'] * 100)
                        if resumen['total_frames'] > 0 else 0,
                        2
                    )
                },
                'video_resultado_url': resumen['cloudinary_url'],
                'video_filename': os.path.basename(output_path)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


@analisis_postural_bp.route('/download/<filename>', methods=['GET'])
def download_video(filename):
    try:
        path = os.path.join(OUTPUT_FOLDER, filename)

        if not os.path.exists(path):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        return send_file(path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': f'Error al descargar archivo: {str(e)}'}), 500


@analisis_postural_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'module': 'analisis-postural',
        'status': 'operational',
        'version': '1.0.0'
    }), 200


@analisis_postural_bp.route('/info', methods=['GET'])
def info():
    return jsonify({
        'module': 'Análisis Postural (Video)',
        'description': 'Módulo para análisis de postura en tiempo real usando videos con MediaPipe y OpenCV',
        'endpoints': {
            'POST /analizar-postura': 'Analizar postura desde un video',
            'GET /download/<filename>': 'Descargar video procesado',
            'GET /test': 'Verificar estado del módulo',
            'GET /info': 'Información del módulo'
        },
        'requirements': ['video/mp4', 'video/avi', 'video/mov']
    }), 200
