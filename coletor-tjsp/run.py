#!/usr/bin/env python3
"""
Script de execução simplificado
"""
import sys
from src.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
