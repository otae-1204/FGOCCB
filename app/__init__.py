from flask import Flask
from app.db import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    
    # 初始化数据库
    init_db()
    # insert_default_servants()
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    return app