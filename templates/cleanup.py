# cleanup.py
import os
import shutil

print("🧹 Limpando ambiente...")

# Remover arquivos do banco de dados
db_files = ['financeiro.db', 'test.db', 'database.db']
for db_file in db_files:
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Removido: {db_file}")

# Remover pastas de cache
cache_folders = ['__pycache__', 'instance', 'migrations']
for folder in cache_folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"✅ Removido: {folder}/")

# Remover arquivos Python antigos (exceto os necessários)
keep_files = ['app.py', 'requirements.txt', 'cleanup.py', 'templates', 'static']
for file in os.listdir('.'):
    if file.endswith('.py') and file not in keep_files:
        os.remove(file)
        print(f"✅ Removido: {file}")

print("\n✅ Limpeza concluída!")
print("\n🎯 Agora execute:")
print("python app.py")