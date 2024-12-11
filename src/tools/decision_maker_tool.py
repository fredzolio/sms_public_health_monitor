from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

class DecisionMakerInput(BaseModel):
    """Input schema for DecisionMakerTool."""
    outbreaks: pd.DataFrame = Field(..., description="DataFrame containing the detected outbreaks information.")
    threshold: int = Field(default=5, description="Threshold for the number of outbreaks to trigger a notification.")

class DecisionMakerTool(BaseTool):
    name: str = "DecisionMakerTool"
    description: str = (
        "This tool evaluates the detected outbreaks and decides whether notifications should be sent "
        "to health authorities or citizens based on thresholds and trends."
    )
    args_schema: Type[BaseModel] = DecisionMakerInput

    def _run(self, outbreaks: pd.DataFrame, threshold: int = 5) -> dict:
        """
        Evaluate detected outbreaks and decide whether to notify health authorities or citizens.

        Returns:
            dict: A dictionary containing the decision, reasons, and strategic recommendations.
        """
        # Verificar se o DataFrame fornecido está vazio
        if outbreaks.empty:
            logging.info("Nenhum surto detectado. Nenhuma ação necessária.")
            return {
                "notify": False,
                "reason": "Nenhum surto detectado.",
                "recommendations": []
            }

        try:
            # Lógica de decisão
            num_outbreaks = len(outbreaks)
            logging.info(f"{num_outbreaks} surtos detectados.")

            # Identificar as localizações mais afetadas
            location_summary = (
                outbreaks.groupby(["latitude", "longitude"])
                .size()
                .reset_index(name="count")
                .sort_values(by="count", ascending=False)
            )
            top_locations = location_summary.head(5).to_dict(orient="records")

            # Identificar condições mais frequentes
            condition_summary = (
                outbreaks.groupby("condicao_id")
                .size()
                .reset_index(name="count")
                .sort_values(by="count", ascending=False)
            )
            top_conditions = condition_summary.head(5).to_dict(orient="records")

            recommendations = [
                "Monitorar as localizações mais afetadas.",
                "Realizar campanhas de prevenção para as condições mais frequentes.",
                "Priorizar recursos para áreas com maior número de surtos."
            ]

            if num_outbreaks > threshold:
                logging.info(f"Decisão tomada: Notificar a Secretaria de Saúde.")
                reason = (
                    f"Notificação necessária: {num_outbreaks} surtos detectados, acima do limite de {threshold}."
                )
                return {
                    "notify": True,
                    "reason": reason,
                    "top_locations": top_locations,
                    "top_conditions": top_conditions,
                    "recommendations": recommendations,
                }

            # Caso esteja abaixo do limite
            logging.info(f"{num_outbreaks} surtos detectados, mas abaixo do limite de {threshold}.")
            return {
                "notify": False,
                "reason": f"{num_outbreaks} surtos detectados, abaixo do limite.",
                "top_locations": top_locations,
                "top_conditions": top_conditions,
                "recommendations": recommendations,
            }

        except Exception as e:
            # Capturar qualquer exceção inesperada e logar o erro
            logging.error(f"Erro ao processar a decisão: {str(e)}")
            return {
                "notify": False,
                "reason": f"Erro ao processar a decisão: {str(e)}",
                "recommendations": []
            }
