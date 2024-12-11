from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import google.cloud.bigquery as bigquery
import pandas as pd
import os
from datetime import date, timedelta
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class BigQueryToolInput(BaseModel):
    """Input schema for BigQueryTool."""
    csv_path: str = Field(..., description="Path to the local CSV file.")
    update: bool = Field(default=False, description="Whether to update the CSV incrementally.")

class BigQueryTool(BaseTool):
    name: str = "BigQueryTool"
    description: str = (
        "This tool manages data collection from BigQuery and updates a local CSV file to maintain a 30-day rolling window."
    )
    args_schema: Type[BaseModel] = BigQueryToolInput

    def _run(self, csv_path: str, update: bool = False) -> pd.DataFrame:
        client = bigquery.Client()
        
        try:
            if update and os.path.exists(csv_path):
                # Carregar o CSV existente
                existing_data = pd.read_csv(csv_path)
                last_date = pd.to_datetime(existing_data['entrada_data']).max().date()
                new_date = last_date + timedelta(days=1)

                # Coletar dados incrementais do BigQuery
                query = f"""
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
                    entrada_data = '{new_date}'
                    AND epi.motivo_atendimento IS NOT NULL
                    AND epi.desfecho_atendimento IS NOT NULL
                    AND cond.id IS NOT NULL
                """
                new_data = client.query(query).result().to_dataframe()

                # Atualizar o CSV
                if not new_data.empty:
                    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
                    # Remover registros fora da janela de 30 dias
                    cutoff_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
                    combined_data = combined_data[combined_data['entrada_data'] >= cutoff_date]
                    combined_data.to_csv(csv_path, index=False)
                    logging.info(f"CSV atualizado com dados do dia {new_date}.")
                else:
                    logging.info("Nenhum dado novo encontrado no BigQuery.")

                return combined_data

            else:
                # Primeira importação (últimos 30 dias)
                start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

                query = f"""
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
                    entrada_data BETWEEN '{start_date}' AND '{end_date}'
                    AND epi.motivo_atendimento IS NOT NULL
                    AND epi.desfecho_atendimento IS NOT NULL
                    AND cond.id IS NOT NULL
                """
                initial_data = client.query(query).result().to_dataframe()

                # Salvar no CSV
                initial_data.to_csv(csv_path, index=False)
                logging.info(f"CSV criado com dados de {start_date} a {end_date}.")
                return initial_data

        except Exception as e:
            logging.error(f"Erro ao executar a consulta no BigQuery: {str(e)}")
            return pd.DataFrame()
