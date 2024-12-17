import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from src.tools.csv_tool import CSVTool
from tools.pattern_detector_tool import PatternDetector
from tools.telegram_tool import TelegramBotTool
import logging


# Configuração do logger
logging.basicConfig(level=logging.INFO)

@CrewBase
class SmsDiseaseAlert:
    """SmsDiseaseAlert crew"""

    # Configurações para os arquivos YAML
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # ====================================================
    # Definição dos Agentes
    # ====================================================

    @agent
    def data_collector(self) -> Agent:
        """Agente responsável pela coleta de dados do BigQuery."""
        logging.info("Inicializando o agente 'data_collector'.")
        return Agent(
            config=self.agents_config['data_collector'],
            tools=[CSVTool()],
            verbose=True,
        )

    @agent
    def monitor(self) -> Agent:
        """Agente responsável por monitorar os dados e identificar padrões."""
        logging.info("Inicializando o agente 'monitor'.")
        return Agent(
            config=self.agents_config['monitor'],
            tools=[PatternDetector()],
            verbose=True
        )

    @agent
    def decision_maker(self) -> Agent:
        """Agente responsável por tomar decisões com base nos dados monitorados."""
        logging.info("Inicializando o agente 'decision_maker'.")
        return Agent(
            config=self.agents_config['decision_maker'],
            verbose=True
        )

    @agent
    def notifier(self) -> Agent:
        """Agente responsável por enviar notificações através do Telegram."""
        logging.info("Inicializando o agente 'notifier'.")
        return Agent(
            config=self.agents_config['notifier'],
            tools=[TelegramBotTool()],
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        """Agente responsável pela geração de relatórios mensais."""
        logging.info("Inicializando o agente 'report_generator'.")
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True
        )

    # ====================================================
    # Definição das Tarefas
    # ====================================================

    @task
    def collect_data_task(self) -> Task:
        """Tarefa de coleta de dados em arquivo CSV."""
        logging.info("Criando a tarefa 'collect_data_task'.")
        return Task(
            config=self.tasks_config['collect_data_task'],
            assigned_agent=self.data_collector,
        )

    @task
    def monitor_surge_task(self) -> Task:
        """Tarefa de monitoramento para detectar possíveis surtos."""
        logging.info("Criando a tarefa 'monitor_surge_task'.")
        return Task(
            config=self.tasks_config['monitor_surge_task'],
            assigned_agent=self.monitor,
        )

    @task
    def decision_task(self) -> Task:
        """Tarefa de tomada de decisão com base nos dados analisados."""
        logging.info("Criando a tarefa 'decision_task'.")
        return Task(
            config=self.tasks_config['decision_task'],
            assigned_agent=self.decision_maker,
            context=[self.monitor_surge_task()]
        )

    @task
    def notify_task(self) -> Task:
        """Tarefa de notificação para alertar autoridades e cidadãos."""
        logging.info("Criando a tarefa 'notify_task'.")
        return Task(
            config=self.tasks_config['notify_task'],
            assigned_agent=self.notifier,
            context=[self.decision_task()]
        )

    @task
    def generate_monthly_report_task(self) -> Task:
        """Tarefa para gerar um relatório mensal dos surtos detectados."""
        logging.info("Criando a tarefa 'generate_monthly_report_task'.")
        return Task(
            config=self.tasks_config['generate_monthly_report_task'],
            assigned_agent=self.report_generator,
            output_file='monthly_report.md',
            context=[self.collect_data_task(), self.decision_task(), self.monitor_surge_task(), self.notify_task()]
        )

    # ====================================================
    # Definição da Crew
    # ====================================================
    
    # knowledge_notification_guidelines = TextFileKnowledgeSource(
    #     file_path='knowledge/notification_guidelines.txt',
    # )
    # knowledge_report_template = TextFileKnowledgeSource(
    #     file_path='knowledge/monthly_report_template.txt',
    # )
    # knowledge_csv_data = CSVKnowledgeSource(
    #     file_path='data/health_data.csv',
    # )

    @crew
    def crew(self) -> Crew:
        """Cria a equipe SmsDiseaseAlert e orquestra o processo."""
        logging.info("Configurando a Crew 'SmsDiseaseAlert'.")
        return Crew(
            agents=self.agents,  # Agentes definidos pelos decoradores @agent
            tasks=self.tasks,  # Tarefas definidas pelos decoradores @task
            process=Process.sequential,  # Executa as tarefas em sequência
            verbose=True,
            # knowledge_sources=[knowledge_disease_patterns, knowledge_notification_guidelines, knowledge_report_template], # type: ignore
            # embedder={
            #     "provider": "google",
            #     "config": {"model": "gemini/text-embedding-004", "api_key": os.getenv("GEMINI_API_KEY")},
            # },
        )
