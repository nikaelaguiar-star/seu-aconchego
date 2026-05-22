from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB = "seu_aconchego.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT,
        contato TEXT,
        entrada TEXT NOT NULL,
        saida TEXT NOT NULL,
        status TEXT DEFAULT 'pendente',
        valor REAL DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT DEFAULT 'usuario',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        if session.get("perfil") != "admin":
            flash("Acesso restrito a administradores.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ── AUTH ──────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("index"))
    erro = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = hash_senha(request.form["senha"])
        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha)).fetchone()
        conn.close()
        if user:
            session["usuario_id"] = user["id"]
            session["usuario_nome"] = user["nome"]
            session["perfil"] = user["perfil"]
            return redirect(url_for("index"))
        erro = "E-mail ou senha incorretos."
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── RESERVAS ──────────────────────────────────────────

@app.route("/")
@login_required
def index():
    conn = get_db()
    reservas = conn.execute("SELECT * FROM reservas ORDER BY entrada DESC").fetchall()
    conn.close()
    return render_template("index.html", reservas=reservas)

@app.route("/nova", methods=["POST"])
@login_required
def nova():
    d = request.form
    conn = get_db()
    conn.execute(
        "INSERT INTO reservas (nome, endereco, contato, entrada, saida, status, valor) VALUES (?,?,?,?,?,?,?)",
        (d["nome"], d["endereco"], d["contato"], d["entrada"], d["saida"], d["status"], d.get("valor", 0))
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    conn = get_db()
    if request.method == "POST":
        d = request.form
        conn.execute(
            "UPDATE reservas SET nome=?, endereco=?, contato=?, entrada=?, saida=?, status=?, valor=? WHERE id=?",
            (d["nome"], d["endereco"], d["contato"], d["entrada"], d["saida"], d["status"], d.get("valor", 0), id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    reserva = conn.execute("SELECT * FROM reservas WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("editar.html", r=reserva)

@app.route("/status/<int:id>", methods=["POST"])
@login_required
def atualizar_status(id):
    conn = get_db()
    conn.execute("UPDATE reservas SET status=? WHERE id=?", (request.form["status"], id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    conn = get_db()
    conn.execute("DELETE FROM reservas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ── USUÁRIOS (admin) ──────────────────────────────────

@app.route("/usuarios")
@admin_required
def usuarios():
    conn = get_db()
    lista = conn.execute("SELECT id, nome, email, perfil, criado_em FROM usuarios ORDER BY criado_em DESC").fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=lista)

@app.route("/usuarios/novo", methods=["POST"])
@admin_required
def novo_usuario():
    nome = request.form["nome"].strip()
    email = request.form["email"].strip().lower()
    senha = hash_senha(request.form["senha"])
    perfil = request.form.get("perfil", "usuario")
    conn = get_db()
    try:
        conn.execute("INSERT INTO usuarios (nome, email, senha, perfil) VALUES (?,?,?,?)", (nome, email, senha, perfil))
        conn.commit()
        flash("Usuário criado com sucesso!", "success")
    except sqlite3.IntegrityError:
        flash("E-mail já cadastrado.", "error")
    conn.close()
    return redirect(url_for("usuarios"))

@app.route("/usuarios/excluir/<int:id>", methods=["POST"])
@admin_required
def excluir_usuario(id):
    if id == session["usuario_id"]:
        flash("Você não pode excluir seu próprio usuário.", "error")
        return redirect(url_for("usuarios"))
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Usuário removido.", "success")
    return redirect(url_for("usuarios"))

@app.route("/usuarios/senha/<int:id>", methods=["POST"])
@admin_required
def trocar_senha(id):
    nova = hash_senha(request.form["nova_senha"])
    conn = get_db()
    conn.execute("UPDATE usuarios SET senha=? WHERE id=?", (nova, id))
    conn.commit()
    conn.close()
    flash("Senha atualizada!", "success")
    return redirect(url_for("usuarios"))

# ── PRIMEIRO ACESSO ───────────────────────────────────

@app.route("/setup", methods=["GET", "POST"])
def setup():
    conn = get_db()
    existe = conn.execute("SELECT id FROM usuarios LIMIT 1").fetchone()
    if existe:
        conn.close()
        return redirect(url_for("login"))
    erro = None
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]
        if len(senha) < 6:
            erro = "A senha deve ter pelo menos 6 caracteres."
        else:
            conn.execute("INSERT INTO usuarios (nome, email, senha, perfil) VALUES (?,?,?,?)",
                         (nome, email, hash_senha(senha), "admin"))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
    conn.close()
    return render_template("setup.html", erro=erro)

if __name__ == "__main__":
    init_db()
    # Redireciona para setup se não houver usuários
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
