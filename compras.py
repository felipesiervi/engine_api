from dbconn import pgdb

class compras:
    @staticmethod
    def get_compras():
        print("get_compras()")
        dbpg = pgdb()
        rows = dbpg.query("select p.nmpessoa, d.vltotal from wshop.documen d " 
                        + "join wshop.pessoas p on d.idpessoa = p.idpessoa "
                        + "where d.cdespecie = 'NFe'")
        return rows.to_json(orient='records')