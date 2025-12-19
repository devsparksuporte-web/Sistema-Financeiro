from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    # Registrar blueprints
    from routes import main, auth, api
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(api, url_prefix='/api')
    
    # Custom Jinja2 filters
    @app.template_filter('format_currency')
    def format_currency(value):
        if value is None:
            return "R$ 0,00"
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Erro 404 personalizado
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin padrão se não existir
        from models import Usuario
        from werkzeug.security import generate_password_hash
        
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                nome='Administrador',
                username='admin',
                email='admin@sistema.com',
                senha_hash=generate_password_hash('admin123'),
                perfil='admin',
                departamento='ti',
                status='ativo'
            )
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)