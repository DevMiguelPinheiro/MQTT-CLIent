import asyncio
from datetime import datetime
from textual.screen import Screen
from textual.widgets import Select, Input, Log, Button

from src.models.stress_test import StressTestModel
from src.models.broker import BrokerModel

class StressTestController:
    def __init__(self, screen: Screen, broker_model: BrokerModel):
        self.screen = screen
        self.broker_model = broker_model
        self.stress_test_model = StressTestModel()
        self.setup_ui()

    def setup_ui(self):
        self.broker_select = self.screen.query_one("#broker_select", Select)
        self.topic_input = self.screen.query_one("#topic_input", Input)
        self.message_count = self.screen.query_one("#message_count", Input)
        self.interval = self.screen.query_one("#interval", Input)
        self.message_size = self.screen.query_one("#message_size", Input)
        self.test_log = self.screen.query_one("#test_log", Log)
        self.export_button = self.screen.query_one("#export_csv", Button)

        # Preencher o select com os brokers disponíveis
        broker_options = [(name, name) for name in self.broker_model.broker_configs.keys()]
        self.broker_select.options = [("", "Selecione um broker")] + broker_options

    async def run_stress_test(self):
        broker_name = self.broker_select.value
        topic = self.topic_input.value
        count = int(self.message_count.value or "100")
        interval = int(self.interval.value or "100")
        size = int(self.message_size.value or "1024")

        if not broker_name or not topic:
            self.test_log.write("Por favor, selecione um broker e um tópico.")
            return

        client = self.broker_model.get_broker(broker_name)
        if not client:
            self.test_log.write(f"Broker {broker_name} não está conectado.")
            return

        self.test_log.write(f"Iniciando teste de estresse:\n")
        self.test_log.write(f"Broker: {broker_name}\n")
        self.test_log.write(f"Tópico: {topic}\n")
        self.test_log.write(f"Mensagens: {count}\n")
        self.test_log.write(f"Intervalo: {interval}ms\n")
        self.test_log.write(f"Tamanho: {size} bytes\n")

        self.stress_test_model.clear_results()
        start_time = datetime.now()
        last_message_time = start_time

        for i in range(count):
            current_time = datetime.now()
            payload = self.stress_test_model.generate_random_payload(size)
            client.publish(topic, payload)
            
            # Calcular métricas
            message_time = current_time - last_message_time
            total_time = current_time - start_time
            
            # Armazenar resultados
            self.stress_test_model.add_test_result({
                'message_number': i + 1,
                'timestamp': current_time.isoformat(),
                'message_size_bytes': size,
                'interval_ms': message_time.total_seconds() * 1000,
                'total_time_ms': total_time.total_seconds() * 1000,
                'topic': topic,
                'broker': broker_name
            })
            
            self.test_log.write(f"Enviada mensagem {i+1}/{count}")
            last_message_time = current_time
            await asyncio.sleep(interval / 1000)

        # Calcular e exibir métricas finais
        metrics = self.stress_test_model.calculate_metrics()
        self.test_log.write(f"\nTeste concluído em {metrics['total_time_seconds']:.2f} segundos")
        self.test_log.write(f"Taxa média: {metrics['messages_per_second']:.2f} mensagens/segundo")
        self.test_log.write(f"Intervalo médio entre mensagens: {metrics['avg_interval_ms']:.2f}ms")
        
        self.stress_test_model.mark_test_completed()
        self.export_button.disabled = False

    def export_results(self):
        if not self.stress_test_model.test_completed:
            self.test_log.write("Execute um teste primeiro para exportar os resultados.")
            return

        filename = self.stress_test_model.export_to_csv()
        if filename:
            self.test_log.write(f"\nResultados exportados para: {filename}")
        else:
            self.test_log.write("\nErro ao exportar resultados.") 