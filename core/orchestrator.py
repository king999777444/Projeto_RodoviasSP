import os
import time
import concurrent.futures

# Injeção de Dependência de Hardware
try:
    import cudf as pd_backend
    GPU_AVAILABLE = True
except ImportError:
    import pandas as pd_backend
    GPU_AVAILABLE = False


class PipelineOrchestrator:
    """
    Orquestrador projetado para processar múltiplos extratores simultaneamente,
    utilizando todos os núcleos disponíveis do servidor Linux.
    """
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or max(1, os.cpu_count() - 1)
        self.extratores = []

    def adicionar_extrator(self, extrator):
        self.extratores.append(extrator)

    def _executar_job(self, extrator):
        """Método isolado executado por cada worker em paralelo."""
        # A extração inicial é feita em Pandas devido à leitura de Excel
        df_pandas = extrator.process()
        
        # Se houver GPU, converte imediatamente a tabela final daquela thread para a VRAM
        if GPU_AVAILABLE:
            return pd_backend.DataFrame(df_pandas)
        return df_pandas

    def rodar_pipeline(self):
        """Executa todos os extratores em paralelo e consolida os resultados."""
        print(f"\n[ORQUESTRADOR] A iniciar processamento paralelo com {self.max_workers} workers.")
        start_time = time.time()
        resultados = []

        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_extractor = {
                executor.submit(self._executar_job, ext): ext for ext in self.extratores
            }

            for future in concurrent.futures.as_completed(future_to_extractor):
                nome_extrator = future_to_extractor[future].__class__.__name__
                try:
                    df_result = future.result()
                    resultados.append(df_result)
                    print(f"✅ [{nome_extrator}] Concluído com sucesso: {len(df_result)} linhas processadas.")
                except Exception as e:
                    print(f"❌ [{nome_extrator}] Falha crítica durante a execução: {e}")

        if resultados:
            print("\n[ORQUESTRADOR] A concatenar DataFrames consolidados...")
            df_final = pd_backend.concat(resultados, ignore_index=True)
            
            end_time = time.time()
            print(f"[ORQUESTRADOR] Pipeline finalizado em {end_time - start_time:.2f} segundos!")
            print(f"📊 Total de registos na base unificada: {len(df_final)}")
            return df_final
        else:
            print("[ORQUESTRADOR] Nenhum dado foi retornado pelos extratores.")
            return None