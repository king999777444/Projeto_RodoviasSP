
from .logger import configurar_logger
from .hardware import checar_aceleracao, get_max_workers

__all__ = [
    "configurar_logger",
    "checar_aceleracao",
    "get_max_workers"
]