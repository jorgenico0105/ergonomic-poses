from flask import Blueprint, request, jsonify, current_app
import uuid
from openai import OpenAI
from app.utils.cloudinary_helper import upload_image
from app.utils.mediapipe_helper import analyze_posture
from app.utils.openai_helper import generate_ergonomic_report

analisis_ergonomico_bp = Blueprint('analisis_ergonomico', __name__)

@analisis_ergonomico_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró imagen en el request'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400

        analysis_id = str(uuid.uuid4())


        analysis_result = analyze_posture(file)
        if not analysis_result['success']:
            return jsonify({'error': analysis_result['error']}), 500

        upload_result = upload_image(
            analysis_result['processed_image'],
            folder='analisis-ergonomico',
            public_id=f'analysis_{analysis_id}'
        )


        client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

        ai_report_result = generate_ergonomic_report(
            client=client,
            image_url=upload_result['url'],
            angles=analysis_result['angles'],
            angle_details=analysis_result['recommendations']['angle_details'],
            recommendations=analysis_result['recommendations']['recommendations'],
            is_good_posture=analysis_result['is_good_posture']
        )
        response_data = {
            'id': analysis_id,
            'status': 'success',
            'message': 'Análisis completado exitosamente',
            'recommendations' : analysis_result['recommendations'],
            'data': {
                'image_url': upload_result['url'],
                'ai_analysis': None
            }
        }

        if ai_report_result['success']:
            response_data['data']['ai_analysis'] = ai_report_result['report']
        else:
            response_data['data']['ai_analysis'] = {
                'error': ai_report_result.get('error', 'No se pudo generar análisis con IA')
            }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


@analisis_ergonomico_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'module': 'analisis-ergonomico',
        'status': 'operational',
        'version': '1.0.0'
    }), 200


@analisis_ergonomico_bp.route('/info', methods=['GET'])
def info():

    return jsonify({
        'module': 'Análisis Ergonómico',
        'description': 'Módulo para análisis de postura ergonómica usando MediaPipe y OpenCV',
        'endpoints': {
            'POST /analyze': 'Analizar postura desde una imagen',
            'GET /test': 'Verificar estado del módulo',
            'GET /info': 'Información del módulo'
        },
        'requirements': ['image/jpeg', 'image/png', 'image/webp']
    }), 200
