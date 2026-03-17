import geopandas as gpd
import pandas as pd
import os

arquivo_final = os.path.join("Processamento_Final_Rede", "MALHA_CONSOLIDADA_FINAL.shp")

print(f"--> AUDITANDO ARQUIVO: {arquivo_final}")

if not os.path.exists(arquivo_final):
    print("ERRO: Arquivo não encontrado.")
    exit()

gdf = gpd.read_file(arquivo_final)
print(f"Total de Trechos (Links) na Rede: {len(gdf)}")

anos = [str(a) for a in range(2013, 2026)]

print("\n--- RELATÓRIO DE PREENCHIMENTO POR ANO ---")
print(f"{'ANO':<6} | {'TRECHOS COM DADOS':<18} | {'% COBERTURA':<12} | {'MÉDIA VDM (Estado)':<15}")
print("-" * 65)

for ano in anos:
    coluna = f'VDM_{ano}'
    
    if coluna in gdf.columns:
        com_dados = gdf[gdf[coluna] > 0]
        qtd = len(com_dados)
        pct = (qtd / len(gdf)) * 100
        media = com_dados[coluna].mean() if qtd > 0 else 0
        
        print(f"{ano:<6} | {qtd:<18} | {pct:<11.1f}% | {int(media):<15}")
    else:
        print(f"{ano:<6} | COLUNA NÃO ENCONTRADA")

print("\n--- ANÁLISE DE LÓGICA ---")

total_2015 = len(gdf[gdf['VDM_2015'] > 0])
total_2016 = len(gdf[gdf['VDM_2016'] > 0])

print(f"Trechos com dados em 2015 (Só DER): {total_2015}")
print(f"Trechos com dados em 2016 (DER + ARTESP): {total_2016}")

if total_2016 > total_2015:
    print("✅ LÓGICA OK: Houve aumento de cobertura em 2016 (Entrada da base ARTESP).")
else:
    print("⚠️ ATENÇÃO: 2016 não tem mais dados que 2015. Verifique se a ARTESP foi somada corretamente.")

print("\nAUDITORIA CONCLUÍDA.")