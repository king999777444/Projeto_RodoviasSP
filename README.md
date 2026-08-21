# 🛣️ Pipeline Geoespacial de Tráfego - São Paulo

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Spatial_Analysis-brightgreen?logo=geopandas)
![NVIDIA RAPIDS](https://img.shields.io/badge/NVIDIA_RAPIDS-cuDF_GPU-76B900?logo=nvidia&logoColor=white)
![Parquet](https://img.shields.io/badge/Apache_Parquet-Big_Data-orange?logo=apache)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Sistema avançado de Engenharia de Dados Espaciais focado na ingestão, auditoria e unificação de grandes volumes de dados de tráfego rodoviário do Estado de São Paulo. O projeto cruza dados históricos do **DER-SP**, **ARTESP** e **PNCT (DNIT)**, aplicando referenciamento linear e análise de redundância geográfica.

Este projeto foi desenhado com uma arquitetura Orientada a Objetos (POO) e otimizado para execução em servidores Linux de alta performance, utilizando paralelismo de CPU e aceleração de GPU.

---

## ✨ Arquitetura e Funcionalidades

*   **Ingestão Orientada a Objetos:** Classes extratoras padronizadas (`BaseExtractor`, `DERExtractor`, etc.) que aplicam *downcasting* dinâmico de tipos (ex: `float64` para `float32` ou `category`) para otimização massiva de memória RAM.
*   **Orquestração e Paralelismo:** Uso de `ProcessPoolExecutor` para processamento concorrente de múltiplos arquivos e bases de dados, bypassando o GIL (Global Interpreter Lock) do Python.
*   **Aceleração via GPU (NVIDIA RAPIDS):** Implementação de *Fallback Pattern* que detecta automaticamente a presença de hardware NVIDIA no cluster e converte DataFrames Pandas para `cuDF`, acelerando operações matemáticas na VRAM.
*   **Auditoria Geográfica (Spatial Matching):** Algoritmos de intersecção espacial (`sjoin`) baseados no motor C++ `pyogrio` e `shapely`. Identifica sobreposições e redundâncias de infraestrutura de contagem de tráfego no mesmo trecho geométrico e ano.
*   **Quality Assurance (QA) Automatizado:** Classe de *Self-Healing* que detecta marcos quilométricos absurdos, anomalias de formatação e remove duplicatas temporais antes da injeção no banco de dados.

---

## 📂 Estrutura do Projeto

A organização dos diretórios segue os padrões da indústria para Engenharia de Dados:

```text
trafego-sp-geo/
├── core/                   # Regras de Negócio e Motores
│   ├── extractor.py        # Módulos de extração (DER, ARTESP, PNCT)
│   ├── orchestrator.py     # Gerenciamento de Threads e GPU
│   ├── geocoder.py         # Referenciamento Linear Espacial
│   ├── spatial_matcher.py  # Algoritmo de cruzamento de radares/trechos
│   └── validator.py        # Motor de auditoria (QA)
├── utils/                  # Ferramentas de Suporte
│   ├── hardware.py         # Autodetect de CPU/GPU em servidores
│   └── logger.py           # Registro de anomalias detectadas
├── Auditoria_scripts/      # Scripts standalone para validação rápida
│   └── auditoria_shp.py    # Gera análises anuais de sobreposição
├── data/                   # (Ignorado no Git)
│   ├── raw/                # Planilhas brutas (.xlsx, .csv)
│   ├── geometry/           # Malhas rodoviárias oficiais (.shp)
│   └── processed/          # Arquivos consolidados (.parquet, .gpkg)
```

🚀 Como Executar
1. Ambiente Padrão (CPU)

Para rodar localmente utilizando múltiplos núcleos do processador:
```
# Criação do ambiente virtual
python -m venv venv

# Ativação (Windows)
.\venv\Scripts\activate
# Ativação (Linux/Mac)
source venv/bin/activate

# Instalação de dependências
pip install -r requirements.txt

# Executar o pipeline de auditoria espacial
python Auditoria_scripts/auditoria_shp.py
```

2. Ambiente de Alta Performance (Cluster Linux / GPU)

Para implantação em servidores de pesquisa com acesso a placas de vídeo NVIDIA:
```
# Criação de ambiente Conda isolado com RAPIDS
conda create -n trafego_gpu -c rapidsai -c conda-forge -c nvidia cudf=24.02 python=3.12 cudatoolkit=12.0
conda activate trafego_gpu

# Instalação das dependências espaciais
pip install geopandas shapely pyogrio openpyxl
```
🗺️ Formatos de Saída Suportados

O pipeline é agnóstico em relação à exportação, priorizando formatos de alta compressão e leitura para ciência de dados e SIGs (Sistemas de Informação Geográfica):

    .parquet: Para consumo rápido em modelos de Machine Learning.

    .gpkg (GeoPackage): Novo padrão da OGC para armazenamento espacial moderno.

    .shp (Shapefiles Anuais): Relatórios espaciais fatiados cronologicamente para fácil visualização no QGIS ou ArcGIS.

    .xlsx: Tabelas gerenciais formatadas para leitura humana e relatórios executivos.

👨‍💻 Autor e Pesquisa

Este projeto faz parte de iniciativas de pesquisa acadêmica em engenharia e infraestrutura, focadas na modernização da análise de dados do sistema rodoviário. Ferramentas construídas com rigor técnico para transformar dados brutos em inteligência geográfica auditável.
├── main.py                 # Ponto de entrada do pipeline unificado
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação

Este projeto foi financiado com bolsa de Iniciação Científica pela Fundação de Apoio à Universidade de São Paulo (FUSP)
