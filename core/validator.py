import pandas as pd
import numpy as np

class AuditorQualidade:
    """
    Sistema de QA (Quality Assurance) e Self-Healing.
    Verifica anomalias clássicas de tráfego e aplica autocorreções documentadas.
    """
    def __init__(self):
        # Configurações de limites lógicos para São Paulo
        self.MAX_KM_SP = 800.0  # Nenhuma rodovia em SP passa do KM 800
        self.MIN_KM = 0.0
        self.logs_correcao = [] # Para gerar um relatório do que foi alterado automaticamente

    def _log(self, mensagem: str):
        """Registra a ação tomada pela inteligência do auditor."""
        self.logs_correcao.append(mensagem)
        # Pode ser substituído por um logger.info() para salvar em arquivo txt

    def corrigir_kms_absurdos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corrige erros de digitação onde o KM é negativo ou absurdo."""
        col = 'km_marco'
        if col in df.columns:
            # Erro 1: KM Negativo (ex: -1, que injetamos como flag no PNCT 2021)
            # Autocorreção: Converte para NaN (nulo) para ser tratado ou descartado com segurança
            qtd_negativos = (df[col] < self.MIN_KM).sum()
            if qtd_negativos > 0:
                df.loc[df[col] < self.MIN_KM, col] = np.nan
                self._log(f"Corrigidos {qtd_negativos} registros com KM negativo (convertidos para nulo).")

            # Erro 2: Erro de vírgula do digitador (ex: KM 15000 em vez de 150.00)
            qtd_absurdos = (df[col] > self.MAX_KM_SP).sum()
            if qtd_absurdos > 0:
                # Tenta dividir por 100 se for maior que o limite
                df.loc[df[col] > self.MAX_KM_SP, col] = df[col] / 100.0
                self._log(f"Autocorreção de escala decimal em {qtd_absurdos} marcos quilométricos absurdos.")
        return df

    def remover_duplicatas_temporais(self, df: pd.DataFrame) -> pd.DataFrame:
        """Garante que não haja duas contagens para a mesma rodovia, mesmo km, no mesmo ano."""
        # Se você encontrar a mesma rodovia, no mesmo KM, no mesmo ano e sentido, é lixo.
        chaves_unicas = ['ano', 'rodovia_id', 'km_marco', 'direcao']
        
        # Só verifica se todas as colunas existem
        if all(c in df.columns for c in chaves_unicas):
            antes = len(df)
            df = df.drop_duplicates(subset=chaves_unicas, keep='last')
            depois = len(df)
            if antes != depois:
                self._log(f"Removidas {antes - depois} contagens duplicadas no mesmo ponto.")
        return df

    def padronizar_direcoes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Autocorrige erros de digitação como 'N', 'norte', 'Nort' para 'NORTE'."""
        if 'direcao' in df.columns:
            df['direcao'] = df['direcao'].astype(str).str.upper().str.strip()
            
            mapa_correcao = {
                'N': 'NORTE', 'S': 'SUL', 'L': 'LESTE', 'O': 'OESTE', 'W': 'OESTE',
                'N/D': 'AMBOS', 'NAN': 'AMBOS', '': 'AMBOS'
            }
            df['direcao'] = df['direcao'].replace(mapa_correcao)
        return df

    def auditar_e_curar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Orquestrador do QA. Aplica todas as vacinas em sequência."""
        print("[AUDITOR] Iniciando varredura e autocorreção do dataset...")
        
        df = self.remover_duplicatas_temporais(df)
        df = self.corrigir_kms_absurdos(df)
        df = self.padronizar_direcoes(df)
        
        # Elimina dados cujo KM ficou inválido mesmo após tentar corrigir
        linhas_validas = len(df)
        df = df.dropna(subset=['km_marco'])
        removidas = linhas_validas - len(df)
        if removidas > 0:
            self._log(f"Descartadas {removidas} linhas irrecuperáveis por falta de KM espacial.")

        print(f"[AUDITOR] Varredura concluída. Foram feitas {len(self.logs_correcao)} intervenções de autocorreção.")
        return df