import geopandas as gpd
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
arquivo_final = "Processamento_Final_Rede/MALHA_FINAL_ORDENADA.shp"

print(f"--> AUDITORIA DE ESTRUTURA: {arquivo_final}")

if not os.path.exists(arquivo_final):
    print("ERRO: Arquivo não encontrado.")
    exit()

# Carrega apenas o cabeçalho (para ser rápido)
gdf = gpd.read_file(arquivo_final, rows=1)
colunas = sorted(list(gdf.columns))

print(f"\nTOTAL DE COLUNAS NO ARQUIVO: {len(colunas)}")

# Filtra colunas de dados (formato YY_SRC_CAT ou VDM_...)
colunas_dados = [c for c in colunas if c[0].isdigit() and '_' in c] 
# (O filtro acima pega '23_ART_MOT', '16_DER_PAS', etc. pois começam com número)

print(f"TOTAL DE COLUNAS DE TRÁFEGO (VDM): {len(colunas_dados)}")
print("-" * 60)

# Análise Detalhada
anos = set()
fontes = set()
categorias = set()

for col in colunas_dados:
    partes = col.split('_')
    if len(partes) == 3:
        ano, fonte, cat = partes
        anos.add(ano)
        fontes.add(fonte)
        categorias.add(cat)

print(f"ANOS ENCONTRADOS ({len(anos)}): {sorted(list(anos))}")
print(f"FONTES ENCONTRADAS: {sorted(list(fontes))}")
print(f"CATEGORIAS ENCONTRADAS: {sorted(list(categorias))}")

print("-" * 60)
print("LISTAGEM COMPLETA POR ANO:")

# Gera a matriz esperada vs encontrada
for ano in sorted(list(anos)):
    print(f"\nANO 20{ano}:")
    for fonte in sorted(list(fontes)):
        # Verifica se as 3 categorias existem para esta fonte/ano
        cats_existentes = []
        for cat in sorted(list(categorias)):
            nome_col = f"{ano}_{fonte}_{cat}"
            if nome_col in colunas:
                cats_existentes.append(cat)
        
        if cats_existentes:
            print(f"   > {fonte}: {cats_existentes}")
        else:
            print(f"   > {fonte}: [NENHUMA COLUNA ENCONTRADA]")

print("-" * 60)
print("VEREDITO:")
if len(colunas_dados) > 70:
    print("✅ SUCESSO: Mais de 70 colunas de dados detectadas!")
else:
    print(f"⚠️ ATENÇÃO: Encontrei apenas {len(colunas_dados)} colunas de dados. Verifique se falta algum ano.")