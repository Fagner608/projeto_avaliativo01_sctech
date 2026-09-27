import csv
import re
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


def main():
    """Executa as etapas de geração, leitura, inspeção e limpeza dos dados."""
    diretorio_projeto = Path(__file__).resolve().parent
    caminho_csv = diretorio_projeto / "vendas.csv"
    gerar_dataset_vendas(caminho_csv)
    registros = carregar_dataset(caminho_csv)
    inspecionar_dados(registros)
    limpar_dados(registros)


if __name__ == "__main__":
    main()
