from dbconn import pgdb
import json
import pandas as pd
import glob

class Compras:
    pedido_compra = pd.DataFrame()

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

    @staticmethod
    def get_fornecedores(nome):
        dbpg = pgdb()
        rows = dbpg.query(
            """select p.idpessoa, p.nmpessoa, p.nmfantasia from wshop.pessoas p
                where p.sttipopessoa  = 'F' and p.stativo = 'S'
                    and (p.nmpessoa like upper('%{}%') or p.nmfantasia like upper('%{}%'))
                order by p.nmpessoa """.format(nome, nome)
        )
        return rows.to_json(orient="records")

    @staticmethod
    def get_pedidos():
        arquivos = glob.glob("pedidos/*.h5")
        arquivos.sort(reverse=True)
        ret = pd.DataFrame()
        for arquivo in arquivos:
            arquivo = arquivo.split('__')
            ret = ret.append({'idpessoa': arquivo[2], 'strdata': arquivo[0], 'nmpessoa': arquivo[1]}, ignore_index=True)
        return ret.to_json(orient="records")

    @staticmethod
    def post_criar_pedido(obj):
        arquivo = 'pedidos/' + obj['strdata'] + '__' + obj['nmpessoa'] + '__' + obj['idpessoa'] + '.h5'
        dbpg = pgdb()
        lista = dbpg.query("""select d.cdprincipal, d.iddetalhe 
                                ,round(sum(COALESCE(di.qtitem,0))/90*30-COALESCE(es.qtestoque,0)) demanda
                                ,round(COALESCE(es.qtestoque,0)) qtd_atual
                                ,d.dsdetalhe produto
                                ,to_char(inv.dtemissao, 'DD/MM/YYYY') ult_ajuste
                                from wshop.detalhe d
                                join wshop.produto p on p.idproduto = d.idproduto 
                                left join wshop.docitem di on di.iddetalhe = d.iddetalhe
                                left join wshop.detalhe_montagem dm on dm.iddetalhe = d.iddetalhe
                                left join (select ee.iddetalhe, ee.qtestoque from wshop.estoque ee
                                    where (ee.iddetalhe, ee.dtreferencia) in (
                                    select d.iddetalhe, max(dtreferencia) dtreferencia from wshop.estoque e
                                    join wshop.detalhe d on e.iddetalhe = d.iddetalhe
                                    group by d.iddetalhe)) es on es.iddetalhe = di.iddetalhe
                                left join (select di.iddetalhe , max(d.dtemissao) dtemissao from wshop.documen d
                            join wshop.docitem di on di.iddocumento = d.iddocumento 
                            where d.cdfiscal in ('1949', '5949')
                            group by di.iddetalhe ) inv on inv.iddetalhe = di.iddetalhe
                                where  (di.dtreferencia > current_date-90 and di.tpoperacao = 'V' or di.tpoperacao is null)
                                --and d.dsdetalhe like '%PREGO%'
                                and (not dm.stdesmembracomposicao or dm.iddetalhe is null) 
                                and d.stexp = 'A' 
                                group by d.iddetalhe, d.dsdetalhe, es.qtestoque, d.cdprincipal, es.iddetalhe, inv.dtemissao
                                having (round(sum(di.qtitem)/90*30-es.qtestoque) > es.qtestoque or es.qtestoque <= 0 or es.iddetalhe is null)
                            order by demanda desc""")

        lista['qtd_compra'] = 0
        lista['vl_compra'] = 0
        lista.to_parquet(arquivo)
        Compras.pedido_compra = lista
        return {"message": "Pedido criado com sucesso", "success": True, "arquivo": arquivo}

