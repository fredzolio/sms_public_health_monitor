from datetime import datetime
import os
import sys
import warnings

from crew import SmsDiseaseAlert

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Este arquivo principal é destinado para executar sua equipe localmente, então evite adicionar lógica desnecessária.
# Substitua as entradas pelos valores que deseja testar.

def run():
    """
    Executa a equipe.
    """
    inputs = {
        'csv_file': 'data/health_data.csv',
        'chat_id_cidadao': os.getenv('CHAT_FRED_ID'),
        'chat_id_gov': os.getenv('CHAT_FRED_ID'),
        'current_date': datetime.now().strftime("%d/%m/%Y")
    }
    SmsDiseaseAlert().crew().kickoff(inputs=inputs)

def train():
    """
    Treina a equipe por um número específico de iterações.
    """
    inputs = {
        "topic": "Surto de Doenças"
    }
    try:
        SmsDiseaseAlert().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"Ocorreu um erro durante o treinamento da equipe: {e}")

def replay():
    """
    Reproduz a execução da equipe a partir de uma tarefa específica.
    """
    try:
        SmsDiseaseAlert().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"Ocorreu um erro ao reproduzir a execução da equipe: {e}")

def test():
    """
    Testa a execução da equipe e retorna os resultados.
    """
    inputs = {
        "topic": "Surto de Doenças"
    }
    try:
        SmsDiseaseAlert().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"Ocorreu um erro ao testar a execução da equipe: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: main.py [run|train|replay|test] [args]")
    else:
        command = sys.argv[1]
        if command == "run":
            run()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            print("Comando não reconhecido. Use: [run|train|replay|test]")
