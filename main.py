import time
from pathlib import Path

# Nossos módulos
from utils.hardware import checar_aceleracao, get_max_workers
from core.extractor import DERExtractor, ARTESPExtractor, PNCTExtractor
from core.orchestrator import PipelineOrchestrator
from core.validator import AuditorQualidade
from core.geocoder import GeocoderRodoviario

def main():
    print("="*50)
    print(" PIPELINE GEOESPACIAL DE TRÁFEGO SP (POO) ")
    print("="*50)
    
    # 1. Configuração de Hardware
    gpu_ativa = checar_aceleracao()
    workers = get_max_workers()
    
    # 2. Configura os caminhos físicos
    caminho_der = Path("data/raw/der_2024.xlsx")
    caminho_artesp = Path("data/raw/artesp_2024.xlsx")
    caminho_pnct = Path("data/raw/pnct_2021.csv")
    caminho_malha = Path("data/geometry/malha_sp_oficial.shp")
    
    # ---- FASE 1: INGESTÃO E PARALELISMO ----
    orquestrador = PipelineOrchestrator(max_workers=workers)
    
    # Fila de trabalhos
    orquestrador.adicionar_extrator(DERExtractor(caminho_der, 2024))
    orquestrador.adicionar_extrator(ARTESPExtractor(caminho_artesp, 2024))
    orquestrador.adicionar_extrator(PNCTExtractor(caminho_pnct, 2021))
    
    # Executa tudo!
    df_bruto = orquestrador.rodar_pipeline()
    
    if df_bruto is None or df_bruto.empty:
        print(" Falha na extração. O Pipeline foi abortado.")
        return

    auditor = AuditorQualidade()
    df_limpo = auditor.auditar_e_curar(df_bruto)

    if caminho_malha.exists():
        geocoder = GeocoderRodoviario(caminho_malha)
        gdf_final = geocoder.processar_coordenadas(df_limpo)
        
        Path("data/processed").mkdir(exist_ok=True)
        
        # Salva em Parquet para leitura rápida em Machine Learning (tabela leve)
        output_parquet = "data/processed/base_consolidada.parquet"
        gdf_final.drop(columns='geometry').to_parquet(output_parquet, index=False)
        print(f"💾 Tabela otimizada salva em: {output_parquet}")
        
        # Salva em GeoPackage (O "Novo Shapefile", mais moderno, para o QGIS)
        output_gpkg = "data/processed/mapa_trafego.gpkg"
        gdf_final.to_file(output_gpkg, driver="GPKG")
        print(f" Mapa geoespacial salvo em: {output_gpkg}")
        
    else:
        print(f" Malha rodoviária não encontrada em {caminho_malha}. Geocodificação ignorada.")
    
    print("\n PIPELINE FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    main()