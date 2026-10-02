from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db
from routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Wix ve diğer domainlerden gelen isteklere izin vermek için CORS ayarı
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Veritabanını ve tabloları ilklendir
    init_db(app)

    # Rotaları (routes) uygulamaya kaydet
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
