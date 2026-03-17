import pandas as pd
import os

arquivo = os.path.join("dados_artesp", "contagem_diaria_2025.csv")

if not os.path.exists(arquivo):
    print(f"ERRO: Não achei o arquivo em: {arquivo}")
    print("Verifique se o nome da pasta é 'dados_artesp' mesmo.")
else:
    print(f"--> Analisando: {os.path.basename(arquivo)}")
    
    print("\n[1] CONTEÚDO BRUTO (Primeiras 3 linhas):")
    with open(arquivo, 'r', encoding='latin1') as f:
        for i in range(3):
            print(f.readline().strip())
            
    print("\n[2] TENTATIVA DE LEITURA (Pandas):")
    try:
        df = pd.read_csv(arquivo, sep=';', encoding='latin1', nrows=2)
        print("Separador detectado: Ponto-e-vírgula (;)")
        print("COLUNAS:", list(df.columns))
    except:
        try:
            df = pd.read_csv(arquivo, sep=',', encoding='latin1', nrows=2)
            print("Separador detectado: Vírgula (,)")
            print("COLUNAS:", list(df.columns))
        except Exception as e:
            print(f"Erro ao ler colunas: {e}")