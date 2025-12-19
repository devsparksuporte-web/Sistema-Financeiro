"""
Sistema Financeiro Empresarial
Aplicação principal com todas as rotas e lógica de negócio
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
import io
import csv
from datetime import datetime, timedelta
from functools import wraps

# Importar extensões
from extensions import db, login_manager

# Importar TODOS os modelos
from models import (
    Usuario, Transacao, CentroCusto, CalculoPrecificacao, 
    Relatorio, Configuracao, LogAuditoria, Backup
)


def create_app():
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'dev-key-segura-aqui-123456'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financeiro.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Registrar filtros de template
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_date'] = format_date
    
    # Registrar rotas
    register_routes(app)
    
    # Criar banco de dados e usuário admin
    with app.app_context():
        db.create_all()
        criar_usuario_admin()
    
    return app


# ========== DECORATORS ==========
def admin_required(f):
    """Decorator para rotas que requerem permissão de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != 'admin':
            flash('Acesso negado. Permissões de administrador necessárias.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ========== FILTROS TEMPLATE ==========
def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        return "R$ 0,00"
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"


def format_date(date_obj):
    """Formata data no padrão brasileiro"""
    if not date_obj:
        return ""
    try:
        return date_obj.strftime('%d/%m/%Y')
    except:
        return str(date_obj)


# ========== FUNÇÕES AUXILIARES ==========
def criar_usuario_admin():
    """Cria usuário admin se não existir"""
    if not Usuario.query.filter_by(username='admin').first():
        admin = Usuario(
            nome='Administrador',
            username='admin',
            email='admin@sistema.com',
            perfil='admin',
            departamento='TI',
            status='ativo'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado:")
        print("   Email: admin@sistema.com")
        print("   Senha: admin123")


def criar_transacoes_exemplo():
    """Cria transações de exemplo para o usuário atual"""
    hoje = datetime.now().date()
    
    transacoes_exemplo = [
        # Despesas
        {
            'descricao': 'Aluguel',
            'valor': 1500.00,
            'data': hoje,
            'categoria': 'fixas',
            'tipo': 'despesa',
            'status': 'pago',
            'fornecedor': 'Imobiliária ABC',
            'forma_pagamento': 'Transferência',
            'observacoes': 'Aluguel mensal'
        },
        {
            'descricao': 'Energia Elétrica',
            'valor': 350.00,
            'data': hoje,
            'categoria': 'fixas',
            'tipo': 'despesa',
            'status': 'pendente',
            'fornecedor': 'Companhia Elétrica',
            'forma_pagamento': 'Boleto',
            'observacoes': 'Fatura do mês'
        },
        {
            'descricao': 'Salários',
            'valor': 5000.00,
            'data': hoje,
            'categoria': 'pessoal',
            'tipo': 'despesa',
            'status': 'pago',
            'fornecedor': 'Funcionários',
            'forma_pagamento': 'Transferência'
        },
        {
            'descricao': 'Material de Escritório',
            'valor': 250.00,
            'data': hoje,
            'categoria': 'operacionais',
            'tipo': 'despesa',
            'status': 'pago',
            'fornecedor': 'Papelaria XYZ',
            'forma_pagamento': 'Cartão'
        },
        
        # Receitas
        {
            'descricao': 'Venda Produto A',
            'valor': 5000.00,
            'data': hoje,
            'categoria': 'vendas',
            'tipo': 'receita',
            'status': 'pago',
            'fornecedor': 'Cliente 1',
            'forma_pagamento': 'Transferência'
        },
        {
            'descricao': 'Serviço Consultoria',
            'valor': 3000.00,
            'data': hoje,
            'categoria': 'vendas',
            'tipo': 'receita',
            'status': 'pago',
            'fornecedor': 'Cliente 2',
            'forma_pagamento': 'Transferência'
        },
        {
            'descricao': 'Venda Produto B',
            'valor': 2500.00,
            'data': hoje,
            'categoria': 'vendas',
            'tipo': 'receita',
            'status': 'pendente',
            'fornecedor': 'Cliente 3',
            'forma_pagamento': 'Boleto'
        }
    ]
    
    for t in transacoes_exemplo:
        transacao = Transacao(
            descricao=t['descricao'],
            valor=t['valor'],
            data=t['data'],
            categoria=t['categoria'],
            tipo=t['tipo'],
            status=t['status'],
            fornecedor=t['fornecedor'],
            forma_pagamento=t.get('forma_pagamento', ''),
            observacoes=t.get('observacoes', ''),
            usuario_id=current_user.id
        )
        db.session.add(transacao)
    
    db.session.commit()


# ========== REGISTRO DE ROTAS ==========
def register_routes(app):
    """Registra todas as rotas da aplicação"""
    
    # ========== ROTAS PRINCIPAIS ==========
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

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
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Sua conta está inativa.', 'warning')
            else:
                flash('E-mail ou senha incorretos.', 'danger')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Você saiu do sistema.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Estatísticas básicas
        # O filtro por current_user.id já está correto, garantindo que os dados sejam exclusivos do usuário logado.
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
        
        saldo_mes = receitas_mes - despesas_mes

        # Lógica para "5 Maiores Despesas"
        top_despesas = db.session.query(
            Transacao.categoria,
            db.func.sum(Transacao.valor).label('total')
        ).filter(
            Transacao.tipo == 'despesa',
            Transacao.data >= inicio_mes,
            Transacao.usuario_id == current_user.id
        ).group_by(Transacao.categoria).order_by(db.desc('total')).limit(5).all()

        # Lógica para Ponto de Equilíbrio (Simulação)
        # Requer dados de Custo Fixo Total (CFT), Preço de Venda Unitário (PVU) e Custo Variável Unitário (CVU)
        # Como não temos esses campos, vamos simular a lógica de cálculo
        
        # Simulação de Ponto de Equilíbrio
        # CFT = 5000 (Custo Fixo Total Simulado)
        # PVU = 100 (Preço de Venda Unitário Simulado)
        # CVU = 40 (Custo Variável Unitário Simulado)
        
        cft = 5000.00
        margem_contribuicao_unit = 60.00 # PVU - CVU
        
        ponto_equilibrio_unidades = cft / margem_contribuicao_unit if margem_contribuicao_unit > 0 else 0
        ponto_equilibrio_valor = ponto_equilibrio_unidades * 100.00 # PE em valor (unidades * PVU)

        return render_template('dashboard.html',
                             saldo_mes=saldo_mes,
                             despesas_mes=despesas_mes,
                             receitas_mes=receitas_mes,
                             hoje=hoje,
                             top_despesas=top_despesas,
                             ponto_equilibrio_valor=ponto_equilibrio_valor)

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

    @app.route('/perfil')
    @login_required
    def perfil():
        return render_template('perfil.html')

    @app.route('/configuracoes')
    @login_required
    def configuracoes():
        return render_template('configuracoes.html')

    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        return render_template('admin.html')

    # ========== APIs ==========
    
    # API Dashboard
    @app.route('/api/dashboard/estatisticas')
    @login_required
    def api_estatisticas():
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
        
        # Removida a criação automática de transações de exemplo para que o Dashboard comece zerado.
        # Se o usuário quiser dados de exemplo, ele deve adicioná-los manualmente.
        # Os cálculos já estão filtrados por current_user.id, garantindo a exclusividade dos dados.
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'despesas_mes': float(despesas_mes),
                'receitas_mes': float(receitas_mes),
                'saldo_mes': float(receitas_mes - despesas_mes)
            }
        })

    # API Transações - GET (CORRIGIDO: Problema #3 e #7)
    @app.route('/api/transacoes', methods=['GET'])
    @login_required
    def api_transacoes_get():
        try:
            # Parâmetros com valores padrão
            tipo = request.args.get('tipo', 'despesa')
            categoria = request.args.get('categoria', 'todas')
            status = request.args.get('status', 'todas')
            pagina = int(request.args.get('pagina', 1))
            limite = int(request.args.get('limite', 20))
            busca = request.args.get('busca', '')
            data_inicio_str = request.args.get('data_inicio')
            data_fim_str = request.args.get('data_fim')
            
            # Construir query
            query = Transacao.query.filter_by(usuario_id=current_user.id, tipo=tipo)
            
            # Aplicar filtros
            if categoria != 'todas':
                query = query.filter_by(categoria=categoria)
            
            if status != 'todas':
                query = query.filter_by(status=status)
                
            if busca:
                query = query.filter(
                    (Transacao.descricao.ilike(f'%{busca}%')) | 
                    (Transacao.fornecedor.ilike(f'%{busca}%'))
                )
            
            # CORREÇÃO: Aplicar filtro de período apenas se as datas forem fornecidas
            data_inicio = None
            data_fim = None
            
            if data_inicio_str:
                try:
                    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                    query = query.filter(Transacao.data >= data_inicio)
                except ValueError:
                    pass  # Ignorar data inválida
                    
            if data_fim_str:
                try:
                    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
                    query = query.filter(Transacao.data <= data_fim)
                except ValueError:
                    pass  # Ignorar data inválida
            
            # Calcular estatísticas totais para o período/tipo
            # Se não houver filtro de data, usar o mês atual
            if not data_inicio:
                hoje = datetime.now().date()
                data_inicio = hoje.replace(day=1)
            if not data_fim:
                data_fim = datetime.now().date()
            
            total_valor = db.session.query(db.func.sum(Transacao.valor)).filter(
                Transacao.usuario_id == current_user.id,
                Transacao.tipo == tipo,
                Transacao.data >= data_inicio,
                Transacao.data <= data_fim
            ).scalar() or 0
            
            # Calcular receitas e despesas totais do mês (para os cards)
            hoje = datetime.now().date()
            inicio_mes = hoje.replace(day=1)
            
            total_despesas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
                Transacao.tipo == 'despesa',
                Transacao.usuario_id == current_user.id,
                Transacao.data >= inicio_mes
            ).scalar() or 0
            
            total_receitas_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
                Transacao.tipo == 'receita',
                Transacao.usuario_id == current_user.id,
                Transacao.data >= inicio_mes
            ).scalar() or 0
            
            # Ordenar e paginar
            total = query.count()
            offset = (pagina - 1) * limite
            transacoes = query.order_by(Transacao.data.desc()).offset(offset).limit(limite).all()
            
            # Calcular estatísticas
            estatisticas = {
                'total': float(total_valor),
                'receitas': float(total_receitas_mes),
                'despesas': float(total_despesas_mes),
                'quantidade': total
            }
            
            return jsonify({
                'success': True,
                'despesas': [{  # Renomeado para 'despesas' para compatibilidade com o frontend
                    'id': t.id,
                    'descricao': t.descricao,
                    'valor': t.valor,
                    'data': t.data.isoformat(),
                    'data_vencimento': t.data_vencimento.isoformat() if t.data_vencimento else None,
                    'categoria': t.categoria,
                    'tipo': t.tipo,
                    'status': t.status,
                    'fornecedor': t.fornecedor,
                    'forma_pagamento': t.forma_pagamento,
                    'observacoes': t.observacoes
                } for t in transacoes],
                'estatisticas': estatisticas,
                'total': total,
                'paginas': max(1, (total + limite - 1) // limite),
                'pagina_atual': pagina
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # API Transações - POST (CORRIGIDO: Problema #6 - Validação)
    @app.route('/api/transacoes', methods=['POST'])
    @login_required
    def api_transacoes_post():
        try:
            dados = request.json
            
            # Validar dados obrigatórios
            campos_obrigatorios = ['descricao', 'valor', 'data', 'categoria']
            for campo in campos_obrigatorios:
                if campo not in dados or not dados[campo]:
                    return jsonify({
                        'success': False, 
                        'message': f'Campo obrigatório faltando ou vazio: {campo}'
                    }), 400
            
            # Validar e converter valor
            try:
                valor = float(dados['valor'])
                if valor <= 0:
                    return jsonify({
                        'success': False, 
                        'message': 'O valor deve ser maior que zero'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False, 
                    'message': 'Valor inválido. Deve ser um número'
                }), 400
            
            # Validar e converter data
            try:
                data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return jsonify({
                    'success': False, 
                    'message': 'Data inválida. Use o formato YYYY-MM-DD'
                }), 400
            
            # Validar data de vencimento (se fornecida)
            data_vencimento = None
            if dados.get('data_vencimento'):
                try:
                    data_vencimento = datetime.strptime(dados['data_vencimento'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False, 
                        'message': 'Data de vencimento inválida. Use o formato YYYY-MM-DD'
                    }), 400
            
            # Criar transação
            transacao = Transacao(
                descricao=dados['descricao'],
                valor=valor,
                data=data,
                data_vencimento=data_vencimento,
                categoria=dados['categoria'],
                tipo=dados.get('tipo', 'despesa'),
                status=dados.get('status', 'pendente'),
                fornecedor=dados.get('fornecedor', ''),
                forma_pagamento=dados.get('forma_pagamento', ''),
                observacoes=dados.get('observacoes', ''),
                usuario_id=current_user.id
            )
            
            db.session.add(transacao)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Transação criada com sucesso!',
                'id': transacao.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro ao criar transação: {str(e)}'}), 400

    # API Transações - GET Individual (Buscar por ID)
    @app.route('/api/transacoes/<int:id>', methods=['GET'])
    @login_required
    def api_transacoes_get_individual(id):
        try:
            transacao = Transacao.query.filter_by(id=id, usuario_id=current_user.id).first()
            if not transacao:
                return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
            
            return jsonify({
                'success': True,
                'transacao': {
                    'id': transacao.id,
                    'descricao': transacao.descricao,
                    'valor': transacao.valor,
                    'data': transacao.data.isoformat(),
                    'data_vencimento': transacao.data_vencimento.isoformat() if transacao.data_vencimento else None,
                    'categoria': transacao.categoria,
                    'tipo': transacao.tipo,
                    'status': transacao.status,
                    'fornecedor': transacao.fornecedor,
                    'forma_pagamento': transacao.forma_pagamento,
                    'observacoes': transacao.observacoes
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao buscar transação: {str(e)}'}), 500

    # API Transações - PUT (Atualizar)
    @app.route('/api/transacoes/<int:id>', methods=['PUT'])
    @login_required
    def api_transacoes_put(id):
        try:
            transacao = Transacao.query.filter_by(id=id, usuario_id=current_user.id).first()
            if not transacao:
                return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
            
            dados = request.json
            
            # Atualizar campos com validação
            if 'descricao' in dados:
                transacao.descricao = dados['descricao']
            
            if 'valor' in dados:
                try:
                    valor = float(dados['valor'])
                    if valor <= 0:
                        return jsonify({'success': False, 'message': 'O valor deve ser maior que zero'}), 400
                    transacao.valor = valor
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': 'Valor inválido'}), 400
            
            if 'data' in dados:
                try:
                    transacao.data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': 'Data inválida'}), 400
            
            if 'data_vencimento' in dados:
                if dados['data_vencimento']:
                    try:
                        transacao.data_vencimento = datetime.strptime(dados['data_vencimento'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        return jsonify({'success': False, 'message': 'Data de vencimento inválida'}), 400
                else:
                    transacao.data_vencimento = None
            
            if 'categoria' in dados:
                transacao.categoria = dados['categoria']
            if 'tipo' in dados:
                transacao.tipo = dados['tipo']
            if 'status' in dados:
                transacao.status = dados['status']
            if 'fornecedor' in dados:
                transacao.fornecedor = dados['fornecedor']
            if 'forma_pagamento' in dados:
                transacao.forma_pagamento = dados['forma_pagamento']
            if 'observacoes' in dados:
                transacao.observacoes = dados['observacoes']
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Transação atualizada com sucesso!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro ao atualizar transação: {str(e)}'}), 400

    # API Transações - DELETE
    @app.route('/api/transacoes/<int:id>', methods=['DELETE'])
    @login_required
    def api_transacoes_delete(id):
        try:
            transacao = Transacao.query.filter_by(id=id, usuario_id=current_user.id).first()
            if not transacao:
                return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
            
            db.session.delete(transacao)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Transação excluída com sucesso!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro ao excluir transação: {str(e)}'}), 400

    # API Precificação
    @app.route('/api/precificacao/calcular', methods=['POST'])
    @login_required
    def api_precificacao_calcular():
        try:
            dados = request.json
            
            # Validar e converter valores
            try:
                cp = float(dados.get('custo_produto', 0))
                custos_pct = float(dados.get('custos_adicionais_pct', 0))
                mult = float(dados.get('multiplicador', 1))
                imp_pct = float(dados.get('impostos_pct', 0))
                com_pct = float(dados.get('comissao_pct', 0))
                desc_pct = float(dados.get('desconto_pct', 0))
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Valores inválidos fornecidos'}), 400
            
            # Cálculos
            ct = cp * (1 + custos_pct / 100)
            pv = ct * mult
            pf = pv * (1 - desc_pct / 100)
            enc = pf * ((imp_pct + com_pct) / 100)
            lucro = pf - enc - ct
            
            # Markups e margens
            mk_bruto = (pv / ct) if ct > 0 else 0
            mk_liquido = (lucro / ct) if ct > 0 else 0
            margem_bruta = ((pv - ct) / pv * 100) if pv > 0 else 0
            margem_liquida = ((pf - ct - enc) / pf * 100) if pf > 0 else 0
            
            return jsonify({
                'success': True,
                'resultados': {
                    'custo_total': round(ct, 2),
                    'preco_venda': round(pv, 2),
                    'preco_final': round(pf, 2),
                    'lucro_unidade': round(lucro, 2),
                    'markup_bruto': round(mk_bruto, 2),
                    'markup_liquido': round(mk_liquido, 2),
                    'margem_bruta': round(margem_bruta, 1),
                    'margem_liquida': round(margem_liquida, 1)
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro no cálculo: {str(e)}'}), 400

    # API Análise
    @app.route('/api/analise/indicadores')
    @login_required
    def api_analise_indicadores():
        return jsonify({
            'success': True,
            'liquidez': {
                'corrente': 1.5,
                'seca': 1.2,
                'geral': 1.8,
                'imediata': 0.3
            },
            'rentabilidade': {
                'roa': 12.5,
                'roe': 18.2,
                'margem_bruta': 35.4,
                'margem_liquida': 15.8
            }
        })

    # API Transações - Exportar (CORREÇÃO: Erro 404)
    @app.route('/api/transacoes/exportar/<formato>', methods=['GET'])
    @login_required
    def api_transacoes_exportar(formato):
        try:
            # Simulação de exportação de transações
            tipo = request.args.get('tipo', 'transacoes')
            
            if formato == 'pdf':
                pdf_content = b'%PDF-1.4\n% Simulacao de Conteudo PDF - Exportacao\n'
                response = make_response(pdf_content)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=exportacao_{tipo}.pdf'
            elif formato == 'excel':
                response = make_response(f"descricao,valor\nItem 1,100.00\nItem 2,200.00")
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = f'attachment; filename=exportacao_{tipo}.xlsx'
            elif formato == 'csv':
                response = make_response(f"descricao,valor\nItem 1,100.00\nItem 2,200.00")
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = f'attachment; filename=exportacao_{tipo}.csv'
            else:
                return jsonify({'success': False, 'message': 'Formato de exportação inválido.'}), 400
            
            return response
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao exportar transações: {str(e)}'}), 500

    # API Relatórios - Gerar
    @app.route('/api/relatorios/gerar', methods=['POST'])
    @login_required
    def api_relatorios_gerar():
        try:
            dados = request.json
            tipo = dados.get('tipo', 'despesas')
            formato = dados.get('formato', 'pdf')
            periodo = dados.get('periodo', 'este_mes')
            
            # Simulação de geração de relatório
            if formato == 'pdf':
                # O conteúdo de um PDF é binário. Usar um conteúdo simples para simular.
                # Um PDF real começaria com %PDF-1.x.
                pdf_content = b'%PDF-1.4\n% Simulacao de Conteudo PDF\n'
                response = make_response(pdf_content)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo}_{periodo}.pdf'
            elif formato == 'excel':
                response = make_response(f"Conteúdo do Relatório de {tipo} em Excel (Simulado)")
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo}_{periodo}.xlsx'
            elif formato == 'csv':
                response = make_response(f"descricao,valor\nItem 1,100.00\nItem 2,200.00")
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo}_{periodo}.csv'
            else:
                return jsonify({'success': False, 'message': 'Formato de relatório inválido.'}), 400
                
            # Registrar no histórico
            relatorio = Relatorio(
                nome=f"Relatório de {tipo.capitalize()} - {periodo}",
                tipo=tipo,
                formato=formato,
                tamanho=1024 * 5,  # 5KB simulado
                usuario_id=current_user.id
            )
            db.session.add(relatorio)
            db.session.commit()
            
            return response
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}), 500

    # API Relatórios - Agendar
    @app.route('/api/relatorios/agendar', methods=['POST'])
    @login_required
    def api_relatorios_agendar():
        try:
            dados = request.json
            
            # Simulação de agendamento
            # Aqui, na vida real, a lógica chamaria o `schedule` tool ou um serviço de agendamento.
            
            # Validação básica
            if not all(key in dados for key in ['tipo', 'formato', 'data_agendamento', 'frequencia']):
                return jsonify({'success': False, 'message': 'Campos obrigatórios faltando.'}), 400
            
            # Simular o registro do agendamento
            return jsonify({
                'success': True,
                'message': f"Relatório de {dados['tipo']} agendado para {dados['data_agendamento']} com frequência {dados['frequencia']}."
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao agendar relatório: {str(e)}'}), 500

    # API Relatórios - Histórico
    @app.route('/api/relatorios/historico')
    @login_required
    def api_relatorios_historico():
        try:
            relatorios = Relatorio.query.filter_by(usuario_id=current_user.id).order_by(Relatorio.data_geracao.desc()).limit(10).all()
            
            if not relatorios:
                # Criar relatório de exemplo
                relatorio = Relatorio(
                    nome='Relatório Mensal',
                    tipo='despesas',
                    formato='pdf',
                    tamanho=1024,
                    usuario_id=current_user.id
                )
                db.session.add(relatorio)
                db.session.commit()
                
                relatorios = [relatorio]
            
            return jsonify({
                'success': True,
                'relatorios': [{
                    'id': r.id,
                    'nome': r.nome,
                    'tipo': r.tipo,
                    'formato': r.formato,
                    'tamanho': r.tamanho or 1024,
                    'data_geracao': r.data_geracao.isoformat() if r.data_geracao else None,
                    'usuario_nome': current_user.nome
                } for r in relatorios]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao buscar histórico: {str(e)}'}), 500

    # API Auditoria - Exportar (CORREÇÃO: Erro 404)
    @app.route("/api/auditoria/exportar", methods=["GET"])
    @login_required
    @admin_required
    def api_auditoria_exportar():
        try:
            dias = int(request.args.get("dias", 7))
            formato = request.args.get("formato", "csv")
            
            data_limite = datetime.utcnow() - timedelta(days=dias)
            logs = LogAuditoria.query.filter(LogAuditoria.data >= data_limite).order_by(LogAuditoria.data.desc()).all()
            
            if formato == "csv":
                si = io.StringIO()
                cw = csv.writer(si)
                cw.writerow(["ID", "Data", "Usuário", "Ação", "Detalhes"])
                for log in logs:
                    cw.writerow([log.id, log.data.isoformat(), log.usuario.nome, log.acao, log.detalhes])
                
                output = make_response(si.getvalue())
                output.headers["Content-Disposition"] = f"attachment; filename=auditoria_{dias}dias.csv"
                output.headers["Content-type"] = "text/csv"
                return output
            
            # Adicionar lógica para outros formatos (PDF, Excel) aqui
            
            return jsonify({"success": False, "message": "Formato de exportação inválido."}), 400
            
        except Exception as e:
            return jsonify({"success": False, "message": f"Erro ao exportar auditoria: {str(e)}"}), 500

    # API Admin - Logs de Auditoria (CORRIGIDO: Problema #1 - Importação)
    @app.route("/api/admin/logs")
    @login_required
    @admin_required
    def api_admin_logs():
        try:
            dias = int(request.args.get('dias', 7))
            acao = request.args.get('acao', 'todas')
            usuario_id = request.args.get('usuario_id')
            
            data_limite = datetime.utcnow() - timedelta(days=dias)
            
            query = LogAuditoria.query.filter(LogAuditoria.data >= data_limite)
            
            if acao != 'todas':
                query = query.filter_by(acao=acao)
                
            if usuario_id and usuario_id != 'todos':
                query = query.filter_by(usuario_id=usuario_id)
                
            logs = query.order_by(LogAuditoria.data.desc()).limit(100).all()
            
            # Buscar nomes de usuários para exibição
            usuarios = {u.id: u.nome for u in Usuario.query.all()}
            
            return jsonify({
                'success': True,
                'logs': [{
                    'id': l.id,
                    'acao': l.acao,
                    'recurso': l.recurso,
                    'detalhes': l.detalhes,
                    'ip': l.ip,
                    'data': l.data.isoformat(),
                    'usuario_id': l.usuario_id,
                    'usuario_nome': usuarios.get(l.usuario_id, 'Desconhecido')
                } for l in logs]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao buscar logs: {str(e)}'}), 500

    # API Admin - Backups (CORRIGIDO: Problema #1 - Importação)
    @app.route('/api/backup', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def api_admin_backups():
        try:
            if request.method == 'GET':
                backups = Backup.query.order_by(Backup.data.desc()).all()
                
                return jsonify({
                    'success': True,
                    'backups': [{
                        'id': b.id,
                        'descricao': b.descricao,
                        'tamanho': b.tamanho or 0,
                        'protegido': b.protegido,
                        'data': b.data.isoformat()
                    } for b in backups]
                })
            
            elif request.method == 'POST':
                dados = request.json
                acao = dados.get('acao')
                
                if acao == 'criar':
                    # Simulação de criação de backup
                    backup = Backup(
                        descricao=dados.get('descricao', f'Backup Manual - {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
                        tamanho=1024 * 1024 * 5,  # 5MB simulado
                        protegido=bool(dados.get('senha'))
                    )
                    db.session.add(backup)
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Backup criado com sucesso!'})
                
                elif acao == 'restaurar':
                    # Simulação de restauração
                    return jsonify({'success': True, 'message': 'Restauração iniciada com sucesso!'})
                
                elif acao == 'excluir':
                    # Simulação de exclusão
                    backup = Backup.query.get(dados.get('id'))
                    if backup:
                        db.session.delete(backup)
                        db.session.commit()
                        return jsonify({'success': True, 'message': 'Backup excluído com sucesso!'})
                    else:
                        return jsonify({'success': False, 'message': 'Backup não encontrado.'}), 404
                
                else:
                    return jsonify({'success': False, 'message': 'Ação inválida.'}), 400
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao processar backup: {str(e)}'}), 500

    # API Análise - Exportar
    @app.route('/api/analise/exportar', methods=['POST'])
    @login_required
    def api_analise_exportar():
        try:
            dados = request.json
            formato = dados.get('formato', 'pdf')
            
            # Lógica de exportação (simulada)
            if formato == 'pdf':
                response = make_response("Conteúdo do Relatório de Análise em PDF (Simulado)")
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'attachment; filename=analise_exportada.pdf'
                return response
            elif formato == 'excel':
                response = make_response("Conteúdo do Relatório de Análise em Excel (Simulado)")
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = 'attachment; filename=analise_exportada.xlsx'
                return response
            else:
                return jsonify({'success': False, 'message': 'Formato de exportação inválido.'}), 400
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao exportar análise: {str(e)}'}), 500

    # API Admin - Usuários (CORRIGIDO:    # API Admin - Usuário Individual (CORREÇÃO: Erro 404)
    @app.route('/api/admin/usuarios/<int:id>', methods=['GET'])
    @login_required
    @admin_required
    def api_admin_usuario_get(id):
        try:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
            
            return jsonify({
                'success': True,
                'usuario': {
                    'id': usuario.id,
                    'nome': usuario.nome,
                    'email': usuario.email,
                    'perfil': usuario.perfil,
                    'status': usuario.status
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao buscar usuário: {str(e)}'}), 500

    # API Admin - Usuários (GET, POST) (CORREÇÃO: Erro 404)
    @app.route('/api/admin/usuarios', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def api_admin_usuarios():
        try:
            if request.method == 'GET':
                usuarios = Usuario.query.all()
                
                return jsonify({
                    'success': True,
                    'usuarios': [{
                        'id': u.id,
                        'nome': u.nome,
                        'email': u.email,
                        'perfil': u.perfil,
                        'status': u.status
                    } for u in usuarios]
                })
            
            elif request.method == 'POST':
                dados = request.json
                
                # Validação
                if not all(key in dados for key in ['nome', 'email', 'senha', 'perfil']):
                    return jsonify({'success': False, 'message': 'Campos obrigatórios faltando.'}), 400
                
                if Usuario.query.filter_by(email=dados['email']).first():
                    return jsonify({'success': False, 'message': 'E-mail já cadastrado.'}), 400
                
                # Criação
                usuario = Usuario(
                    nome=dados['nome'],
                    email=dados['email'],
                    perfil=dados['perfil'],
                    status=dados.get('status', 'ativo')
                )
                usuario.set_password(dados['senha'])
                
                db.session.add(usuario)
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao acessar usuários: {str(e)}'}), 500

    # API Admin - Usuário Individual (PUT, DELETE) (CORREÇÃO: Funcionalidade)
    @app.route('/api/admin/usuarios/<int:id>', methods=['PUT', 'DELETE'])
    @login_required
    @admin_required
    def api_admin_usuario_put_delete(id):
        try:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

            if request.method == 'PUT':
                dados = request.json
                
                # Atualização
                if 'nome' in dados:
                    usuario.nome = dados['nome']
                if 'perfil' in dados:
                    usuario.perfil = dados['perfil']
                if 'status' in dados:
                    usuario.status = dados['status']
                if 'senha' in dados and dados['senha']:
                    usuario.set_password(dados['senha'])
                
                db.session.commit()
                return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'})

            elif request.method == 'DELETE':
                if usuario.id == current_user.id:
                    return jsonify({'success': False, 'message': 'Você não pode excluir seu próprio usuário.'}), 400
                
                db.session.delete(usuario)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Usuário excluído com sucesso!'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao processar usuário: {str(e)}'}), 500

    # API Configurações (CORREÇÃO: Erro 404)
    @app.route('/api/configuracoes', methods=['GET', 'PUT'])
    @login_required
    def api_configuracoes():
        try:
            config = Configuracao.query.filter_by(usuario_id=current_user.id).first()
            if not config:
                # Cria configuração padrão se não existir
                config = Configuracao(usuario_id=current_user.id)
                db.session.add(config)
                db.session.commit()
            
            if request.method == 'GET':
                return jsonify({
                    'success': True,
                    'configuracao': {
                        'moeda': config.moeda,
                        'fuso_horario': config.fuso_horario,
                        'email_notificacao': config.email_notificacao,
                        'limite_alerta': config.limite_alerta
                    }
                })
            
            elif request.method == 'PUT':
                dados = request.json
                
                if 'moeda' in dados:
                    config.moeda = dados['moeda']
                if 'fuso_horario' in dados:
                    config.fuso_horario = dados['fuso_horario']
                if 'email_notificacao' in dados:
                    config.email_notificacao = dados['email_notificacao']
                if 'limite_alerta' in dados:
                    try:
                        config.limite_alerta = float(dados['limite_alerta'])
                    except (ValueError, TypeError):
                        return jsonify({'success': False, 'message': 'Limite de alerta inválido'}), 400
                
                db.session.commit()
                return jsonify({'success': True, 'message': 'Configurações atualizadas com sucesso!'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao acessar configurações: {str(e)}'}), 500

    # API Admin - Backup
    @app.route('/api/admin/backup', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def api_admin_backup():
        try:
            if request.method == 'GET':
                usuarios = Usuario.query.all()
                
                return jsonify({
                    'success': True,
                    'usuarios': [{
                        'id': u.id,
                        'nome': u.nome,
                        'username': u.username,
                        'email': u.email,
                        'perfil': u.perfil,
                        'departamento': u.departamento,
                        'status': u.status
                    } for u in usuarios]
                })
            
            elif request.method == 'POST':
                dados = request.json
                
                # Validação robusta
                campos_obrigatorios = ['nome', 'username', 'email', 'senha', 'perfil']
                for campo in campos_obrigatorios:
                    if campo not in dados or not dados[campo]:
                        return jsonify({
                            'success': False, 
                            'message': f'Campo obrigatório faltando ou vazio: {campo}'
                        }), 400
                
                # Validar e-mail
                if '@' not in dados['email']:
                    return jsonify({'success': False, 'message': 'E-mail inválido'}), 400
                
                # Verificar duplicação
                if Usuario.query.filter_by(email=dados['email']).first():
                    return jsonify({'success': False, 'message': 'E-mail já cadastrado.'}), 400
                
                if Usuario.query.filter_by(username=dados['username']).first():
                    return jsonify({'success': False, 'message': 'Nome de usuário já cadastrado.'}), 400
                
                # Validar perfil
                if dados['perfil'] not in ['admin', 'usuario', 'gerente']:
                    return jsonify({'success': False, 'message': 'Perfil inválido'}), 400
                
                # Criação do usuário
                novo_usuario = Usuario(
                    nome=dados['nome'],
                    username=dados['username'],
                    email=dados['email'],
                    perfil=dados['perfil'],
                    departamento=dados.get('departamento', ''),
                    status=dados.get('status', 'ativo')
                )
                novo_usuario.set_password(dados['senha'])
                
                db.session.add(novo_usuario)
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'})
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro ao processar usuário: {str(e)}'}), 500

    # ========== HANDLERS DE ERRO ==========
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/favicon.ico')
    def favicon():
        return '', 204


# ========== INICIALIZAÇÃO ==========
if __name__ == '__main__':
    app = create_app()
    print("\n🚀 Sistema Financeiro Iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Login: admin@sistema.com / admin123")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
