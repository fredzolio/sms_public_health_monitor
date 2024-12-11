from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.bigquery_tool import BigQueryTool
from tools.pattern_detector_tool import PatternDetector
from tools.decision_maker_tool import DecisionMakerTool
from tools.telegram_tool import TelegramBotTool
from tools.report_compiler_tool import ReportCompilerTool
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
            tools=[BigQueryTool()],
            verbose=True
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
            tools=[DecisionMakerTool()],
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
            tools=[ReportCompilerTool()],
            verbose=True
        )

    # ====================================================
    # Definição das Tarefas
    # ====================================================

    @task
    def collect_data_task(self) -> Task:
        """Tarefa de coleta de dados do BigQuery."""
        logging.info("Criando a tarefa 'collect_data_task'.")
        return Task(
            config=self.tasks_config['collect_data_task'],
            assigned_agent=self.data_collector
        )

    @task
    def monitor_surge_task(self) -> Task:
        """Tarefa de monitoramento para detectar possíveis surtos."""
        logging.info("Criando a tarefa 'monitor_surge_task'.")
        return Task(
            config=self.tasks_config['monitor_surge_task'],
            assigned_agent=self.monitor
        )

    @task
    def decision_task(self) -> Task:
        """Tarefa de tomada de decisão com base nos dados analisados."""
        logging.info("Criando a tarefa 'decision_task'.")
        return Task(
            config=self.tasks_config['decision_task'],
            assigned_agent=self.decision_maker
        )

    @task
    def notify_task(self) -> Task:
        """Tarefa de notificação para alertar autoridades e cidadãos."""
        logging.info("Criando a tarefa 'notify_task'.")
        return Task(
            config=self.tasks_config['notify_task'],
            assigned_agent=self.notifier
        )

    @task
    def generate_monthly_report_task(self) -> Task:
        """Tarefa para gerar um relatório mensal dos surtos detectados."""
        logging.info("Criando a tarefa 'generate_monthly_report_task'.")
        return Task(
            config=self.tasks_config['generate_monthly_report_task'],
            assigned_agent=self.report_generator,
            output_file='monthly_report.md'
        )

    # ====================================================
    # Definição da Crew
    # ====================================================

    @crew
    def crew(self) -> Crew:
        """Cria a equipe SmsDiseaseAlert e orquestra o processo."""
        logging.info("Configurando a Crew 'SmsDiseaseAlert'.")
        return Crew(
            agents=self.agents,  # Agentes definidos pelos decoradores @agent
            tasks=self.tasks,  # Tarefas definidas pelos decoradores @task
            process=Process.sequential,  # Executa as tarefas em sequência
            verbose=True
        )
