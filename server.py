from flask import Flask
from compras import compras
from flask.wrappers import Response
from flask_cors import CORS, cross_origin
from flask import request

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@cross_origin(origin="localhost", headers=["Content- Type", "Authorization"])
@app.route("/compras/get_notas")
def get_notas():
    return Response(compras.get_notas(), mimetype="application/json")


@cross_origin(origin="localhost", headers=["Content- Type", "Authorization"])
@app.route("/compras/get_nota_itens")
def get_nota_itens():
    id = request.args.get("id")
    return Response(compras.get_nota_itens(id), mimetype="application/json")


if __name__ == "__main__":
    app.run()
