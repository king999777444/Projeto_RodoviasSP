# 🛣️ Integração e Análise Geoespacial de Dados de Tráfego - São Paulo (Free-Flow)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Spatial_Data-lightgrey?logo=geopandas)
![NVIDIA RAPIDS](https://img.shields.io/badge/RAPIDS-GPU_Acceleration-76B900?logo=nvidia)
![POO](https://img.shields.io/badge/Architecture-POO-orange)

Este repositório contém o *pipeline* de Engenharia de Dados Espaciais desenvolvido como parte de um projeto de Iniciação Científica na **Universidade de São Paulo (Poli-USP)**. O projeto tem como objetivo caracterizar, auditar e integrar as bases de dados georreferenciadas da rede viária e de fluxo de tráfego do Estado de São Paulo para subsidiar a modelagem de impactos de pedágios *Free-Flow*.

## 🎯 Objetivo
A transição das praças de pedágio convencionais para o modelo *free-flow* exige a construção de uma linha de base (*baseline*) confiável do Volume Diário Médio (VDM). Este projeto supera a fragmentação histórica e metodológica dos dados ao unificar três bases jurisdicionais distintas:
*   **DER/SP:** Departamento de Estradas de Rodagem.
*   **ARTESP:** Agência de Transporte do Estado de São Paulo (Rede Concessionada).
*   **PNCT (DNIT):** Plano Nacional de Contagem de Tráfego (Malha Federal).

## 🚀 Arquitetura e Tecnologias

Para lidar com *gigabytes* de dados históricos de contagem (2013-2025) e pesadas geometrias rodoviárias, o *pipeline* foi refatorado utilizando **Programação Orientada a Objetos (POO)** e técnicas avançadas de processamento:

*   **Extratores Polimórficos & Downcasting:** Otimização agressiva de consumo de memória RAM ao carregar as séries históricas longas.
*   **PipelineOrchestrator (Multiprocessing):** Orquestração e paralelismo em múltiplos núcleos de CPU para a carga massiva das matrizes de tráfego.
*   **GPU Acceleration (Fallback Pattern):** Utilização das bibliotecas **NVIDIA RAPIDS** e **cuDF** como *fallback* para acelerar cálculos pesados de geometria espacial.

## 🧠 Algoritmos Principais

### 1. Spatial Matcher (Auditoria Geográfica)
Um dos maiores desafios era o "ruído" estatístico de contagem, onde o DER, a ARTESP e o DNIT possuíam equipamentos no mesmo trecho viário, gerando sobreposições. O algoritmo **Spatial Matcher** realiza o cruzamento topológico (referenciamento linear) desses postos e filtra as redundâncias, impedindo que o volume (VDM) seja inflado artificialmente em simulações futuras.

### 2. Quality Assurance & Self-Healing
Módulo autônomo desenhado para auditar falhas críticas estruturais nos dados brutos. Como destaque, esse mecanismo recuperou matematicamente a base de 2021 do PNCT (que sofria com a ausência de marcos quilométricos), cruzando as coordenadas remanescentes com os *links* espaciais e garantindo a continuidade topológica da malha federal em São Paulo sem pontos cegos de fronteira.

## 📊 Formatos e Saídas (Outputs)
O pipeline converte estruturas tabulares complexas para formatos longitudinais largos (*Wide Format*). Os dados finais são exportados e altamente otimizados para integração com *Machine Learning*, Modelos de Alocação de Tráfego e SIG (Sistemas de Informações Geográficas como o QGIS):
*   `Shapefiles` (.shp) anuais e unificados.
*   `GeoPackage` (.gpkg)
*   `Apache Parquet` (.parquet)

## 🛠️ Como executar

1. Clone este repositório:
```bash
   git clone [https://github.com/king999777444/Projeto_RodoviasSP.git](https://github.com/king999777444/Projeto_RodoviasSP.git)
```

Instale as dependências:

pip install -r requirements.txt

Execute o módulo principal para iniciar a integração (Orchestrator):

python main.py


Autores e Apoio
Lucas Pereira Garijo (Graduando - Poli-USP)

Alexandre Duarte (Co-autor / Modelagem)

Prof. Dr. Cassiano Augusto Isler (Orientador)

Pesquisa desenvolvida com o apoio financeiro da Fundação de Apoio à Universidade de São Paulo (FUSP).


Dica rápida para subir esse arquivo no seu repositório:**
Na pasta do seu projeto, crie esse arquivo, cole o texto e no terminal rode:
```bash
git add README.md
git commit -m "Docs: Adiciona README com arquitetura e documentação do projeto"
git push origin main

   ```bash
   git clone [https://github.com/king999777444/Projeto_RodoviasSP.git](https://github.com/king999777444/Projeto_RodoviasSP.git)
