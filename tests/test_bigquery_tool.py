from src.tools.bigquery_tool import BigQueryTool, BigQueryToolInput
import pandas as pd

def test_bigquery_tool():
    # Supondo que este é um teste unitário que não se conecta ao BigQuery real (mock necessário)
    tool = BigQueryTool()
    query = "SELECT * FROM `dummy_dataset.dummy_table` LIMIT 10"
    
    input_data = BigQueryToolInput(query_type='custom', custom_query=query)
    result = tool._run(**input_data.dict())

    # Checar se o resultado é um DataFrame
    assert result is not None, "Resultado deve ser um DataFrame, não None"
    assert isinstance(result, pd.DataFrame), "Resultado deve ser um pandas DataFrame"