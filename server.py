from flask import Flask
from compras import Compras
from flask.wrappers import Response
from flask_cors import CORS, cross_origin
from flask import request
import json
from preferencias import Preferencias
import dbconn

pref = Preferencias()
pref.carregar()
dbconn.host = pref.data["IpBancoDados"]
dbconn.user = pref.data["Usuario"]
dbconn.database = pref.data["NomeBanco"]
dbconn.password = pref.data["Senha"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/compras/get_notas")
def get_notas():
    return Response(Compras.get_notas(), mimetype="application/json")


@app.route("/compras/get_nota_itens")
def get_nota_itens():
    id = request.args.get("id")
    return Response(Compras.get_nota_itens(id), mimetype="application/json")


@app.route("/compras/get_nota_item")
def get_nota_item():
    id = request.args.get("id")
    return Response(Compras.get_nota_item(id), mimetype="application/json")


@app.route("/compras/post_preco", methods=["POST"])
def post_preco():
    obj = json.loads(request.data)
    return Compras.post_preco(obj)


@app.route("/preferencias/atualizar", methods=["POST"])
def atualizar():
    obj = json.loads(request.data)
    for x in obj:
        pref.atualizar(x, obj[x])
    pref.gravar()
    return {"message": "Configurações atualizadas"}

@app.route("/preferencias", methods=["GET"])
def get_preferencias():
    return json.dumps(pref.data)

@app.route("/compras/get_fornecedores")
def get_fornecedores():
    nome = request.args.get("nome")
    nome = '' if nome == None else nome
    return Response(Compras.get_fornecedores(nome), mimetype="application/json")

@app.route("/compras/get_pedidos")
def get_pedidos():
    return Response(Compras.get_pedidos(), mimetype="application/json")

@app.route("/compras/post_criar_pedido", methods=["POST"])
def post_criar_pedido():
    obj = json.loads(request.data)
    return Compras.post_criar_pedido(obj)

@app.route("/compras/get_pedido_itens")
def get_pedido_itens():
    arquivo = request.args.get("arquivo")
    return Response(Compras.get_pedido_itens(arquivo), mimetype="application/json")

@app.route("/compras/post_pedido_remover_item", methods=["POST"])
def post_pedido_remover_item():
    obj = json.loads(request.data)
    return Compras.post_pedido_remover_item(obj)

@app.route("/compras/get_pedido_item_hist")
def get_pedido_item_hist():
    id = request.args.get("id")
    return Response(Compras.get_pedido_item_hist(id), mimetype="application/json")

@app.route("/compras/post_produto_inativar", methods=["POST"])
def post_produto_inativar():
    obj = json.loads(request.data)
    return Compras.post_produto_inativar(obj)

@app.route("/compras/post_pedido_atualizar_item", methods=["POST"])
def post_pedido_atualizar_item():
    obj = json.loads(request.data)
    return Compras.post_pedido_atualizar_item(obj)

@app.route("/compras/get_preco_lote")
def get_preco_lote():
    lista = request.args.get("lista")
    return Response(Compras.get_preco_lote(lista), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
