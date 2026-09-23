import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

class BaseExtractor(ABC):
    """
    Classe abstrata que define o contrato para todos os extratores de dados de tráfego.
    """
    def __init__(self, file_path: Union[str, Path], ano_referencia: int):
        self.file_path = Path(file_path)
        self.ano_referencia = ano_referencia
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Ficheiro não encontrado: {self.file_path}")

    @abstractmethod
    def read_raw_data(self) -> pd.DataFrame:
        """Lê o ficheiro bruto (CSV, XLSX, etc) e retorna o DataFrame."""
        pass

    @abstractmethod
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza os nomes e tipos das colunas."""
        pass

    def process(self) -> pd.DataFrame:
        """
        Método orquestrador (Template Method Pattern).
        Executa o pipeline padrão de extração para qualquer fonte.
        """
        print(f"[{self.__class__.__name__}] A iniciar extração para o ano {self.ano_referencia}...")
        df_raw = self.read_raw_data()
        df_normalized = self.normalize_columns(df_raw)
        
        # Garante que o ano de referência fica registado na base de dados
        df_normalized['ano'] = self.ano_referencia
        
        print(f"[{self.__class__.__name__}] Extração concluída. {len(df_normalized)} registos processados.")
        return df_normalized


class DERExtractor(BaseExtractor):
    def read_raw_data(self) -> pd.DataFrame:
        # Pula as linhas de cabeçalho inúteis do Excel do DER
        return pd.read_excel(self.file_path, skiprows=3, engine='openpyxl')

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns={
            'Rodovia': 'rodovia_id',
            'Km': 'km_marco',
            'Volume_Total': 'vmd_total'
        })


class ARTESPExtractor(BaseExtractor):
    def __init__(self, file_path: Union[str, Path], ano_referencia: int):
        super().__init__(file_path, ano_referencia)
        # Otimização de memória para não sobrecarregar a RAM
        self.dtypes_otimizados = {
            'Rodovia': 'category',
            'Praca': 'category',
            'Sentido': 'category',
            'Volume_Leves': 'Int32',
            'Volume_Pesados': 'Int32',
            'Volume_Total': 'Int32'
        }

    def read_raw_data(self) -> pd.DataFrame:
        df = pd.read_excel(self.file_path, engine='openpyxl')
        for col, dtype in self.dtypes_otimizados.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        return df

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df_renamed = df.rename(columns={
            'Rodovia': 'rodovia_id',
            'Praca': 'praca_pedagio',
            'Km': 'km_marco',
            'Sentido': 'direcao',
            'Volume_Total': 'vmd_total',
            'Volume_Leves': 'vmd_leves',
            'Volume_Pesados': 'vmd_pesados'
        })
        
        if 'direcao' in df_renamed.columns:
            df_renamed['direcao'] = df_renamed['direcao'].str.strip().str.upper()
            
        if 'km_marco' in df_renamed.columns:
            df_renamed['km_marco'] = (
                df_renamed['km_marco']
                .astype(str)
                .str.replace(',', '.')
                .apply(pd.to_numeric, errors='coerce')
                .astype('float32') 
            )
        return df_renamed


class PNCTExtractor(BaseExtractor):
    def read_raw_data(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep=';', encoding='latin1')

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df_renamed = df.rename(columns={
            'rodovia': 'rodovia_id',
            'km': 'km_marco',
            'vmd': 'vmd_total'
        })
        # A vacina para o ano em que o DNIT não enviou a quilometragem
        if self.ano_referencia == 2021 and 'km_marco' in df_renamed.columns:
            df_renamed['km_marco'] = df_renamed['km_marco'].fillna(-1)
            
        return df_renamed