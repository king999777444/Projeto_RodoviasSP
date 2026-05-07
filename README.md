# 🛣️ Pipeline Geoespacial de Tráfego Rodoviário (SP)

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-Spatial_Data-1572B6?logo=pandas&logoColor=white)](https://geopandas.org/)
[![Linux](https://img.shields.io/badge/OS-Fedora%20/%20Arch-0B2C4A?logo=fedora&logoColor=white)](https://getfedora.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Refactoring](https://img.shields.io/badge/Status-Refatorando_para_POO-orange?style=flat-square)]()

Este projeto é uma plataforma de **Engenharia de Dados e Inteligência Geográfica** desenvolvida para consolidar, auditar e espacializar o histórico de tráfego rodoviário do Estado de São Paulo (2013-2025). O objetivo central é prover uma base de dados unificada e georreferenciada para simulações de impactos operacionais e financeiros na transição para o modelo de pedágio **Free-Flow**.

## 🎯 Objetivos do Projeto

A gestão de tráfego em São Paulo sofre com a **fragmentação de dados**. Órgãos diferentes (DER-SP, ARTESP e PNCT) utilizam padrões distintos. Este pipeline resolve esse "gap" através de:

- **Unificação de Fontes Heterogêneas:** Integração de planilhas complexas do DER, ARTESP e PNCT (Governo Federal).
- **Referenciamento Linear:** Conversão de marcos quilométricos em coordenadas geográficas exatas (`Lat/Long`) utilizando a malha rodoviária oficial.
- **Análise Multitemporal:** Série histórica do VMDa (Volume Médio Diário Anual) segmentada por categorias veiculares.
- **Garantia de Qualidade (QA):** Scripts de auditoria forense para detectar anomalias em 117 colunas de dados.

## 🏗️ Arquitetura do Sistema (Roadmap POO)

Estamos atualmente refatorando o sistema de scripts procedurais para uma arquitetura **Orientada a Objetos (OOP)**, garantindo escalabilidade e modularidade:

```bash
.
├── core/                   # Classes base do sistema
│   ├── extractor.py        # Abstração para leitura de DER/ARTESP/PNCT
│   ├── geocoder.py         # Lógica de Referenciamento Linear
│   └── validator.py        # Motor de auditoria e consistência
├── data/
│   ├── input/              # Bases brutas (CSV/XLSX)
│   ├── geometry/           # Shapefiles da malha rodoviária oficial
│   └── output/             # GeoPackages e Shapefiles consolidados
├── notebooks/              # Análises exploratórias e validações
└── main.py                 # Orquestrador do Pipeline
