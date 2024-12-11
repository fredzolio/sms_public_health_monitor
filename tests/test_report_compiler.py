import pandas as pd
from src.tools.report_compiler_tool import ReportCompilerTool, ReportCompilerInput

def test_report_compiler():
    tool = ReportCompilerTool()
    
    # Criar DataFrames de exemplo
    data1 = {'condicoes': ['CID1', 'CID2'], 'cid_count': [5, 3]}
    data2 = {'condicoes': ['CID3', 'CID1'], 'cid_count': [2, 4]}
    dataframe1 = pd.DataFrame(data1)
    dataframe2 = pd.DataFrame(data2)

    input_data = ReportCompilerInput(dataframes_list=[dataframe1, dataframe2])
    result = tool._run(**input_data.dict())

    # Verificar se o resultado é uma string e contém o termo "Relatório Mensal de Surtos"
    assert isinstance(result, str), "O resultado deve ser uma string"
    assert "Relatório Mensal de Surtos" in result, "O relatório deve conter o título 'Relatório Mensal de Surtos'"