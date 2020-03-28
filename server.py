from flask import Flask
from compras import compras
from flask.wrappers import Response
from flask_cors import CORS,cross_origin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/compras/get_compras": {"origins": "http://localhost:52172"}})

@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
@app.route('/compras/get_compras')
def get_compras():
    
    return Response(compras.get_compras(), mimetype='application/json')
if __name__ == '__main__':
    app.run()