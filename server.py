from flask import Flask
from compras import compras
from flask.wrappers import Response
from flask_cors import CORS, cross_origin
from flask import request
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/compras/get_notas")
def get_notas():
    return Response(compras.get_notas(), mimetype="application/json")


@app.route("/compras/get_nota_itens")
def get_nota_itens():
    id = request.args.get("id")
    return Response(compras.get_nota_itens(id), mimetype="application/json")


@app.route("/compras/post_preco", methods=["POST"])
def post_preco():
    obj = json.loads(request.data)
    return compras.post_preco(obj)


if __name__ == "__main__":
    app.run()
