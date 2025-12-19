# add_sample_data.py
from app import app, db
from models import Transacao, Usuario
from datetime import datetime, timedelta

with app.app_context():
    # Pegar usuário admin
    admin = Usuario.query.filter_by(username='admin').first()
    
    if admin:
        # Adicionar transações de exemplo
        categorias = ['fixas', 'pessoal', 'operacionais', 'vendas', 'investimentos']
        fornecedores = ['Empresa A', 'Empresa B', 'Empresa C', 'Fornecedor X', 'Fornecedor Y']
        
        # Transações do mês atual
        hoje = datetime.now().date()
        for i in range(20):
            data = hoje - timedelta(days=i)
            
            # Despesa
            despesa = Transacao(
                descricao=f'Despesa {i+1}',
                valor=100.00 * (i+1),
                data=data,
                data_vencimento=data + timedelta(days=30),
                categoria=categorias[i % len(categorias)],
                tipo='despesa',
                status='pago' if i % 2 == 0 else 'pendente',
                fornecedor=fornecedores[i % len(fornecedores)],
                forma_pagamento='Transferência' if i % 2 == 0 else 'Boleto',
                observacoes=f'Observação {i+1}',
                usuario_id=admin.id
            )
            db.session.add(despesa)
            
            # Receita
            receita = Transacao(
                descricao=f'Receita {i+1}',
                valor=200.00 * (i+1),
                data=data,
                categoria='vendas',
                tipo='receita',
                status='pago',
                fornecedor=f'Cliente {i+1}',
                usuario_id=admin.id
            )
            db.session.add(receita)
        
        db.session.commit()
        print(f"✅ Adicionadas {40} transações de exemplo para o usuário admin")