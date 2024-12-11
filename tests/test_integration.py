import pandas as pd
from sms_disease_alert import SmsDiseaseAlert

def test_integration():
    crew = SmsDiseaseAlert()
    # Executar a coleta de dados e a detecção de surtos
    data_collected = crew.data_collector().tools[0]._run(query_type='daily_collect')
    outbreaks = crew.monitor().tools[0]._run(dataframe=data_collected)

    # Certificar-se de que o ciclo de coleta e detecção funciona como esperado
    assert isinstance(outbreaks, pd.DataFrame), "Outbreaks deve ser um DataFrame"