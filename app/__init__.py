import os
from flask import Flask
from flask_cors import CORS
import cloudinary

def create_app(config_name='development'):

    app = Flask(__name__)


    from app.config import config
    app.config.from_object(config[config_name])


    CORS(app)


    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET']
    )


    from app.modules.analisis_ergonomico.routes import analisis_ergonomico_bp
    from app.modules.analisis_postural.routes import analisis_postural_bp
    app.register_blueprint(analisis_ergonomico_bp, url_prefix='/api/analisis-ergonomico')
    app.register_blueprint(analisis_postural_bp, url_prefix='/api/analisis-postural')

    @app.route('/')
    def index():
        return {
            'message': 'API de Análisis Postural',
            'status': 'running',
            'version': '1.0.0',
            'modules': ['analisis-ergonomico', 'analisis-postural']
        }

    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    return app
