from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_segura'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dados de login
USUARIO = 'Marquita'
SENHA = 'M@rquita077'

NOTAS_ARQUIVO = 'notas.json'

# ========== Funções auxiliares ==========

def carregar_notas():
    """Lê as notas do arquivo JSON."""
    if os.path.exists(NOTAS_ARQUIVO):
        with open(NOTAS_ARQUIVO, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_todas_as_notas(notas):
    """Salva a lista completa de notas no arquivo JSON."""
    with open(NOTAS_ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(notas, f, indent=2, ensure_ascii=False)

def salvar_nota(texto):
    """Adiciona uma nova nota à lista e salva."""
    notas = carregar_notas()
    notas.append({
        'texto': texto
    })
    salvar_todas_as_notas(notas)

# ========== Rotas principais ==========

@app.route('/')
def index():
    if not session.get('logado'):
        return redirect(url_for('login'))
    arquivos = os.listdir(UPLOAD_FOLDER)
    notas = carregar_notas()
    return render_template('index.html', arquivos=arquivos, notas=notas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == USUARIO and senha == SENHA:
            session['logado'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========== Upload de arquivos ==========

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logado'):
        return redirect(url_for('login'))
    if 'arquivo' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['arquivo']
    if file.filename == '':
        return "Arquivo sem nome", 400
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def baixar_arquivo(nome_arquivo):
    if not session.get('logado'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], nome_arquivo)

# ========== Notas ==========

@app.route('/nota', methods=['POST'])
def adicionar_nota():
    if not session.get('logado'):
        return redirect(url_for('login'))
    texto = request.form.get('mensagem')
    if texto:
        salvar_nota(texto)
    return redirect(url_for('index'))

@app.route('/nota/excluir/<int:indice>', methods=['POST'])
def excluir_nota(indice):
    if not session.get('logado'):
        return redirect(url_for('login'))

    senha_digitada = request.form.get('senha')
    if senha_digitada != SENHA:
        return redirect(url_for('index', erro_excluir='Senha incorreta!'))

    notas = carregar_notas()
    if 0 <= indice < len(notas):
        del notas[indice]
        salvar_todas_as_notas(notas)
    return redirect(url_for('index'))


# ========== Execução ==========

if __name__ == '__main__':
    app.run(debug=True)
