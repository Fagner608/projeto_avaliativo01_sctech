import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src.data.gerador_dataset.gerar_dataset_vendas import gerar_dataset_vendas


def carregar_dataset(caminho_csv):
    """Lê o CSV e retorna uma lista de dicionários, um por registro."""
    with open(caminho_csv, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        registros = list(leitor)
    return registros


def inspecionar_dados(registros):
    """Exibe a estrutura, os valores ausentes e uma amostra do dataset."""
    total = len(registros)
    colunas = list(registros[0].keys()) if registros else []
    nulos = {coluna: 0 for coluna in colunas}

    for linha in registros:
        for coluna in colunas:
            if linha.get(coluna, "").strip() == "":
                nulos[coluna] += 1

    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Total de registros: {total}")
    print(f"Total de colunas: {len(colunas)}")
    print(f"Colunas: {colunas}")
    print(f"Valores ausentes por coluna: {nulos}")
    print("Primeiros registros:")
    for linha in registros[:5]:
        print(linha)

    return registros


def limpar_dados(registros):
    """Limpa os registros e retorna os dados válidos e o relatório da operação."""
    relatorio = {
        "iniciais": len(registros),
        "removidos_data": 0,
        "removidos_nulos": 0,
        "clientes_fora_do_padrao": 0,
        "finais": 0,
    }
    padrao_cliente = re.compile(r"^Cliente_\d{3}$", flags=re.IGNORECASE)
    extrair_numero_cliente = re.compile(r"\d{3}")
    limpos = []

    for registro in registros:
        linha = dict(registro)

        for chave in ("id_venda", "data_venda", "cliente", "produto", "categoria", "regiao", "quantidade", "preco_unitario"):
            linha[chave] = linha.get(chave, "").strip()

        try:
            linha["data_venda"] = datetime.strptime(linha["data_venda"], "%Y-%m-%d")
        except ValueError:
            relatorio["removidos_data"] += 1
            continue

        if linha["quantidade"] == "" or linha["preco_unitario"] == "":
            relatorio["removidos_nulos"] += 1
            continue

        linha["id_venda"] = int(linha["id_venda"])
        linha["quantidade"] = int(float(linha["quantidade"]))
        linha["preco_unitario"] = float(linha["preco_unitario"])

        nome_original = linha["cliente"]
        numero_cliente = extrair_numero_cliente.search(nome_original)
        if numero_cliente:
            linha["cliente"] = f"Cliente_{numero_cliente.group()}"

        if padrao_cliente.fullmatch(nome_original) is None:
            relatorio["clientes_fora_do_padrao"] += 1

        limpos.append(linha)

    relatorio["finais"] = len(limpos)
    print("\n=== RELATÓRIO DE LIMPEZA ===")
    print(relatorio)
    return limpos, relatorio


def criar_colunas_derivadas(registros):
    """Acrescenta as colunas de receita e período aos registros limpos."""
    nomes_meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }
    transformados = []

    for registro in registros:
        linha = dict(registro)
        receita_total = round(linha["quantidade"] * linha["preco_unitario"], 2)
        mes = linha["data_venda"].month

        if mes <= 3:
            trimestre = "Q1"
        elif mes <= 6:
            trimestre = "Q2"
        elif mes <= 9:
            trimestre = "Q3"
        else:
            trimestre = "Q4"

        if receita_total < 500:
            faixa_receita_item = "Baixo Valor"
        elif receita_total < 5000:
            faixa_receita_item = "Médio Valor"
        else:
            faixa_receita_item = "Alto Valor"

        linha["receita_total"] = receita_total
        linha["mes"] = mes
        linha["mes_nome"] = nomes_meses[mes]
        linha["trimestre"] = trimestre
        linha["ano"] = linha["data_venda"].year
        linha["faixa_receita_item"] = faixa_receita_item
        transformados.append(linha)

    return transformados


def calcular_metricas(registros):
    """Calcula as métricas de vendas por mês, produto, categoria e região."""
    totais_mes = defaultdict(lambda: {"receita_total": 0.0, "quantidade": 0, "n_vendas": 0})
    totais_produto = defaultdict(float)
    totais_categoria = defaultdict(float)
    totais_regiao = defaultdict(lambda: {"receita_total": 0.0, "n_vendas": 0})

    for linha in registros:
        chave_mes = (linha["ano"], linha["mes"])
        totais_mes[chave_mes]["receita_total"] += linha["receita_total"]
        totais_mes[chave_mes]["quantidade"] += linha["quantidade"]
        totais_mes[chave_mes]["n_vendas"] += 1
        totais_produto[linha["produto"]] += linha["receita_total"]
        totais_categoria[linha["categoria"]] += linha["receita_total"]
        totais_regiao[linha["regiao"]]["receita_total"] += linha["receita_total"]
        totais_regiao[linha["regiao"]]["n_vendas"] += 1

    por_mes = [
        {
            "ano": ano,
            "mes": mes,
            "receita_total": round(valores["receita_total"], 2),
            "quantidade": valores["quantidade"],
            "n_vendas": valores["n_vendas"],
        }
        for (ano, mes), valores in sorted(totais_mes.items())
    ]
    top_produtos = [
        {"produto": produto, "receita_total": round(receita, 2)}
        for produto, receita in sorted(totais_produto.items(), key=lambda item: item[1], reverse=True)[:5]
    ]
    por_categoria = [
        {"categoria": categoria, "receita_total": round(receita, 2)}
        for categoria, receita in sorted(totais_categoria.items(), key=lambda item: item[1], reverse=True)
    ]
    por_regiao = [
        {
            "regiao": regiao,
            "receita_total": round(valores["receita_total"], 2),
            "ticket_medio": round(valores["receita_total"] / valores["n_vendas"], 2),
        }
        for regiao, valores in sorted(
            totais_regiao.items(), key=lambda item: item[1]["receita_total"], reverse=True
        )
    ]
    metricas = {
        "por_mes": por_mes,
        "top_produtos": top_produtos,
        "por_categoria": por_categoria,
        "por_regiao": por_regiao,
    }

    print("\n=== MÉTRICAS POR MÊS ===")
    for linha in por_mes:
        print(linha)
    print("\n=== TOP 5 PRODUTOS ===")
    for linha in top_produtos:
        print(linha)
    print("\n=== MÉTRICAS POR CATEGORIA ===")
    for linha in por_categoria:
        print(linha)
    print("\n=== MÉTRICAS POR REGIÃO ===")
    for linha in por_regiao:
        print(linha)

    return metricas


def main():
    """Executa o fluxo de preparação e análise das vendas."""
    diretorio_projeto = Path(__file__).resolve().parent
    caminho_csv = diretorio_projeto / "vendas.csv"
    gerar_dataset_vendas(caminho_csv)
    registros = carregar_dataset(caminho_csv)
    inspecionar_dados(registros)
    registros_limpos, _ = limpar_dados(registros)
    registros_transformados = criar_colunas_derivadas(registros_limpos)
    calcular_metricas(registros_transformados)


if __name__ == "__main__":
    main()
