"""
Extensões do Flask
Inicialização das extensões sem a aplicação
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensões sem a aplicação
db = SQLAlchemy()
login_manager = LoginManager()

# Configurar login manager
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
