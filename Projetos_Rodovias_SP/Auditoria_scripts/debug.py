import pandas as pd
import geopandas as gpd
import os
import glob
from shapely.geometry import Point

# --- CONFIGURAÇÕES ---
pasta_geo = "Entrada_Geometria"
pasta_artesp = "Entrada_Dados/ARTESP" # Confirme se seus CSVs estão aqui
pasta_saida = "Saida_Dados/ARTESP"

if not os.path.exists(pasta_saida): os.makedirs(pasta_saida)
arquivo_malha_shp = os.path.join(pasta_geo, "MALHA_OUT.shp")

print("--> INICIANDO DIAGNÓSTICO DETALHADO ARTESP")

# 1. Carregar Geometria e Mostrar Exemplos
print("1. Lendo Malha Rodoviária...")
try:
    gdf_geo = gpd.read_file(arquivo_malha_shp)
except:
    print(f"ERRO CRÍTICO: Não achei {arquivo_malha_shp}")
    exit()

def limpar_nome(nome):
    if not isinstance(nome, str): return ""
    return nome.replace(" ", "").replace("-", "").upper().strip()

gdf_geo['match_code'] = gdf_geo['Rodovia'].apply(limpar_nome)
geo_dict = dict(tuple(gdf_geo.groupby('match_code')))

# MOSTRAR EXEMPLOS DA MALHA
print(f"   > Total de rodovias na malha: {len(geo_dict)}")
print(f"   > Exemplos de nomes na Malha (Como o script vê): {list(geo_dict.keys())[:5]}")

# 2. Ler CSVs
arquivos_sat = glob.glob(os.path.join(pasta_artesp, "*.csv"))
if not arquivos_sat: 
    print(f"ERRO: Nenhum CSV encontrado em {pasta_artesp}")
    exit()

for arq in arquivos_sat:
    nome_arq = os.path.basename(arq)
    print(f"\n---------------------------------------------------")
    print(f"ANALISANDO ARQUIVO: {nome_arq}")
    
    try:
        # Tenta ler e mostra o que leu
        try:
            df_sat = pd.read_csv(arq, sep=';', encoding='latin1', on_bad_lines='skip', nrows=5)
            sep_usado = ";"
        except:
            df_sat = pd.read_csv(arq, sep=',', encoding='latin1', on_bad_lines='skip', nrows=5)
            sep_usado = ","
            
        print(f"   > Separador detectado: '{sep_usado}'")
        print(f"   > Colunas encontradas: {list(df_sat.columns)}")
        
        # Recarrega arquivo inteiro
        if sep_usado == ';':
            df_sat = pd.read_csv(arq, sep=';', encoding='latin1', on_bad_lines='skip')
        else:
            df_sat = pd.read_csv(arq, sep=',', encoding='latin1', on_bad_lines='skip')

        # Tenta mapear colunas
        cols_map = {c.upper(): c for c in df_sat.columns}
        
        col_rod = next((cols_map[c] for c in cols_map if 'RODOVIA' in c), None)
        col_km = next((cols_map[c] for c in cols_map if 'KM' in c), None)
        
        print(f"   > Coluna Rodovia identificada: {col_rod}")
        print(f"   > Coluna KM identificada: {col_km}")

        # Verifica categorias
        col_moto = next((cols_map[c] for c in cols_map if 'MOTO' in c), None)
        col_pass = next((cols_map[c] for c in cols_map if 'PASSEIO' in c or 'LEVE' in c), None)
        col_com = next((cols_map[c] for c in cols_map if 'COMERCIAL' in c or 'PESADO' in c), None)
        
        print(f"   > Categoria MOTO: {col_moto}")
        print(f"   > Categoria PASSEIO: {col_pass}")
        print(f"   > Categoria COMERCIAL: {col_com}")

        if not col_rod:
            print("   🔴 FALHA: Não achei coluna de Rodovia. Pulando arquivo.")
            continue

        # Teste de Match (O Pulo do Gato)
        df_sat['match_code'] = df_sat[col_rod].apply(limpar_nome)
        
        exemplos_csv = df_sat['match_code'].unique()[:5]
        print(f"   > Exemplos de nomes no CSV: {exemplos_csv}")
        
        # Conta quantos batem
        matches = df_sat[df_sat['match_code'].isin(geo_dict.keys())]
        total_rows = len(df_sat)
        total_matches = len(matches)
        
        print(f"   > LINHAS TOTAIS: {total_rows}")
        print(f"   > LINHAS QUE DERAM MATCH NA MALHA: {total_matches}")
        
        if total_matches == 0:
            print("   🔴 FALHA GRAVE: Nenhuma rodovia do CSV existe no Shapefile. Verifique os nomes acima!")
        else:
            print("   🟢 SUCESSO: O cruzamento está funcionando! O erro pode ser no salvamento.")

    except Exception as e:
        print(f"   🔴 ERRO DE EXECUÇÃO: {e}")