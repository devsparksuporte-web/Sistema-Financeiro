# reset_db.py
import os

# Remover o banco de dados antigo
if os.path.exists('financeiro.db'):
    os.remove('financeiro.db')
    print("✅ Banco de dados antigo removido")

# Remover arquivos de cache
cache_files = ['__pycache__', 'instance']
for cache in cache_files:
    if os.path.exists(cache):
        import shutil
        shutil.rmtree(cache)
        print(f"✅ Pasta {cache} removida")

print("\n🔧 Agora execute:")
print("python app.py")