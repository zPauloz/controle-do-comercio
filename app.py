from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "troque-esta-chave-antes-de-publicar"
DB = Path(__file__).with_name("comercio.db")

def conectar():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def iniciar_banco():
    with conectar() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL CHECK(preco > 0),
            estoque INTEGER NOT NULL CHECK(estoque >= 0)
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        );
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            total REAL NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        );
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        );
        """)

HTML = """
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Controle do Comércio</title>
<style>
body{font-family:Arial,sans-serif;background:#f3f5f7;color:#202733;margin:0}
header{background:#17365d;color:white;padding:22px}
main{max-width:900px;margin:24px auto;padding:16px}
nav{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
a,button{background:#176b4d;color:white;padding:11px 15px;border:0;border-radius:6px;text-decoration:none;cursor:pointer}
section{background:white;padding:18px;border-radius:10px;margin:15px 0}
input,select{padding:10px;margin:5px 0 12px;max-width:100%;box-sizing:border-box}
label{display:block;font-weight:bold}
table{border-collapse:collapse;width:100%;background:white}
th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}
.msg{padding:12px;background:#fff0c2;border-radius:6px;margin:10px 0}
</style>
</head>
<body>
<header><h1>Controle do Comércio</h1><p>Pedidos, clientes e estoque em um só lugar.</p></header>
<main>
<nav>
<a href="/">Início</a><a href="/produtos">Produtos</a>
<a href="/clientes">Clientes</a><a href="/pedido">Novo pedido</a>
<a href="/pedidos">Histórico</a>
</nav>
{% with mensagens = get_flashed_messages() %}
{% for mensagem in mensagens %}<div class="msg">{{ mensagem }}</div>{% endfor %}
{% endwith %}
{{ conteudo|safe }}
</main>
</body></html>
"""

def pagina(conteudo, **dados):
    return render_template_string(HTML, conteudo=render_template_string(conteudo, **dados))

@app.route("/")
def inicio():
    with conectar() as db:
        produtos = db.execute("SELECT COUNT(*) n FROM produtos").fetchone()["n"]
        clientes = db.execute("SELECT COUNT(*) n FROM clientes").fetchone()["n"]
        pedidos = db.execute("SELECT COUNT(*) n FROM pedidos").fetchone()["n"]
    return pagina("""
    <section><h2>Painel principal</h2>
    <p>Produtos cadastrados: <strong>{{ produtos }}</strong></p>
    <p>Clientes cadastrados: <strong>{{ clientes }}</strong></p>
    <p>Pedidos registrados: <strong>{{ pedidos }}</strong></p>
    <p>Comece cadastrando produtos e clientes para registrar um pedido.</p></section>
    """, produtos=produtos, clientes=clientes, pedidos=pedidos)

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    with conectar() as db:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            try:
                preco = float(request.form.get("preco", ""))
                estoque = int(request.form.get("estoque", ""))
                if not nome or preco <= 0 or estoque < 0:
                    raise ValueError
                db.execute("INSERT INTO produtos(nome,preco,estoque) VALUES(?,?,?)",
                           (nome, preco, estoque))
                flash("Produto cadastrado com sucesso.")
            except (ValueError, TypeError):
                flash("Confira o nome, o preço maior que zero e o estoque não negativo.")
            return redirect(url_for("produtos"))
        lista = db.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    return pagina("""
    <section><h2>Cadastrar produto</h2><form method="post">
    <label>Nome<input name="nome" required maxlength="100"></label>
    <label>Preço (R$)<input name="preco" type="number" min="0.01" step="0.01" required></label>
    <label>Estoque inicial<input name="estoque" type="number" min="0" step="1" required></label>
    <button>Cadastrar produto</button></form></section>
    <section><h2>Produtos cadastrados</h2><table><tr><th>Produto</th><th>Preço</th><th>Estoque</th></tr>
    {% for p in lista %}<tr><td>{{ p.nome }}</td><td>R$ {{ "%.2f"|format(p.preco) }}</td><td>{{ p.estoque }}</td></tr>{% else %}
    <tr><td colspan="3">Nenhum produto cadastrado.</td></tr>{% endfor %}</table></section>
    """, lista=lista)

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    with conectar() as db:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            telefone = request.form.get("telefone", "").strip()
            if nome:
                db.execute("INSERT INTO clientes(nome,telefone) VALUES(?,?)",
                           (nome, telefone))
                flash("Cliente cadastrado com sucesso.")
            else:
                flash("Informe o nome do cliente.")
            return redirect(url_for("clientes"))
        lista = db.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    return pagina("""
    <section><h2>Cadastrar cliente</h2><form method="post">
    <label>Nome<input name="nome" required maxlength="100"></label>
    <label>Telefone (opcional)<input name="telefone" maxlength="30"></label>
    <button>Cadastrar cliente</button></form></section>
    <section><h2>Clientes cadastrados</h2><table><tr><th>Nome</th><th>Telefone</th></tr>
    {% for c in lista %}<tr><td>{{ c.nome }}</td><td>{{ c.telefone or "—" }}</td></tr>{% else %}
    <tr><td colspan="2">Nenhum cliente cadastrado.</td></tr>{% endfor %}</table></section>
    """, lista=lista)

@app.route("/pedido", methods=["GET", "POST"])
def pedido():
    with conectar() as db:
        if request.method == "POST":
            try:
                cliente_id = int(request.form.get("cliente_id", ""))
                produto_id = int(request.form.get("produto_id", ""))
                quantidade = int(request.form.get("quantidade", ""))
                if quantidade <= 0:
                    raise ValueError
                cliente = db.execute("SELECT id FROM clientes WHERE id=?", (cliente_id,)).fetchone()
                produto = db.execute("SELECT * FROM produtos WHERE id=?", (produto_id,)).fetchone()
                if not cliente or not produto:
                    flash("Selecione um cliente e um produto válidos.")
                    return redirect(url_for("pedido"))
                if quantidade > produto["estoque"]:
                    flash("Estoque insuficiente. Reduza a quantidade ou confira o estoque.")
                    return redirect(url_for("pedido"))
                total = round(produto["preco"] * quantidade, 2)
                with db:
                    db.execute("INSERT INTO pedidos(cliente_id,total) VALUES(?,?)", (cliente_id, total))
                    pedido_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.execute("""INSERT INTO itens_pedido
                        (pedido_id,produto_id,quantidade,preco_unitario) VALUES(?,?,?,?)""",
                        (pedido_id, produto_id, quantidade, produto["preco"]))
                    atualizacao = db.execute(
                        "UPDATE produtos SET estoque=estoque-? WHERE id=? AND estoque>=?",
                        (quantidade, produto_id, quantidade))
                    if atualizacao.rowcount != 1:
                        raise ValueError("Estoque insuficiente")
                flash(f"Pedido #{pedido_id} registrado! Total: R$ {total:.2f}. Estoque atualizado.")
                return redirect(url_for("pedidos"))
            except (ValueError, TypeError):
                flash("Dados inválidos. Confira o cliente, o produto e a quantidade.")
                return redirect(url_for("pedido"))
        clientes_lista = db.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
        produtos_lista = db.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    return pagina("""
    <section><h2>Novo pedido</h2>
    {% if not clientes_lista or not produtos_lista %}
    <p>Antes de registrar pedidos, cadastre pelo menos um cliente e um produto.</p>
    {% else %}
    <form method="post">
    <label>Cliente<select name="cliente_id" required>
    {% for c in clientes_lista %}<option value="{{ c.id }}">{{ c.nome }}</option>{% endfor %}
    </select></label>
    <label>Produto<select name="produto_id" required>
    {% for p in produtos_lista %}<option value="{{ p.id }}">{{ p.nome }} — R$ {{ "%.2f"|format(p.preco) }} (estoque: {{ p.estoque }})</option>{% endfor %}
    </select></label>
    <label>Quantidade<input name="quantidade" type="number" min="1" step="1" required></label>
    <button>Registrar pedido</button></form>{% endif %}</section>
    """, clientes_lista=clientes_lista, produtos_lista=produtos_lista)

@app.route("/pedidos")
def pedidos():
    with conectar() as db:
        lista = db.execute("""
            SELECT p.id, p.total, p.criado_em, c.nome cliente
            FROM pedidos p JOIN clientes c ON c.id=p.cliente_id
            ORDER BY p.id DESC
        """).fetchall()
    return pagina("""
    <section><h2>Histórico de pedidos</h2><table>
    <tr><th>Número</th><th>Cliente</th><th>Total</th><th>Data</th></tr>
    {% for p in lista %}<tr><td>#{{ p.id }}</td><td>{{ p.cliente }}</td>
    <td>R$ {{ "%.2f"|format(p.total) }}</td><td>{{ p.criado_em }}</td></tr>{% else %}
    <tr><td colspan="4">Nenhum pedido registrado.</td></tr>{% endfor %}</table></section>
    """, lista=lista)

if __name__ == "__main__":
    iniciar_banco()
    app.run(debug=False)
