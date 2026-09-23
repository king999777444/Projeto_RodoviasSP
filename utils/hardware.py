import os
import multiprocessing

def checar_aceleracao():
    """Detecta a presença de GPU NVIDIA e ajusta o ambiente para Multiprocessing."""
    print("--- Verificação de Hardware (Servidor IME) ---")
    
    try:
        import cudf
        print(" NVIDIA RAPIDS (cuDF) Encontrado! Aceleração GPU Ativa.")
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            pass
        return True
    except ImportError:
        print("⚠️ cuDF não encontrado. Rodando em modo CPU (Pandas).")
        return False

def get_max_workers() -> int:
    """Retorna o número ideal de threads baseando-se no hardware."""
    cores = os.cpu_count() or 2
    return max(1, cores - 2)