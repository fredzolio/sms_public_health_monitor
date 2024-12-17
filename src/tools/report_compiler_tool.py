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
    
    class Config:
        arbitrary_types_allowed = True

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
            missing_columns = [col for col in required_columns if col not in compiled_data.columns]
            if missing_columns:
                logging.error(f"As seguintes colunas estão ausentes: {missing_columns}")
                return f"Erro: Colunas ausentes nos dados fornecidos: {missing_columns}"

            # Agrupar os dados por condições (CIDs) e contar os eventos
            report_by_cid = compiled_data.groupby('condicoes')['cid_count'].sum().sort_values(ascending=False)

            # Localizações mais afetadas
            report_by_location = compiled_data.groupby(['latitude', 'longitude'])['cid_count'].sum().reset_index()
            report_by_location = report_by_location.sort_values(by='cid_count', ascending=False)

            # Condições mais frequentes por localização
            conditions_by_location = compiled_data.groupby(['latitude', 'longitude', 'condicoes'])['cid_count'].sum().reset_index()
            conditions_by_location = conditions_by_location.sort_values(by='cid_count', ascending=False)

            # Criar a mensagem do relatório
            report_message = "## Relatório Mensal de Surtos Detectados\n"
            report_message += "\n### Seção 1: Resumo por Condição (CID):\n"
            for condicao, count in report_by_cid.items():
                report_message += f"- {condicao}: {count} casos detectados\n"

            report_message += "\n### Seção 2: Localizações Mais Afetadas:\n"
            for _, row in report_by_location.iterrows():
                report_message += f"- Localização ({row['latitude']}, {row['longitude']}): {row['cid_count']} casos\n"

            report_message += "\n### Seção 3: Condições Mais Frequentes por Localização:\n"
            for _, row in conditions_by_location.iterrows():
                report_message += (
                    f"- Localização ({row['latitude']}, {row['longitude']}), Condição {row['condicoes']}: {row['cid_count']} casos\n"
                )

            # Informações adicionais do relatório
            total_cases = compiled_data['cid_count'].sum()
            total_outbreaks = len(compiled_data[compiled_data['outbreak'] == -1])
            report_message += f"\n### Seção 4: Estatísticas Gerais:\n"
            report_message += f"- Total de casos analisados: {total_cases}\n"
            report_message += f"- Total de surtos detectados: {total_outbreaks}\n"

            logging.info("Relatório mensal gerado com sucesso.")
            return report_message

        except Exception as e:
            # Capturar exceções inesperadas e logar o erro
            logging.error(f"Erro ao gerar o relatório mensal: {str(e)}")
            return "Erro ao gerar o relatório mensal. Verifique os logs para mais informações."
