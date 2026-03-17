import geopandas as gpd
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
arquivo_final = "Processamento_Final_Rede/MALHA_FINAL_ORDENADA.shp"

print(f"--> VERIFICADOR DE ORDEM DAS COLUNAS: {arquivo_final}")

if not os.path.exists(arquivo_final):
    print("ERRO: Arquivo não encontrado.")
    exit()

# Lê apenas a primeira linha para ser instantâneo
gdf = gpd.read_file(arquivo_final, rows=1)
colunas_reais = list(gdf.columns)

print(f"\nTOTAL DE COLUNAS: {len(colunas_reais)}")
print("="*60)
print(f"{'IDX':<5} | {'NOME DA COLUNA':<25} | {'TIPO'}")
print("-" * 60)

# Variável para detectar mudança de ano visualmente
ultimo_ano = ""

for i, col in enumerate(colunas_reais):
    tipo = "METADADO"
    
    # Verifica se é coluna de dados (começa com número, ex: 13_ART_MOT)
    if col[0].isdigit() and '_' in col:
        ano_atual = col.split('_')[0]
        
        # Se mudou de ano, faz uma separação visual
        if ano_atual != ultimo_ano:
            print("-" * 60)
            ultimo_ano = ano_atual
            
        tipo = f"DADOS 20{ano_atual}"
    
    print(f"{i:<5} | {col:<25} | {tipo}")

print("="*60)

# --- VERIFICAÇÃO AUTOMÁTICA DE ORDEM CRONOLÓGICA ---
print("\n🔍 ANÁLISE DE CONSISTÊNCIA TEMPORAL:")

cols_dados = [c for c in colunas_reais if c[0].isdigit() and '_' in c]
anos_detectados = [c.split('_')[0] for c in cols_dados]

# Verifica se os anos estão crescendo
esta_ordenado = True
for k in range(len(anos_detectados) - 1):
    ano_a = int(anos_detectados[k])
    ano_b = int(anos_detectados[k+1])
    
    if ano_b < ano_a:
        esta_ordenado = False
        print(f"   ❌ ERRO DE ORDEM DETECTADO: Coluna {cols_dados[k+1]} veio depois de {cols_dados[k]}")
        break

if esta_ordenado:
    print("   ✅ APROVADO: As colunas estão em ordem cronológica perfeita (13 -> 25).")
else:
    print("   ⚠️ ATENÇÃO: As colunas NÃO estão ordenadas cronologicamente.")

# Verifica agrupamento por Fonte
print("\n🔍 ANÁLISE DE ORDEM (FONTE):")
# Esperado: Dentro do ano, ART vem antes de DER (ordem alfabética) ou DER antes de ART?
# No script de geração usamos: for fonte in fontes_presentes
# Isso depende da ordem que o Python leu. Vamos só listar o padrão do primeiro ano.

primeiro_ano = anos_detectados[0]
amostra_ano = [c for c in cols_dados if c.startswith(primeiro_ano)]
print(f"   Padrão de ordenação dentro de 20{primeiro_ano}:")
print(f"   {amostra_ano}")