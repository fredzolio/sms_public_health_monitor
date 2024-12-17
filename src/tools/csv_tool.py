from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import os
from datetime import date, timedelta
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class CSVToolInput(BaseModel):
    """Input schema for CSVTool."""
    csv_path: str = Field(default="data/health_data.csv", description="Path to the local CSV file.")

class CSVTool(BaseTool):
    name: str = "CSVTool"
    description: str = (
        "This tool manages data from a local CSV file and loads it into memory for analysis."
    )
    args_schema: Type[BaseModel] = CSVToolInput

    def _run(self, csv_path: str = "data/health_data.csv") -> pd.DataFrame:
        try:
            # Verificar se o arquivo CSV existe
            if not os.path.exists(csv_path):
                logging.error(f"O arquivo CSV {csv_path} não foi encontrado.")
                return pd.DataFrame()

            # Carregar os dados do CSV
            data = pd.read_csv(csv_path)
            logging.info(f"Arquivo CSV {csv_path} carregado com {len(data)} registros.")

            # Garantir que a coluna 'entrada_data' está no formato de data
            if 'entrada_data' in data.columns:
                data['entrada_data'] = pd.to_datetime(data['entrada_data'], errors='coerce')
                # Remover valores inválidos
                data = data.dropna(subset=['entrada_data'])
                logging.info(f"{len(data)} registros possuem datas válidas na coluna 'entrada_data'.")
            else:
                logging.error("A coluna 'entrada_data' não está presente no CSV.")
                return pd.DataFrame()

            # Retornar todos os dados sem filtrar
            return data

        except Exception as e:
            logging.error(f"Erro ao processar o CSV: {str(e)}")
            return pd.DataFrame()
