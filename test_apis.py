import requests

BASE_URL = 'http://localhost:5000'

# Testar login
print("🔐 Testando login...")
response = requests.post(f'{BASE_URL}/login', data={
    'email': 'admin@sistema.com',
    'senha': 'admin123'
}, allow_redirects=False)
print(f"Login: {response.status_code}")

# Pegar cookies da sessão
cookies = response.cookies

# Testar APIs
apis = [
    '/api/dashboard/estatisticas',
    '/api/transacoes',
    '/api/analise/indicadores',
    '/api/relatorios/historico',
    '/api/admin/usuarios',
    '/api/configuracoes',
    '/api/notificacoes',
    '/api/auditoria',
    '/api/backup'
]

print("\n📡 Testando APIs...")
for api in apis:
    response = requests.get(f'{BASE_URL}{api}', cookies=cookies)
    print(f"{api}: {response.status_code} - {response.json().get('success', False) if response.ok else 'ERROR'}")