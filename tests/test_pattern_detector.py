import pandas as pd
from src.tools.pattern_detector_tool import PatternDetector, PatternDetectorInput

def test_pattern_detector():
    tool = PatternDetector()

    # Criação de um DataFrame de exemplo
    data = {'condicoes': [['CID1', 'CID2'], ['CID1'], [], ['CID3', 'CID4', 'CID5']]}
    dataframe = pd.DataFrame(data)

    input_data = PatternDetectorInput(dataframe=dataframe)
    result = tool._run(**input_data.dict())

    # Verificar se o resultado é um DataFrame e se existem surtos detectados
    assert isinstance(result, pd.DataFrame), "Resultado deve ser um pandas DataFrame"
    assert 'outbreak' in result.columns, "Resultado deve conter a coluna 'outbreak'"