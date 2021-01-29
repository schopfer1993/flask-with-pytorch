import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'app/static/uploads')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}