import os

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    DATABASE = os.path.join(os.path.dirname(__file__), 'instance/fgo.db')
    
    # 安全设置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False