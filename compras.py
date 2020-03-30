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
        qry = "select di.iddocumentoitem, di.iddetalhe, di.qtitem, di.vlunitario, di.vlsubst/di.qtitem vlsubst, di.vlipi/di.qtitem vlipi, de.dsdetalhe, de.allucrodesejada, de.vlprecovenda vlprecoprazo, dp.vlpreco vlprecovista, di.vlfreterateado, 0 vlrateio \
            from wshop.docitem di \
            join wshop.detalhe de on di.iddetalhe = de.iddetalhe \
            join wshop.detalheprecos dp on dp.iddetalhe = de.iddetalhe \
            where di.iddocumento = '{}' \
            and idtabela = '01000EBK0Y'".format(
            id
        )
        rows = dbpg.query(qry)
        return rows.to_json(orient="records")

    @staticmethod
    def post_preco(obj):
        dbpg = pgdb()
        update_prazo = "update wshop.detalhe set vlprecovenda = {} where iddetalhe = '{}'".format(
            obj["prazo"], obj["id"]
        )
        update_avista = "update wshop.detalheprecos set vlpreco = {} where iddetalhe = '{}'".format(
            obj["avista"], obj["id"]
        )

        dbpg.execute(update_avista)
        dbpg.execute(update_prazo)
        return {"message": "Preços atualizados com sucesso"}
