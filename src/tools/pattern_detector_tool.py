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
    """Input schema for PatternDetector."""
    csv_path: str = Field(default="data/health_data.csv", description="Path to the CSV file containing health records.")
    contamination: float = Field(default=0.01, description="Contamination level for anomaly detection.")
    n_estimators: int = Field(default=100, description="Number of estimators for the Isolation Forest.")

class PatternDetector(BaseTool):
    name: str = "PatternDetector"
    description: str = (
        "This tool uses machine learning algorithms to detect patterns or anomalies in health records from a CSV file."
    )
    args_schema: Type[BaseModel] = PatternDetectorInput

    def _run(self, csv_path: str = "data/health_data.csv", contamination: float = 0.01, n_estimators: int = 100) -> pd.DataFrame:
        """
        Detect patterns and anomalies in health records from a CSV file.

        Args:
            csv_path (str): Path to the CSV file containing health records.
            contamination (float): Contamination level for anomaly detection.
            n_estimators (int): Number of estimators for the Isolation Forest.

        Returns:
            pd.DataFrame: Aggregated DataFrame of detected outbreaks.
        """
        try:
            # Verificar se o arquivo CSV existe
            if not os.path.exists(csv_path):
                logging.error(f"O arquivo CSV {csv_path} não foi encontrado.")
                return pd.DataFrame()

            # Carregar o CSV em um DataFrame
            logging.info(f"Carregando dados do arquivo CSV: {csv_path}")
            dataframe = pd.read_csv(csv_path)

            if dataframe.empty:
                logging.warning("O CSV fornecido está vazio. Não há dados para analisar.")
                return pd.DataFrame()

            # Verificar se as colunas necessárias estão presentes
            required_columns = ['condicao_id', 'motivo_atendimento', 'estabelecimento_id']
            missing_columns = [col for col in required_columns if col not in dataframe.columns]
            if missing_columns:
                logging.error(f"As seguintes colunas estão ausentes no DataFrame: {missing_columns}")
                return pd.DataFrame()

            # Contar o número de CIDs por episódio de atendimento
            dataframe['cid_count'] = dataframe['condicao_id'].apply(lambda x: len(x) if isinstance(x, list) else 0)

            # Filtrar registros inválidos
            dataframe = dataframe.dropna(subset=['cid_count', 'motivo_atendimento', 'estabelecimento_id'])

            # Preparar os dados para o modelo
            features = ['cid_count']
            X = dataframe[features].values

            # Treinar o Isolation Forest para detectar anomalias
            model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=42)
            dataframe['outbreak'] = model.fit_predict(X)

            # Filtrar surtos detectados (anomalias)
            outbreaks = dataframe[dataframe['outbreak'] == -1]
            logging.info(f"{len(outbreaks)} possíveis surtos detectados nos dados fornecidos.")

            # Agregar dados para análise adicional
            aggregated = outbreaks.groupby(['condicao_id', 'estabelecimento_id']).agg({
                'cid_count': 'sum',
                'motivo_atendimento': 'count'
            }).reset_index()
            aggregated.rename(columns={'cid_count': 'total_cid_count', 'motivo_atendimento': 'total_cases'}, inplace=True)
            logging.info("Análise adicional de surtos concluída.")

            return aggregated

        except Exception as e:
            logging.error(f"Erro ao analisar os dados com o PatternDetector: {str(e)}")
            return pd.DataFrame()
