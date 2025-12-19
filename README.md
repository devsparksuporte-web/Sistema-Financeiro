# Sistema Financeiro Empresarial - Versão Corrigida

## Descrição

Sistema completo de gestão financeira empresarial com todas as correções aplicadas para resolver problemas estruturais e de lógica identificados na versão anterior.

## Correções Implementadas

### 1. Problema Crítico: Falta de Importação de Modelos (RESOLVIDO ✅)
- **Antes:** `app.py` usava `LogAuditoria` e `Backup` sem importá-los
- **Depois:** Todos os modelos são importados explicitamente de `models.py`

### 2. Problema de Importação Circular (RESOLVIDO ✅)
- **Antes:** `app.py` e `models.py` tinham dependência circular
- **Depois:** Criado `extensions.py` para inicializar `db` e `login_manager` sem a aplicação
- **Padrão:** Implementado *Application Factory Pattern*

### 3. Problema de Duplicação de Modelos (RESOLVIDO ✅)
- **Antes:** Modelos definidos em `app.py` e `models.py`
- **Depois:** Todos os modelos centralizados em `models.py`

### 4. Problema de Filtro de Datas (RESOLVIDO ✅)
- **Antes:** Comparação com `None` causava `TypeError`
- **Depois:** Verificação se `data_inicio` e `data_fim` existem antes de aplicar filtro

### 5. Problema de Validação de Dados (RESOLVIDO ✅)
- **Antes:** Validação básica, sem verificação de tipo
- **Depois:** Validação robusta com tratamento de exceções e mensagens claras

### 6. Arquivo routes.py Removido (RESOLVIDO ✅)
- **Antes:** Arquivo duplicado e não utilizado
- **Depois:** Removido para evitar confusão

### 7. Código Limpo (RESOLVIDO ✅)
- Importações duplicadas removidas
- Código organizado e comentado
- Seguindo boas práticas do Flask

## Estrutura do Projeto

```
sistema_corrigido/
├── app.py                 # Aplicação principal com Application Factory
├── extensions.py          # Inicialização de extensões (resolve importação circular)
├── models.py              # Todos os modelos centralizados
├── requirements.txt       # Dependências do projeto
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── gerencial.html
│   ├── precificacao.html
│   ├── analise.html
│   ├── relatorios.html
│   ├── admin.html
│   └── 404.html
├── static/                # Arquivos estáticos
│   └── css/
│       └── style.css
├── instance/              # Banco de dados SQLite (criado automaticamente)
└── data/                  # Dados e backups
```

## Instalação

1. **Instalar dependências:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Executar a aplicação:**
   ```bash
   python3 app.py
   ```

3. **Acessar o sistema:**
   - URL: http://localhost:5000
   - E-mail: admin@sistema.com
   - Senha: admin123

## Funcionalidades

### Dashboard
- Visão geral das finanças
- Estatísticas de receitas e despesas
- Saldo do mês

### Gestão Financeira (Gerencial)
- Cadastro de despesas e receitas
- Filtros por categoria, status e período
- Busca por descrição e fornecedor
- Paginação de resultados

### Precificação
- Cálculo de preço de venda
- Markup e margem de lucro
- Impostos e comissões

### Análise Financeira
- Indicadores de liquidez
- Indicadores de rentabilidade
- Exportação de análises

### Relatórios
- Geração de relatórios em PDF, Excel e CSV
- Histórico de relatórios gerados

### Administração (apenas para admin)
- Gerenciamento de usuários
- Logs de auditoria
- Backup e restauração do sistema

## Modelos de Dados

### Usuario
- Autenticação e autorização
- Perfis: admin, gerente, usuario

### Transacao
- Despesas e receitas
- Categorias e status
- Vencimentos e pagamentos

### LogAuditoria
- Registro de ações dos usuários
- Rastreabilidade completa

### Backup
- Backups do sistema
- Proteção com senha

### Relatorio
- Histórico de relatórios gerados

### CentroCusto
- Gestão de centros de custo

### CalculoPrecificacao
- Histórico de cálculos de precificação

### Configuracao
- Configurações do sistema

## Segurança

- Senhas armazenadas com hash (Werkzeug)
- Autenticação via Flask-Login
- Proteção de rotas com decorators
- Validação de dados de entrada

## Tecnologias Utilizadas

- **Backend:** Flask 2.3.3
- **ORM:** SQLAlchemy 3.0.5
- **Autenticação:** Flask-Login 0.6.2
- **Banco de Dados:** SQLite
- **Frontend:** Bootstrap 5, Chart.js, Font Awesome
- **Segurança:** Werkzeug 2.3.7

## Observações

- O banco de dados é criado automaticamente na primeira execução
- O usuário admin é criado automaticamente se não existir
- Transações de exemplo são criadas automaticamente para demonstração
- Todos os problemas identificados no diagnóstico foram corrigidos

## Suporte

Para dúvidas ou problemas, consulte o arquivo `diagnostico.md` que contém a análise completa dos problemas corrigidos.
