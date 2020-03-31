import json


class Preferencias:
    def __init__(self):
        self.data = {}

    def carregar(self):
        with open("data.json", "r") as fp:
            self.data = json.load(fp)

    def gravar(self):
        with open("data.json", "w") as fp:
            json.dump(self.data, fp)

    def atualizar(self, chave, valor):
        self.data[chave] = valor
