from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json
import os
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)

# Schema de entrada para a Tool
class CIDLookupInput(BaseModel):
    cid_code: str = Field(..., description="Código CID a ser consultado (formato: A00.0). Exemplo de formatação: se for um CID A975, informe A97.5, se for CID A10, informe A10.0")

class CIDLookupTool(BaseTool):
    name: str = "CIDLookupTool"
    description: str = "Consulta a descrição de um CID em um arquivo cids.json."
    args_schema: Type[BaseModel] = CIDLookupInput

    def _run(self, cid_code: str) -> dict:
        """
        Consulta a descrição de um CID no arquivo cids.json.

        Args:
            cid_code (str): Código CID a ser consultado.

        Returns:
            dict: Contém o código CID e sua descrição, ou uma mensagem de erro caso não seja encontrado.
        """
        try:
            # Caminho do arquivo cids.json
            file_path = "knowledge/cids.json"

            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                logging.error(f"Arquivo {file_path} não encontrado.")
                return {"error": f"O arquivo {file_path} não foi encontrado."}

            # Carregar o arquivo JSON
            with open(file_path, "r", encoding="utf-8") as f:
                cids_data = json.load(f)

            # Verificar se o CID está presente na lista
            for cid in cids_data:
                if cid["code"] == cid_code:
                    description = cid["description"]
                    logging.info(f"CID {cid_code} encontrado: {description}")
                    return {"cid_code": cid_code, "description": description}

            # Se o CID não for encontrado
            logging.warning(f"CID {cid_code} não encontrado no arquivo.")
            return {"error": f"CID {cid_code} não encontrado no arquivo."}

        except Exception as e:
            logging.error(f"Erro ao consultar o CID: {e}")
            return {"error": f"Erro ao consultar o CID: {e}"}
