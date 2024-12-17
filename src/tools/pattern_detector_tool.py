# Importações
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
import pandas as pd
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class PatternDetectorInput(BaseModel):
    csv_path: str = Field(default="data/health_data.csv", description="Path to the CSV file containing health records.")
    contamination: float = Field(default=0.01, description="Contamination level for anomaly detection.")
    n_estimators: int = Field(default=100, description="Number of estimators for the Isolation Forest.")

class PatternDetector(BaseTool):
    name: str = "PatternDetector"
    description: str = "Detect patterns or anomalies in health records using Isolation Forest."
    args_schema: Type[BaseModel] = PatternDetectorInput

    def _run(self, csv_path: str = "data/health_data.csv", contamination: float = 0.01, n_estimators: int = 100) -> pd.DataFrame:
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(csv_path):
                logging.error(f"O arquivo CSV {csv_path} não foi encontrado.")
                return pd.DataFrame()

            # Carregar os dados
            logging.info(f"Carregando dados do arquivo CSV: {csv_path}")
            dataframe = pd.read_csv(csv_path)

            # Verificar colunas
            required_columns = ['condicao_id', 'motivo_atendimento', 'estabelecimento_id', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in dataframe.columns]
            if missing_columns:
                logging.error(f"As seguintes colunas estão ausentes: {missing_columns}")
                return pd.DataFrame()

            # Tratar valores nulos
            dataframe = dataframe.dropna(subset=required_columns)

            # Features melhoradas para o modelo
            dataframe['condicao_count'] = dataframe.groupby('condicao_id')['condicao_id'].transform('count')
            features = ['condicao_count', 'latitude', 'longitude']

            # Treinar Isolation Forest
            X = dataframe[features].values
            model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=42)
            dataframe['outbreak'] = model.fit_predict(X)

            # Filtrar surtos
            outbreaks = dataframe[dataframe['outbreak'] == -1]
            logging.info(f"{len(outbreaks)} possíveis surtos detectados.")

            # Agregar os dados
            aggregated = outbreaks.groupby(['condicao_id', 'estabelecimento_id']).agg({
                'condicao_count': 'sum',
                'motivo_atendimento': 'count'
            }).reset_index()
            aggregated.rename(columns={'condicao_count': 'total_cid_count', 'motivo_atendimento': 'total_cases'}, inplace=True)

            return aggregated

        except Exception as e:
            logging.error(f"Erro ao analisar os dados: {e}")
            return pd.DataFrame()
