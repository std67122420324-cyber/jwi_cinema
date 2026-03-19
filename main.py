import os
from flask import Flask
from extensions import db, bcrypt, login_manager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jwi_cinema_secret_key_2026_super_secure'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from core.routes import core_bp
    from users.routes import users_bp
    from movies.routes import movies_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(movies_bp, url_prefix='/movies')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':

    app.run(debug=True)