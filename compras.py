from dbconn import pgdb
import json
import pandas as pd
import glob
import time
import os

def iniciar_arquivo():
    while(Compras.arquivo_lock):
        print('esperando...')
        time.sleep(0.5)

    Compras.arquivo_lock = True

def finalizar_arquivo():
    Compras.arquivo_lock = False

class Compras:
    pedido_compra = pd.DataFrame()
    arquivo_lock = False
    valor_frete =  {}

    ### NOTAS COMPRA ###
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
        return rows.head(100).to_json(orient="records")

    @staticmethod
    def get_nota_itens(id):
        dbpg = pgdb()
        qry = f"""select di.iddocumentoitem
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
                    ,'' idmontagem
            from wshop.docitem di
                join wshop.detalhe de on di.iddetalhe = de.iddetalhe 
                left join wshop.detalheprecos dp on dp.iddetalhe = de.iddetalhe and idtabela = '01000EBK0Y' 
            where di.iddocumento = '{id}' 
        union
            select dm.idmontagem 
                ,dm.iddetalhe
                ,0 qtitem
                ,di.vlunitario * dmi.nrquantidade vlunitario
                ,di.vlsubst/di.qtitem * dmi.nrquantidade  vlsubst
                ,di.vlipi/di.qtitem * dmi.nrquantidade  vlipi
                ,de.dsdetalhe
                ,de.allucrodesejada
                ,de.vlprecovenda vlprecoprazo
                ,dp.vlpreco vlprecovista
                ,di.vlfreterateado
                ,0.0 vlrateio
                ,dm.idmontagem 
            from wshop.detalhe_montagem dm 
                join wshop.detalhe_montagemitem dmi on dm.idmontagem = dmi.idmontagem 
                join wshop.docitem di on di.iddetalhe = dmi.idreferencia 
                join wshop.detalhe de on de.iddetalhe = dm.iddetalhe 
                left join wshop.detalheprecos dp on dp.iddetalhe = de.iddetalhe and idtabela = '01000EBK0Y' 
            where dmi.idreferencia in (select iddetalhe from wshop.docitem d where d.iddocumento = '{id}')
                and di.iddocumento = '{id}'
            order by dsdetalhe"""

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
            """select p.idpessoa, replace(p.nmpessoa,'/','-') nmpessoa, p.nmfantasia from wshop.pessoas p
                where p.sttipopessoa  = 'F' and p.stativo = 'S'
                    and (p.nmpessoa like upper('%{}%') or p.nmfantasia like upper('%{}%'))
                order by p.nmpessoa """.format(nome, nome)
        )
        return rows.to_json(orient="records")

    @staticmethod
    def carregar_fretes():
        Compras.valor_frete = pd.read_csv('csv/valor_frete.csv').set_index('iddocumento')

    ### PEDIDOS ###
    @staticmethod
    def get_pedidos():
        arquivos = glob.glob("pedidos/*.csv")
        arquivos.sort(reverse=True)
        ret = pd.DataFrame()
        for arquivo in arquivos:
            arq = arquivo.split('__')
            data = arq[0][8:18].split('_')
            data.reverse()
            data = '/'.join(data)
            ret = ret.append({'idpessoa': arq[2], 'strdata': data, 'nmpessoa': arq[1], 'arquivo': arquivo}, ignore_index=True)
        return ret.to_json(orient="records")

    @staticmethod
    def post_criar_pedido(obj):
        arquivo = 'pedidos/' + obj['strdata'] + '__' + obj['nmpessoa'] + '__' + obj['idpessoa'] + '.csv'
        arquivo = arquivo.replace(' ', '-').replace('&', '')
        dbpg = pgdb()
        lista = dbpg.query("""select d.cdprincipal, d.iddetalhe 
                                ,round(sum(COALESCE(di.qtitem,0))/90*40-COALESCE(es.qtestoque,0)) demanda
                                ,round(COALESCE(es.qtestoque,0)) qtestoque
                                ,d.dsdetalhe
                                ,to_char(inv.dtemissao, 'DD/MM/YYYY') ultajuste
                                from wshop.detalhe d
                                left join wshop.docitem di on di.iddetalhe = d.iddetalhe and di.dtreferencia > current_date-90 and di.tpoperacao = 'V'
                                left join wshop.detalhe_montagem dm on dm.iddetalhe = d.iddetalhe
                                left join (select ee.iddetalhe, ee.qtestoque from wshop.estoque ee
                                    where (ee.iddetalhe, ee.dtreferencia) in (
                                    select d.iddetalhe, max(dtreferencia) dtreferencia from wshop.estoque e
                                    join wshop.detalhe d on e.iddetalhe = d.iddetalhe
                                    group by d.iddetalhe)) es on es.iddetalhe = d.iddetalhe
                                left join (select di.iddetalhe , max(d.dtemissao) dtemissao from wshop.documen d
                            join wshop.docitem di on di.iddocumento = d.iddocumento 
                            where d.cdfiscal in ('1949', '5949')
                            group by di.iddetalhe ) inv on inv.iddetalhe = d.iddetalhe
                                where 1=1
                                --and d.dsdetalhe like '%PREGO%'
                                and d.cdprincipal not in ('001787')
                                and (not dm.stdesmembracomposicao or dm.iddetalhe is null) 
                                and stdetalheativo != 'f'
                                group by d.iddetalhe, d.dsdetalhe, es.qtestoque, d.cdprincipal, es.iddetalhe, inv.dtemissao
                                having (round(sum(di.qtitem)/90*40-es.qtestoque) > es.qtestoque or es.qtestoque <= 0 or es.iddetalhe is null)
                            order by demanda desc, d.dsdetalhe""")

        # Remover itens de outros pedidos
        ped = pd.DataFrame()
        arquivos = glob.glob("pedidos/*.csv")
        for arq in arquivos:
            ped = pd.concat([ped, pd.read_csv(arq)], ignore_index=True)
            
        if(len(arquivos) > 0):
            itens_remover = ped[ped['qtdcompra'] > 0]['iddetalhe'].unique()
            lista = lista[~lista['iddetalhe'].isin(itens_remover)]

        lista['qtdcompra'] = 0
        lista['vlcompra'] = 0.0
        lista['arquivo'] = arquivo

        lista.to_csv(arquivo, index=False)
        Compras.pedido_compra = lista
        return {"message": "Pedido criado com sucesso", "success": True, "arquivo": arquivo}

    @staticmethod
    def get_pedido_itens(arquivo):
        iniciar_arquivo()
        ret =  pd.read_csv(arquivo)
        finalizar_arquivo()
        return ret.to_json(orient='records')

    @staticmethod
    def post_pedido_remover_item(obj):
        iniciar_arquivo()
        ret =  pd.read_csv(obj['arquivo'])
        ret = ret[ret['iddetalhe'] != obj['iddetalhe']]
        ret.to_csv(obj['arquivo'], index=False)
        finalizar_arquivo()
        return {"message": "Produto removido com sucesso", "success": True, "arquivo": obj['arquivo']}

    @staticmethod
    def get_pedido_item_hist(id):
        dbpg = pgdb()
        qry = """select p.nmpessoa "nomePessoa"
                    ,de.dsdetalhe "nomeProduto"
                    ,di.iddetalhe "id"
                    ,di.vlsubst/di.qtitem + di.vlipi/di.qtitem + di.vlunitario "valorCusto"
                    ,to_char(d.dtemissao, 'DD/MM/YYYY') "emissao"
                from wshop.documen d
                    join wshop.docitem di on di.iddocumento = d.iddocumento 
                    join wshop.pessoas p on p.idpessoa = d.idpessoa 
                    join wshop.detalhe de on de.iddetalhe = di.iddetalhe 
                where 1=1
                    and di.iddetalhe = '{}'
                    and d.tpoperacao = 'C'
                    order by d.dtemissao desc""".format(id)

        rows = dbpg.query(qry)
        return json.dumps(rows.to_dict("records"))

    @staticmethod
    def post_produto_inativar(obj):
        dbpg = pgdb()
        dbpg.execute("update wshop.detalhe set stdetalheativo = 'f' where iddetalhe = '{}'".format(obj['iddetalhe']))
        return {"message": "Prduto inativado com sucesso", "success": True}

    @staticmethod
    def post_pedido_atualizar_item(obj):
        iniciar_arquivo()
        ret = pd.read_csv(obj['arquivo'])
        ret.set_index('iddetalhe', inplace=True)
        ret.at[obj['iddetalhe'], 'qtdcompra'] = obj['qtdcompra']
        ret.at[obj['iddetalhe'], 'vlcompra'] = float(obj['vlcompra'])
        ret.to_csv(obj['arquivo'])
        finalizar_arquivo()
        return {"message": "Produto atualizado com sucesso", "success": True, "arquivo": obj['arquivo']}

    @staticmethod
    def post_pedido_arquivar(obj):
        arquivo = obj['arquivo']
        os.rename(arquivo, arquivo.replace("\\", "\\old\\"))
        return {"message": "Pedido arquivado com sucesso", "success": True, "arquivo": obj['arquivo']}

    ### PRECIFICAÇÃO EM LOTE ###
    @staticmethod
    def get_preco_lote(lista):
        query = """select d.iddetalhe, d.dsdetalhe, dp.vlpreco vlprecovista, d.vlprecovenda vlprecoprazo from wshop.detalhe d 
                    left join wshop.detalheprecos dp on dp.iddetalhe = d.iddetalhe and dp.idtabela = '01000EBK0Y'
                where d.stdetalheativo 
                    {}
                    order by d.dsdetalhe"""

        condicao = "  \nand d.dsdetalhe like upper('%{}%')"
        where = ""

        for sch in  lista.split(' '):
            where += condicao.format(sch)

        dbpg = pgdb()
        rows = dbpg.query(query.format(where))
        return rows.to_json(orient="records")
