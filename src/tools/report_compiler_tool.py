from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import pandas as pd
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class ReportCompilerInput(BaseModel):
    """Input schema for ReportCompilerTool."""
    dataframes_list: List[pd.DataFrame] = Field(..., description="List of DataFrames to compile into a monthly report.")

class ReportCompilerTool(BaseTool):
    name: str = "ReportCompilerTool"
    description: str = (
        "This tool compiles multiple dataframes into a comprehensive monthly report for health authorities. "
        "It summarizes the number of detected outbreaks and provides detailed insights for each health condition."
    )
    args_schema: Type[BaseModel] = ReportCompilerInput

    def _run(self, dataframes_list: List[pd.DataFrame]) -> str:
        try:
            # Verificar se a lista de DataFrames está vazia
            if not dataframes_list:
                logging.warning("Nenhum DataFrame foi fornecido para a compilação do relatório.")
                return "Relatório não pôde ser gerado: Nenhum dado foi fornecido."

            # Verificar se todos os elementos na lista são DataFrames
            for df in dataframes_list:
                if not isinstance(df, pd.DataFrame):
                    logging.error("Um ou mais elementos na lista não são DataFrames. Não é possível gerar o relatório.")
                    return "Erro: Lista contém elementos não DataFrames."

            # Concatenar os DataFrames para compilar os dados em um único DataFrame
            compiled_data = pd.concat(dataframes_list, axis=0, ignore_index=True)
            if compiled_data.empty:
                logging.warning("Os DataFrames fornecidos não contêm dados. Relatório vazio será gerado.")
                return "Relatório não pôde ser gerado: Os DataFrames fornecidos estão vazios."

            # Verificar colunas necessárias
            required_columns = ['condicoes', 'cid_count', 'estabelecimento_id', 'latitude', 'longitude']
            for col in required_columns:
                if col not in compiled_data.columns:
                    logging.error(f"Coluna '{col}' não encontrada no DataFrame compilado.")
                    return f"Erro: Coluna '{col}' não encontrada nos dados fornecidos."

            # Agrupar os dados por condições (CIDs) e contar os eventos
            report_by_cid = compiled_data.groupby('condicoes')['cid_count'].sum()

            # Localizações mais afetadas
            report_by_location = compiled_data.groupby(['latitude', 'longitude'])['cid_count'].sum().reset_index()

            # Criar a mensagem do relatório
            report_message = "Relatório Mensal de Surtos Detectados\n"
            report_message += "\nSeção 1: Resumo por Condição (CID):\n"
            for condicao, count in report_by_cid.items():
                report_message += f"- {condicao}: {count} casos detectados\n"

            report_message += "\nSeção 2: Localizações Mais Afetadas:\n"
            for _, row in report_by_location.iterrows():
                report_message += f"- Localização ({row['latitude']}, {row['longitude']}): {row['cid_count']} casos\n"

            # Informações adicionais do relatório
            total_outbreaks = len(compiled_data[compiled_data['outbreak'] == -1])
            report_message += f"\nSeção 3: Total de surtos detectados durante o mês: {total_outbreaks}\n"

            logging.info("Relatório mensal gerado com sucesso.")
            return report_message

        except Exception as e:
            # Capturar exceções inesperadas e logar o erro
            logging.error(f"Erro ao gerar o relatório mensal: {str(e)}")
            return "Erro ao gerar o relatório mensal. Verifique os logs para mais informações."
