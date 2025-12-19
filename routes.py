from flask import render_template, request, redirect, url_for, flash, jsonify
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
import json
from datetime import datetime, timedelta

from app import app, db
from models import Usuario, Transacao, LogAuditoria, Backup

# Decorator para admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != 'admin':
            flash('Acesso negado. Permissões de administrador necessárias.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha):
            if usuario.status == 'ativo':
                login_user(usuario)
                usuario.ultimo_acesso = datetime.utcnow()
                
                # Registrar log
                log = LogAuditoria(
                    acao='login',
                    recurso='auth',
                    ip=request.remote_addr,
                    usuario_id=usuario.id
                )
                db.session.add(log)
                db.session.commit()
                
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Sua conta está inativa. Contate o administrador.', 'warning')
        else:
            flash('E-mail ou senha incorretos.', 'danger')
    
    return render_template('login.html')

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    log = LogAuditoria(
        acao='logout',
        recurso='auth',
        ip=request.remote_addr,
        usuario_id=current_user.id
    )
    db.session.add(log)
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# Outras rotas
@app.route('/gerencial')
@login_required
def gerencial():
    return render_template('gerencial.html')

@app.route('/precificacao')
@login_required
def precificacao():
    return render_template('precificacao.html')

@app.route('/analise')
@login_required
def analise():
    return render_template('analise.html')

@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin.html')

# APIs
@app.route('/api/dashboard/estatisticas')
@login_required
def api_dashboard_estatisticas():
    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    
    despesas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'despesa',
        Transacao.data >= inicio_mes,
        Transacao.usuario_id == current_user.id
    ).scalar() or 0
    
    receitas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'receita',
        Transacao.data >= inicio_mes,
        Transacao.usuario_id == current_user.id
    ).scalar() or 0
    
    return jsonify({
        'success': True,
        'estatisticas': {
            'despesas_mes': float(despesas_mes),
            'receitas_mes': float(receitas_mes),
            'saldo_mes': float(receitas_mes - despesas_mes)
        }
    })