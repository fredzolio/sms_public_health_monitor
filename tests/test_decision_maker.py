import pandas as pd
from src.tools.decision_maker_tool import DecisionMakerTool, DecisionMakerInput

def test_decision_maker_no_outbreak():
    tool = DecisionMakerTool()

    # Criação de um DataFrame sem surtos detectados
    data = {'cid_count': [1, 2, 3], 'outbreak': [1, 1, 1]}
    dataframe = pd.DataFrame(data)

    input_data = DecisionMakerInput(outbreaks=dataframe)
    result = tool._run(**input_data.dict())

    # Sem surtos, deve retornar False
    assert result is False, "Sem surtos, não deve haver notificação"

def test_decision_maker_with_outbreak():
    tool = DecisionMakerTool()

    # Criação de um DataFrame com surtos detectados
    data = {'cid_count': [1, 2, 3, 4, 5, 6], 'outbreak': [1, 1, -1, -1, -1, -1]}
    dataframe = pd.DataFrame(data)

    input_data = DecisionMakerInput(outbreaks=dataframe)
    result = tool._run(**input_data.dict())

    # Com surtos, deve retornar True
    assert result is True, "Com surtos suficientes, deve haver notificação"