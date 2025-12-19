# test_simple.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Teste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))

with app.app_context():
    db.create_all()
    print("✅ Banco criado com sucesso!")
    
    # Testar inserção
    teste = Teste(nome="Teste 1")
    db.session.add(teste)
    db.session.commit()
    
    # Testar consulta
    resultado = Teste.query.all()
    print(f"📊 Registros: {len(resultado)}")
    
print("\n🎉 Teste concluído com sucesso!")