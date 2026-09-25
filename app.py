from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

BANCO = "simulacao.db"


# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

def conectar_banco():
    conexao = sqlite3.connect(BANCO, timeout=10)
    conexao.row_factory = sqlite3.Row
    return conexao


# ==========================================
# CRIAR TABELAS
# ==========================================

def criar_banco():

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        # Tabela para registrar acessos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL
            )
        """)

        # Tabela da simulação
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inscricoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                modalidade TEXT NOT NULL,
                data_hora TEXT NOT NULL
            )
        """)

        conexao.commit()

    finally:
        conexao.close()


# ==========================================
# PÁGINA INICIAL
# ==========================================

@app.route("/")
def inicio():

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        # Registra um acesso à página
        cursor.execute(
            "INSERT INTO acessos (data_hora) VALUES (?)",
            (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),)
        )

        conexao.commit()

        # Conta quantos acessos aconteceram
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM acessos
        """)

        resultado = cursor.fetchone()

        total_acessos = resultado["total"]

    finally:
        conexao.close()

    return render_template(
        "index.html",
        acessos=total_acessos
    )


# ==========================================
# INSCRIÇÃO
# ==========================================

@app.route("/inscricao", methods=["POST"])
def inscricao():

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    modalidade = request.form.get("modalidade", "").strip()

    # Confere se todos os campos foram preenchidos
    if not nome or not email or not modalidade:
        return redirect(url_for("inicio"))

    # Somente modalidades permitidas
    modalidades_permitidas = [
        "Solo",
        "Duo",
        "Squad"
    ]

    if modalidade not in modalidades_permitidas:
        return redirect(url_for("inicio"))

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO inscricoes
            (
                nome,
                email,
                modalidade,
                data_hora
            )
            VALUES (?, ?, ?, ?)
        """, (
            nome,
            email,
            modalidade,
            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        ))

        conexao.commit()

    finally:
        conexao.close()

    # Depois da inscrição:
    # mostra imediatamente que era uma simulação
    return redirect(
        url_for("revelacao")
    )


# ==========================================
# PÁGINA DE REVELAÇÃO
# ==========================================

@app.route("/revelacao")
def revelacao():

    return render_template(
        "revelacao.html"
    )


# ==========================================
# SOBRE O PROJETO
# ==========================================

@app.route("/sobre")
def sobre():

    return render_template(
        "sobre.html"
    )


# ==========================================
# INICIAR O FLASK
# ==========================================

if __name__ == "__main__":

    criar_banco()

    app.run(
        debug=True
    )