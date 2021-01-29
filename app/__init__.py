from flask import Flask
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from config import config

bootstrap = Bootstrap()
photos = UploadSet('photos', IMAGES)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    configure_uploads(app, photos)
    patch_request_class(app)    

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app