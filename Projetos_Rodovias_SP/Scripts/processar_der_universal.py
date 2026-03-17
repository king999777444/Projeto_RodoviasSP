import pandas as pd
import geopandas as gpd
import os
import glob

pasta_geo = "Entrada_Geometria"
pasta_der_in = "Entrada_Dados/DER"
pasta_der_out = "Saida_Dados/DER"

if not os.path.exists(pasta_der_out): os.makedirs(pasta_der_out)
arquivo_malha_shp = os.path.join(pasta_geo, "MALHA_OUT.shp")

print("--> PROCESSAMENTO DER: VERSÃO FINAL (COLUNAS EXATAS)")

try:
    gdf_geo = gpd.read_file(arquivo_malha_shp).to_crs(epsg=4326)
except:
    print("ERRO CRÍTICO: Malha não encontrada.")
    exit()

def limpar_nome(nome): return str(nome).replace(" ", "").replace("-", "").upper().strip()
gdf_geo['match_code'] = gdf_geo['Rodovia'].apply(limpar_nome)
geo_dict = dict(tuple(gdf_geo.groupby('match_code')))

arquivos = glob.glob(os.path.join(pasta_der_in, "*"))
lista_finais = []

for arq in arquivos:
    if not (arq.endswith('.csv') or arq.endswith('.xlsx')): continue
    if "~$" in arq: continue
    
    nome_arq = os.path.basename(arq)
    ano = "".join(filter(str.isdigit, nome_arq))
    if len(ano) != 4: ano = "0000"
    
    print(f"\n--> DER: {nome_arq} ({ano})")
    
    try:
        if arq.endswith('.csv'):
            try: df = pd.read_csv(arq, sep=';', encoding='latin1', on_bad_lines='skip')
            except: df = pd.read_csv(arq, sep=',', encoding='latin1', on_bad_lines='skip')
        else:
            df = pd.read_excel(arq)

        df.columns = [str(c).lower().strip() for c in df.columns]
        
        col_moto = 'vdm_moto'
        col_pass = 'vdm_passeio'
        col_com = 'vdm_com'
        col_total = 'vdm_total'
        
        col_rod = next((c for c in df.columns if 'rod' in c or 'sp' in c), None)
        col_km = next((c for c in df.columns if 'km' in c or 'local' in c), None)

        missing = []
        if col_moto not in df.columns: missing.append(col_moto)
        if col_pass not in df.columns: missing.append(col_pass)
        if col_com not in df.columns: missing.append(col_com)
        
        if missing:
            print(f"   ⚠️ AVISO: Faltando colunas neste arquivo: {missing}")
            print(f"   Colunas disponíveis: {list(df.columns)}")
        else:
            print(f"   > Colunas identificadas com sucesso!")

        if not col_rod or not col_km:
            print("   ERRO: Não achei coluna de Rodovia ou KM. Pulando.")
            continue

        df['match_code'] = df[col_rod].apply(limpar_nome)
        
        def to_num(x): 
            try: return float(str(x).replace(',', '.'))
            except: return 0.0

        df['KM_FINAL'] = df[col_km].apply(to_num)

        fator = 1
        if col_total in df.columns:
             media = df[col_total].apply(to_num).mean()
             if media > 50000: 
                 fator = 30
                 print(f"   > Aplicando correção (Fator 30) - Média detectada: {int(media)}")
        
        resultados = []
        for idx, row in df.iterrows():
            rod = row['match_code']
            km = row['KM_FINAL']
            
            if rod in geo_dict:
                trechos = geo_dict[rod]
                match = trechos[(trechos['KmInicial'] <= km) & (trechos['KmFinal'] >= km)]
                if not match.empty:
                    geom = match.iloc[0]['geometry']
                    ponto = geom.interpolate(abs(km - match.iloc[0]['KmInicial'])/abs(match.iloc[0]['KmFinal']-match.iloc[0]['KmInicial']), normalized=True)
                    
                    dado = {'rodovia': rod, 'km': km, 'ano': ano, 'origem': 'DER', 'geometry': ponto}
                    
                    if col_moto in df.columns: dado['cat_moto'] = int(to_num(row[col_moto]) / fator)
                    if col_pass in df.columns: dado['cat_passeio'] = int(to_num(row[col_pass]) / fator)
                    if col_com in df.columns: dado['cat_comercial'] = int(to_num(row[col_com]) / fator)
                    if col_total in df.columns: dado['vdm_total'] = int(to_num(row[col_total]) / fator)
                    
                    resultados.append(dado)
        
        if resultados:
            gdf = gpd.GeoDataFrame(resultados, crs="EPSG:4326")
            nome_saida = f"DER_DETALHADO_{ano}.shp"
            gdf.to_file(os.path.join(pasta_der_out, nome_saida))
            lista_finais.append(gdf)
            print(f"   > Salvo: {len(resultados)} pontos em {nome_saida}")

    except Exception as e:
        print(f"   ERRO: {e}")

if lista_finais:
    final = pd.concat(lista_finais, ignore_index=True)
    final.to_file(os.path.join(pasta_der_out, "DER_CONSOLIDADO_DETALHADO.shp"))
    print("\nSUCESSO: Base DER consolidada com categorias!")