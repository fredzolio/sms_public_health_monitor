from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class PatternDetectorInput(BaseModel):
    csv_path: str = Field(default="data/health_data.csv", description="Path to the CSV file containing health records.")
    contamination: float = Field(default=0.01, description="Contamination level for anomaly detection.")
    n_estimators: int = Field(default=100, description="Number of estimators for the Isolation Forest.")
    random_state: int = Field(default=42, description="Random state for reproducibility.")

class PatternDetector(BaseTool):
    name: str = "PatternDetector"
    description: str = "Detect patterns or anomalies in health records using Isolation Forest."
    args_schema: Type[BaseModel] = PatternDetectorInput

    def _run(self, 
            csv_path: str = "data/health_data.csv", 
            contamination: float = 0.01, 
            n_estimators: int = 100,
            random_state: int = 42) -> pd.DataFrame:
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(csv_path):
                logging.error(f"O arquivo CSV {csv_path} não foi encontrado.")
                return pd.DataFrame()

            # Carregar os dados
            logging.info(f"Carregando dados do arquivo CSV: {csv_path}")
            dataframe = pd.read_csv(csv_path)

            # Verificar colunas obrigatórias
            required_columns = ['condicao_id', 'motivo_atendimento', 'estabelecimento_id', 
                                'latitude', 'longitude', 'entrada_data']
            missing_columns = [col for col in required_columns if col not in dataframe.columns]
            if missing_columns:
                logging.error(f"As seguintes colunas estão ausentes: {missing_columns}")
                return pd.DataFrame()

            # Tratar valores nulos
            dataframe = dataframe.dropna(subset=required_columns)
            logging.info("Valores nulos nas colunas obrigatórias foram removidos.")

            # Validar valores numéricos
            for col in ['latitude', 'longitude']:
                if not pd.api.types.is_numeric_dtype(dataframe[col]):
                    logging.error(f"A coluna {col} contém valores não numéricos.")
                    return pd.DataFrame()

            # Adicionar features temporais
            dataframe['entrada_data'] = pd.to_datetime(dataframe['entrada_data'], errors='coerce')
            dataframe = dataframe.dropna(subset=['entrada_data'])
            dataframe['dia_da_semana'] = dataframe['entrada_data'].dt.dayofweek
            dataframe['semana_do_ano'] = dataframe['entrada_data'].dt.isocalendar().week

            # Contar frequência de condicao_id
            condicao_count = dataframe['condicao_id'].value_counts().to_dict()
            dataframe['condicao_count'] = dataframe['condicao_id'].map(condicao_count)

            # Seleção de features
            features = ['condicao_count', 'latitude', 'longitude', 'dia_da_semana', 'semana_do_ano']
            X = dataframe[features].values

            # Normalização das features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Treinar Isolation Forest
            logging.info("Treinando o modelo Isolation Forest...")
            model = IsolationForest(
                n_estimators=n_estimators, 
                contamination=contamination, 
                random_state=random_state
            )
            dataframe['outbreak'] = model.fit_predict(X_scaled)

            # Filtrar surtos detectados
            outbreaks = dataframe[dataframe['outbreak'] == -1]
            logging.info(f"{len(outbreaks)} possíveis surtos detectados.")

            # Agregar os dados
            aggregated = outbreaks.groupby(['condicao_id', 'estabelecimento_id']).agg({
                'condicao_count': 'sum',
                'motivo_atendimento': 'count'
            }).reset_index()
            aggregated.rename(columns={'condicao_count': 'total_cid_count', 'motivo_atendimento': 'total_cases'}, inplace=True)

            logging.info("Análise de surtos concluída com sucesso.")
            return aggregated

        except Exception as e:
            logging.error(f"Erro ao analisar os dados: {e}")
            return pd.DataFrame()