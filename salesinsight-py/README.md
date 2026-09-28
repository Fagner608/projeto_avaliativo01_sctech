# SalesInsight PY

## Sobre o projeto

Projeto de análise de vendas desenvolvido em Python. O programa gera um conjunto de dados, faz a limpeza dos registros, calcula métricas, segmenta os clientes e exporta os resultados.

## O que é analisado

- Receita e quantidade de vendas por mês
- Produtos e categorias com maior receita
- Receita e ticket médio por região
- Clientes com maior gasto
- Segmentação em Bronze, Prata e Ouro

## Como executar

É necessário ter o Python 3.10 ou superior instalado.

```bash
cd salesinsight-py
python salesinsight.py
```

Os arquivos gerados ficam na pasta `outputs`.

## Conceitos utilizados

- Variáveis, listas e dicionários
- Condicionais e repetições
- Funções, parâmetros e retornos
- Funções lambda
- Leitura e escrita de CSV e JSON
- Datas com `datetime`
- Expressões regulares com `re`
- Git e GitHub

## Decisão técnica

Os registros com data inválida ou valores ausentes em quantidade e preço são removidos. Esses campos são necessários para calcular a receita e mantê-los poderia gerar resultados incorretos.

## Vídeo de demonstração

Link: [gravacao](https://drive.google.com/file/d/1fJs7hGUaU2LPEu-gbfXNV7ZsgGm3gjom/view?usp=sharing)
