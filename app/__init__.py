from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mysql.init_app(app)

    # Register routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.booking import booking_bp
    app.register_blueprint(booking_bp)
    
    from app.routes.student import student_bp
    app.register_blueprint(student_bp)

    return app