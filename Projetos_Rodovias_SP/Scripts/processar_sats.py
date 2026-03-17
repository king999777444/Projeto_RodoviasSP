import pandas as pd
import geopandas as gpd
import os
import glob
from shapely.geometry import Point

pasta_geo = "Entrada_Geometria"
pasta_artesp = "Entrada_Dados/ARTESP"
pasta_saida = "Saida_Dados/ARTESP"

if not os.path.exists(pasta_saida): os.makedirs(pasta_saida)
arquivo_malha_shp = os.path.join(pasta_geo, "MALHA_OUT.shp")

print("--> PROCESSAMENTO ARTESP DETALHADO (POR CATEGORIA)")

try:
    gdf_geo = gpd.read_file(arquivo_malha_shp)
    if gdf_geo.crs and gdf_geo.crs.to_epsg() != 4326:
        gdf_geo = gdf_geo.to_crs(epsg=4326)
except:
    print("ERRO: Malha não encontrada.")
    exit()

def limpar_nome(nome):
    if not isinstance(nome, str): return ""
    return nome.replace(" ", "").replace("-", "").upper().strip()

gdf_geo['match_code'] = gdf_geo['Rodovia'].apply(limpar_nome)
geo_dict = dict(tuple(gdf_geo.groupby('match_code')))

arquivos_sat = glob.glob(os.path.join(pasta_artesp, "*.csv"))

lista_shapes_finais = []

for arq in arquivos_sat:
    nome_arq = os.path.basename(arq)
    ano = "".join(filter(str.isdigit, nome_arq))
    if len(ano) != 4: continue
    
    print(f"\n--> Processando ARTESP: {ano}")
    
    try:
        df_sat = pd.read_csv(arq, sep=',', encoding='latin1', on_bad_lines='skip')
        
        if len(df_sat.columns) < 5:
             df_sat = pd.read_csv(arq, sep=';', encoding='latin1', on_bad_lines='skip')

        df_sat.columns = [c.upper().strip() for c in df_sat.columns]
        
        col_rod = next((c for c in df_sat.columns if 'RODOVIA' in c), None)
        col_km = next((c for c in df_sat.columns if 'KM' in c), None)
        col_moto = next((c for c in df_sat.columns if 'MOTO' in c), None)
        col_pass = next((c for c in df_sat.columns if 'PASSEIO' in c or 'LEVE' in c), None)
        col_com = next((c for c in df_sat.columns if 'COMERCIAL' in c or 'PESADO' in c), None)
        
        if not col_rod or not col_km:
            print(f"   ERRO: Colunas não encontradas. Cols: {list(df_sat.columns)}")
            continue

        df_sat['match_code'] = df_sat[col_rod].apply(limpar_nome)
        df_sat['KM_FLOAT'] = pd.to_numeric(df_sat[col_km], errors='coerce').fillna(0)
        col_compl = next((c for c in df_sat.columns if 'COMPLEMENTO' in c), None)
        if col_compl:
            df_sat['KM_FLOAT'] += (pd.to_numeric(df_sat[col_compl], errors='coerce').fillna(0) / 1000.0)
            
        cols_cat = [c for c in [col_moto, col_pass, col_com] if c]
        for c in cols_cat:
            df_sat[c] = pd.to_numeric(df_sat[c], errors='coerce').fillna(0)

        agg_dict = {c: 'mean' for c in cols_cat}
        
        df_vdm = df_sat.groupby(['match_code', 'KM_FLOAT']).agg(agg_dict).reset_index()
        
        rename_map = {}
        if col_moto: rename_map[col_moto] = 'vdm_moto'
        if col_pass: rename_map[col_pass] = 'vdm_passeio'
        if col_com: rename_map[col_com] = 'vdm_comercial'
        df_vdm.rename(columns=rename_map, inplace=True)
        resultados = []
        for idx, row in df_vdm.iterrows():
            rod = row['match_code']
            km = row['KM_FLOAT']
            
            if rod in geo_dict:
                trechos = geo_dict[rod]
                match = trechos[(trechos['KmInicial'] <= km) & (trechos['KmFinal'] >= km)]
                if not match.empty:
                    geom = match.iloc[0]['geometry']
                    kmi, kmf = match.iloc[0]['KmInicial'], match.iloc[0]['KmFinal']
                    dist = abs(kmf - kmi)
                    ponto = geom.interpolate(abs(km - kmi)/dist, normalized=True) if dist > 0.001 else geom.centroid
                    
                    dados_ponto = {
                        'rodovia': rod,
                        'km': km,
                        'ano': ano,
                        'origem': 'ARTESP',
                        'geometry': ponto
                    }
                    if 'vdm_moto' in df_vdm.columns: dados_ponto['cat_moto'] = int(row['vdm_moto'])
                    if 'vdm_passeio' in df_vdm.columns: dados_ponto['cat_passeio'] = int(row['vdm_passeio'])
                    if 'vdm_comercial' in df_vdm.columns: dados_ponto['cat_comercial'] = int(row['vdm_comercial'])
                    
                    resultados.append(dados_ponto)

        print(f"   > Pontos gerados: {len(resultados)}")

        if resultados:
            gdf = gpd.GeoDataFrame(resultados, crs="EPSG:4326")
            nome_saida = f"ARTESP_DETALHADO_{ano}.shp"
            gdf.to_file(os.path.join(pasta_saida, nome_saida))
            lista_shapes_finais.append(gdf)

    except Exception as e:
        print(f"   ERRO: {e}")

if lista_shapes_finais:
    consolidado = pd.concat(lista_shapes_finais, ignore_index=True)
    consolidado.to_file(os.path.join(pasta_saida, "ARTESP_CONSOLIDADO_DETALHADO.shp"))
    print("SUCESSO: Consolidação ARTESP concluída.")
    