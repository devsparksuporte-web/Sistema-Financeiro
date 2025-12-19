# wsgi.py
# Arquivo de entrada para servidores WSGI (como Gunicorn)

from app import create_app

# Cria a instância da aplicação
app = create_app()

if __name__ == "__main__":
    # Executa o servidor de desenvolvimento se o arquivo for executado diretamente
    app.run(debug=True)
