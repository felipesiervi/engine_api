from dbconn import pgdb


class compras:
    @staticmethod
    def get_notas():
        dbpg = pgdb()
        rows = dbpg.query(
            "select d.iddocumento, d.dtemissao, p.nmpessoa, d.vltotal from wshop.documen d "
            + "join wshop.pessoas p on d.idpessoa = p.idpessoa "
            + "where d.cdespecie = 'NFe' order by d.dtreferencia desc"
        )
        return rows.to_json(orient="records")

    @staticmethod
    def get_nota_itens(id):
        dbpg = pgdb()
        print("id {}".format(id))
        rows = dbpg.query(
            "select di.iddocumentoitem, di.iddetalhe, di.qtitem, di.vlunitario, di.vlsubst, di.vlipi, de.dsdetalhe "
            + "from wshop.docitem di "
            + "join wshop.detalhe de on di.iddetalhe = de.iddetalhe "
            + "where di.iddocumento = '{}'".format(id)
        )
        return rows.to_json(orient="records")
