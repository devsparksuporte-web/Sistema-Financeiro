"""
Modelos de Dados do Sistema Financeiro
Centralização de todos os modelos em um único arquivo
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Usuario(db.Model, UserMixin):
    """Modelo de Usuário do Sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    perfil = db.Column(db.String(20), default='usuario')
    departamento = db.Column(db.String(50))
    status = db.Column(db.String(20), default='ativo')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    
    def set_password(self, senha):
        """Define a senha do usuário com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)


class Transacao(db.Model):
    """Modelo de Transação Financeira"""
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    data_vencimento = db.Column(db.Date)
    categoria = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'despesa' ou 'receita'
    status = db.Column(db.String(20), default='pendente')
    fornecedor = db.Column(db.String(100))
    forma_pagamento = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CentroCusto(db.Model):
    """Modelo de Centro de Custo"""
    __tablename__ = 'centros_custo'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    orcamento = db.Column(db.Float, default=0.0)
    tipo = db.Column(db.String(50))
    
    transacoes = db.relationship('Transacao', backref='centro_custo', lazy=True)


class CalculoPrecificacao(db.Model):
    """Modelo de Cálculo de Precificação"""
    __tablename__ = 'calculos_precificacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(200), nullable=False)
    custo_produto = db.Column(db.Float, nullable=False)
    custos_adicionais_pct = db.Column(db.Float, default=0.0)
    multiplicador = db.Column(db.Float, nullable=False)
    impostos_pct = db.Column(db.Float, default=0.0)
    comissao_pct = db.Column(db.Float, default=0.0)
    desconto_pct = db.Column(db.Float, default=0.0)
    custo_total = db.Column(db.Float)
    preco_venda = db.Column(db.Float)
    preco_final = db.Column(db.Float)
    lucro_unidade = db.Column(db.Float)
    markup_bruto = db.Column(db.Float)
    markup_liquido = db.Column(db.Float)
    margem_bruta = db.Column(db.Float)
    margem_liquida = db.Column(db.Float)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))


class Relatorio(db.Model):
    """Modelo de Relatório Gerado"""
    __tablename__ = 'relatorios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    formato = db.Column(db.String(20), nullable=False)
    parametros = db.Column(db.Text)
    caminho_arquivo = db.Column(db.String(500))
    tamanho = db.Column(db.Integer)
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))


class Configuracao(db.Model):
    """Modelo de Configuração do Sistema"""
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    
    @staticmethod
    def get(chave, default=None):
        """Obtém uma configuração"""
        config = Configuracao.query.filter_by(chave=chave).first()
        return config.valor if config else default
    
    @staticmethod
    def set(chave, valor):
        """Define uma configuração"""
        config = Configuracao.query.filter_by(chave=chave).first()
        if config:
            config.valor = valor
        else:
            config = Configuracao(chave=chave, valor=valor)
            db.session.add(config)
        db.session.commit()


class LogAuditoria(db.Model):
    """Modelo de Log de Auditoria"""
    __tablename__ = 'logs_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(100))
    detalhes = db.Column(db.Text)
    ip = db.Column(db.String(50))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))


class Backup(db.Model):
    """Modelo de Backup do Sistema"""
    __tablename__ = 'backups'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    caminho_arquivo = db.Column(db.String(500))
    tamanho = db.Column(db.Integer)
    protegido = db.Column(db.Boolean, default=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
