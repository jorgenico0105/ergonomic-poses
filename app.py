import os
from app import create_app


config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = app.config['PORT']
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
