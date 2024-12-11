from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import google.cloud.bigquery as bigquery
import pandas as pd
from datetime import date, timedelta
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class BigQueryToolInput(BaseModel):
    """Input schema for BigQueryTool."""
    query_type: str = Field(..., description="Type of query to run: 'custom' or 'daily_collect'")
    custom_query: str = Field(default=None, description="Custom SQL query to run on BigQuery.")

class BigQueryTool(BaseTool):
    name: str = "BigQueryTool"
    description: str = (
        "This tool allows the agent to query data from the Google BigQuery data lake. "
        "It can collect data for a specific period or execute custom queries."
    )
    args_schema: Type[BaseModel] = BigQueryToolInput

    def _run(self, query_type: str, custom_query: str = None) -> pd.DataFrame:
        client = bigquery.Client()
        try:
            if query_type == 'daily_collect':
                # Define o intervalo de datas dos últimos 30 dias
                start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

                # Base da consulta SQL
                base_query = f"""
                SELECT 
                    epi.id_episodio,
                    epi.subtipo,
                    epi.entrada_data,
                    epi.motivo_atendimento,
                    epi.desfecho_atendimento,
                    cond.id AS condicao_id,
                    cond.resumo AS condicao_resumo,
                    med.nome AS medicamento_administrado,
                    loc.id_cnes AS estabelecimento_id,
                    loc.endereco_latitude AS latitude,
                    loc.endereco_longitude AS longitude
                FROM 
                    `rj-sms.saude_historico_clinico.episodio_assistencial` AS epi
                LEFT JOIN 
                    UNNEST(epi.condicoes) AS cond
                LEFT JOIN 
                    UNNEST(epi.medicamentos_administrados) AS med
                JOIN 
                    `rj-sms.saude_dados_mestres.estabelecimento` AS loc
                ON 
                    epi.estabelecimento.id_cnes = loc.id_cnes
                WHERE 
                    epi.entrada_data BETWEEN '{start_date}' AND '{end_date}'
                    AND epi.motivo_atendimento IS NOT NULL
                    AND epi.desfecho_atendimento IS NOT NULL
                    AND cond.id IS NOT NULL
                """

                # Configuração de paginação
                batch_size = 100000
                offset = 0
                dfs = []

                # Paginação da consulta
                while True:
                    paginated_query = f"{base_query} LIMIT {batch_size} OFFSET {offset}"
                    logging.info(f"Executando consulta com OFFSET {offset}...")
                    job = client.query(paginated_query)
                    batch_df = job.result().to_dataframe()
                    
                    if batch_df.empty:
                        logging.info("Todas as páginas foram processadas.")
                        break
                    
                    dfs.append(batch_df)
                    offset += batch_size

                # Combinar todos os DataFrames em um único
                final_df = pd.concat(dfs, ignore_index=True)
                logging.info(f"Coletados {len(final_df)} registros do BigQuery entre {start_date} e {end_date}.")
                return final_df

            elif query_type == 'custom' and custom_query is not None:
                logging.info("Executando consulta customizada...")
                job = client.query(custom_query)
                df = job.result().to_dataframe()
                logging.info("Consulta customizada executada com sucesso.")
                return df

            else:
                raise ValueError("Invalid query type or missing custom query.")

        except Exception as e:
            logging.error(f"Erro ao executar a consulta no BigQuery: {str(e)}")
            return pd.DataFrame()
