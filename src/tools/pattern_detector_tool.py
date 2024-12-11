from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
import pandas as pd
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class PatternDetectorInput(BaseModel):
    """Input schema for PatternDetector."""
    dataframe: pd.DataFrame = Field(..., description="DataFrame with health records to analyze.")
    contamination: float = Field(default=0.01, description="Contamination level for anomaly detection.")
    n_estimators: int = Field(default=100, description="Number of estimators for the Isolation Forest.")

class PatternDetector(BaseTool):
    name: str = "PatternDetector"
    description: str = (
        "This tool uses machine learning algorithms to detect patterns or anomalies in health records over a period of time."
    )
    args_schema: Type[BaseModel] = PatternDetectorInput

    def _run(self, dataframe: pd.DataFrame, contamination: float = 0.01, n_estimators: int = 100) -> pd.DataFrame:
        """
        Detect patterns and anomalies in health records.

        Args:
            dataframe (pd.DataFrame): DataFrame with health records.
            contamination (float): Contamination level for anomaly detection.
            n_estimators (int): Number of estimators for the Isolation Forest.

        Returns:
            pd.DataFrame: Aggregated DataFrame of detected outbreaks.
        """
        if dataframe.empty:
            logging.warning("O DataFrame fornecido está vazio. Não há dados para analisar.")
            return pd.DataFrame()

        try:
            # Verificar se as colunas necessárias estão presentes no DataFrame
            required_columns = ['condicoes', 'motivo_atendimento', 'estabelecimento_id']
            missing_columns = [col for col in required_columns if col not in dataframe.columns]
            if missing_columns:
                logging.error(f"As seguintes colunas estão ausentes no DataFrame: {missing_columns}")
                return pd.DataFrame()

            # Contar o número de CIDs por episódio de atendimento
            dataframe['cid_count'] = dataframe['condicoes'].apply(lambda x: len(x) if isinstance(x, list) else 0)

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
            logging.info(f"{len(outbreaks)} possíveis surtos detectados nos últimos 30 dias.")

            # Agregar dados para análise adicional
            aggregated = outbreaks.groupby(['condicoes', 'estabelecimento_id']).agg({
                'cid_count': 'sum',
                'motivo_atendimento': 'count'
            }).reset_index()
            aggregated.rename(columns={'cid_count': 'total_cid_count', 'motivo_atendimento': 'total_cases'}, inplace=True)
            logging.info("Análise adicional de surtos concluída.")

            return aggregated

        except Exception as e:
            logging.error(f"Erro ao analisar os dados com o PatternDetector: {str(e)}")
            return pd.DataFrame()
