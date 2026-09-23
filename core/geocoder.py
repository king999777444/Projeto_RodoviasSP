import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import Point

class GeocoderRodoviario:
    """
    Classe responsável pelo Referenciamento Linear.
    Transforma marcos quilométricos em coordenadas geográficas (Lat/Long) 
    sobre a geometria oficial das rodovias do DER-SP.
    """
    def __init__(self, caminho_shapefile: str):
        print("[GEOCODER] Carregando malha rodoviária na memória...")
        self.malha_gdf = gpd.read_file(Path(caminho_shapefile))
        
        # Otimização crucial: Garantir que o Shapefile esteja projetado em UTM (metros)
        # SIRGAS 2000 / UTM zone 23S (EPSG:31983) é o padrão para São Paulo.
        if self.malha_gdf.crs != "EPSG:31983":
            self.malha_gdf = self.malha_gdf.to_crs("EPSG:31983")

    def _interpolar_ponto(self, rodovia_id: str, km: float) -> Point:
        """Encontra a coordenada exata interpolando o KM na geometria da via."""
        try:
            # Filtra a geometria da rodovia específica
            via = self.malha_gdf[self.malha_gdf['codigo'] == rodovia_id]
            if via.empty:
                return None
            
            linha = via.geometry.iloc[0]
            # O Shapely entende a distância na linha (multiplicamos por 1000 para converter KM em Metros)
            ponto = linha.interpolate(km * 1000) 
            return ponto
        except Exception:
            return None

    def processar_coordenadas(self, df_trafego: pd.DataFrame) -> gpd.GeoDataFrame:
        """Gera o GeoDataFrame final com os pontos exatos de tráfego."""
        print("[GEOCODER] Iniciando referenciamento linear...")
        
        # Se for um cuDF (GPU), trazemos para a CPU (Pandas) momentaneamente, 
        # pois bibliotecas espaciais complexas rodam melhor no GeoPandas padrão.
        if hasattr(df_trafego, 'to_pandas'):
            df_trafego = df_trafego.to_pandas()

        # Aplica a função de interpolação vetorizada
        df_trafego['geometry'] = df_trafego.apply(
            lambda row: self._interpolar_ponto(row['rodovia_id'], row['km_marco']), axis=1
        )
        
        # Remove os pontos que não foram encontrados (vazios)
        df_limpo = df_trafego.dropna(subset=['geometry'])
        
        # Converte de volta para um GeoDataFrame (agora é um mapa!)
        gdf_final = gpd.GeoDataFrame(df_limpo, geometry='geometry', crs="EPSG:31983")
        
        print(f"[GEOCODER] Sucesso: {len(gdf_final)} pontos georreferenciados.")
        return gdf_final