from dbconn import pgdb
import json


class Compras:
    @staticmethod
    def get_notas():
        dbpg = pgdb()
        rows = dbpg.query(
            """select d.iddocumento
                ,d.dtemissao
                ,p.nmpessoa
                ,d.vltotal 
            from wshop.documen d
                join wshop.pessoas p on d.idpessoa = p.idpessoa 
            where d.cdespecie = 'NFe' order by d.dtreferencia desc"""
        )
        return rows.to_json(orient="records")

    @staticmethod
    def get_nota_itens(id):
        dbpg = pgdb()
        qry = """select di.iddocumentoitem
                    ,di.iddetalhe
                    ,cast(di.qtitem as integer) qtitem
                    ,di.vlunitario
                    ,di.vlsubst/di.qtitem vlsubst
                    ,di.vlipi/di.qtitem vlipi
                    ,de.dsdetalhe
                    ,de.allucrodesejada
                    ,de.vlprecovenda vlprecoprazo
                    ,dp.vlpreco vlprecovista
                    ,di.vlfreterateado
                    ,0.0 vlrateio
            from wshop.docitem di
                join wshop.detalhe de on di.iddetalhe = de.iddetalhe 
                left join wshop.detalheprecos dp on dp.iddetalhe = de.iddetalhe and idtabela = '01000EBK0Y' 
            where di.iddocumento = '{}' order by de.dsdetalhe""".format(id)

        rows = dbpg.query(qry)
        rows = rows.fillna(0)
        return rows.to_json(orient="records")

    @staticmethod
    def get_nota_item(id):
        dbpg = pgdb()
        qry = """select de.vlprecovenda vlprecoprazo
                ,dp.vlpreco vlprecovista
                ,de.allucrodesejada 
            from wshop.docitem di 
                join wshop.detalhe de on di.iddetalhe = de.iddetalhe 
                left join wshop.detalheprecos dp on dp.iddetalhe = de.iddetalhe and idtabela = '01000EBK0Y' 
            where di.iddocumentoitem = '{}'""".format(id)

        rows = dbpg.query(qry)
        rows = rows.fillna(0)
        return json.dumps(rows.to_dict("records")[0])

    @staticmethod
    def post_preco(obj):
        try:
            obj = json.loads(obj)
            dbpg = pgdb()

            update_praticado = """update wshop.precos set vlpreco = {}, stexp = 'A', vlprecoant = vlpreco, dtaltvlpreco = now(),
                statusalt = 'Ins' WHERE iddetalhe = '{}'""".format(
                obj["prazo"], obj["id"])

            update_prazo = """update wshop.detalhe set vlprecovenda = {},
                 allucrodesejada = {}, vlprecovendaant = vlprecovenda, dtaltvlprecovenda = now()
                      where iddetalhe = '{}'""".format(obj["prazo"], obj["margem"], obj["id"])

            update_avista = """insert into wshop.detalheprecos as d (iddetalhe, cdempresa, idtabela, qtminima, vlpreco, stexp)
	                VALUES ('{}', '001', '01000EBK0Y', 0, {}, 'A') 
                on conflict (iddetalhe, cdempresa, idtabela) do update
	            set vlpreco = {} WHERE d.iddetalhe = '{}'""".format(obj["id"], obj["avista"], obj["avista"], obj["id"])

            dbpg.execute(update_avista)
            dbpg.execute(update_prazo)
            dbpg.execute(update_praticado)
            return {"message": "Preços atualizados com sucesso", "success": True}
        except:
            return {"message": "Erro ao atualizar erro", "success": False}
