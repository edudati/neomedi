import sys
from pathlib import Path

# Adiciona a pasta raiz ao path para permitir imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from neomediapi.infra.db.session import create_all_tables

if __name__ == "__main__":
    create_all_tables()
    print("Tables created successfully.")
