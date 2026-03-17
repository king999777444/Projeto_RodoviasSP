import geopandas as gpd
import pandas as pd
import os
import numpy as np

arquivo_linhas = os.path.join("Entrada_Geometria", "MALHA_OUT.shp")
arq_der = os.path.join("Saida_Dados", "DER", "DER_CONSOLIDADO_DETALHADO.shp")
arq_artesp = os.path.join("Saida_Dados", "ARTESP", "ARTESP_CONSOLIDADO_DETALHADO.shp")

pasta_saida = "Processamento_Final_Rede"
if not os.path.exists(pasta_saida): os.makedirs(pasta_saida)

print("--> GERANDO REDE FINAL (COM ORDENAÇÃO FORÇADA DE COLUNAS)")

try:
    gdf_linhas = gpd.read_file(arquivo_linhas).to_crs(epsg=4326)
except:
    print("ERRO: MALHA_OUT.shp não encontrado.")
    exit()

def limpar_nome(nome): return str(nome).replace(" ", "").replace("-", "").upper().strip()
gdf_linhas['match_code'] = gdf_linhas['Rodovia'].apply(limpar_nome)
gdf_linhas['KmInicial'] = pd.to_numeric(gdf_linhas['KmInicial'], errors='coerce').fillna(0)
gdf_linhas['KmFinal'] = pd.to_numeric(gdf_linhas['KmFinal'], errors='coerce').fillna(0)

colunas_originais = list(gdf_linhas.columns)
if 'geometry' in colunas_originais: colunas_originais.remove('geometry')

print("2. Carregando dados...")
bases = []
def carregar_base(caminho, nome_origem):
    if os.path.exists(caminho):
        gdf = gpd.read_file(caminho)
        gdf['origem_fixa'] = nome_origem
        col_ano = next((c for c in gdf.columns if 'ano' in c.lower()), None)
        if col_ano: gdf['ano_ref'] = gdf[col_ano].astype(str)
        else: gdf['ano_ref'] = '0000'
        return gdf
    return gpd.GeoDataFrame()

bases.append(carregar_base(arq_der, "DER"))
bases.append(carregar_base(arq_artesp, "ARTESP"))
df_total = pd.concat(bases, ignore_index=True)

mapa_cat = {
    'cat_moto': 'MOT', 'vdm_moto': 'MOT',
    'cat_passeio': 'PAS', 'cat_passei': 'PAS', 'vdm_passeio': 'PAS', 'vdm_passei': 'PAS',
    'cat_comercial': 'COM', 'cat_comerc': 'COM', 'vdm_comercial': 'COM', 'vdm_com': 'COM'
}
mapa_fonte = {'ARTESP': 'ART', 'DER': 'DER', 'PNCT': 'PNC'}

anos = sorted([a for a in df_total['ano_ref'].unique() if a != '0000'])
fontes = ['ART', 'DER'] 
categorias = ['MOT', 'PAS', 'COM']

colunas_ordenadas = []
for ano in anos:
    ano_curto = ano[-2:]
    for fonte in fontes:
        for cat in categorias:
            nome_col = f"{ano_curto}_{fonte}_{cat}"
            colunas_ordenadas.append(nome_col)

print(f"   > Ordem definida: {colunas_ordenadas[:6]} ... até ... {colunas_ordenadas[-3:]}")

cols_existentes = [c for c in df_total.columns if c in mapa_cat]
df_total['match_code'] = df_total['rodovia'].apply(limpar_nome)
df_total['km'] = pd.to_numeric(df_total['km'], errors='coerce')
dados_por_rodovia = dict(tuple(df_total.groupby('match_code')))

print(f"3. Processando {len(gdf_linhas)} trechos...")
resultados = []

for idx, linha in gdf_linhas.iterrows():
    rod = linha['match_code']
    kmi, kmf = linha['KmInicial'], linha['KmFinal']
    
    nova_linha = linha.to_dict()
    
    for col in colunas_ordenadas:
        nova_linha[col] = 0

    if rod in dados_por_rodovia:
        df_rod = dados_por_rodovia[rod]
        pts = df_rod[(df_rod['km'] >= min(kmi, kmf)) & (df_rod['km'] <= max(kmi, kmf))]
        
        if not pts.empty:
            for (ano, origem), grupo in pts.groupby(['ano_ref', 'origem_fixa']):
                if ano == '0000': continue
                
                ano_curto = ano[-2:]
                fonte_curta = mapa_fonte.get(origem, origem[:3])
                
                for cat_original in cols_existentes:
                    if cat_original in grupo.columns:
                        media = grupo[cat_original].mean()
                        if pd.notna(media) and media > 0:
                            tipo_final = mapa_cat.get(cat_original)
                            nome_col = f"{ano_curto}_{fonte_curta}_{tipo_final}"
                            nova_linha[nome_col] = int(media)
                            
    resultados.append(nova_linha)

print("4. Organizando e Salvando...")
gdf_final = gpd.GeoDataFrame(resultados, crs=gdf_linhas.crs)

cols_finais = colunas_originais + colunas_ordenadas + ['geometry']
cols_finais = [c for c in cols_finais if c in gdf_final.columns]

gdf_final = gdf_final[cols_finais]

nome_arq = "MALHA_FINAL_ORDENADA.shp"
gdf_final.to_file(os.path.join(pasta_saida, nome_arq))

print(f"SUCESSO! Arquivo salvo em: {os.path.join(pasta_saida, nome_arq)}")