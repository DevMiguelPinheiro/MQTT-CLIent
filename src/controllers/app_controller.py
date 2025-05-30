import asyncio
import json
from datetime import datetime
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Tree, Log

from src.models.broker import BrokerModel
from src.models.stress_test import StressTestModel
from src.views.screens import MainScreen, AddBrokerScreen, StressTestScreen

class MQTTExplorerController(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_broker", "Adicionar Broker"),
        ("enter", "connect_broker", "Conectar Broker Selecionado"),
        ("s", "stress_test", "Teste de Estresse")
    ]

    connection_status = reactive("Desconectado")

    def __init__(self):
        super().__init__()
        self.broker_model = BrokerModel()
        self.stress_test_model = StressTestModel()
        self.current_selection = None

    def compose(self) -> ComposeResult:
        yield MainScreen()

    def on_mount(self) -> None:
        self.topic_tree = self.query_one("#arvore", Tree)
        self.payloads = self.query_one("#payloads", Log)
        self.refresh_tree()

    def refresh_tree(self):
        self.topic_tree.root.label = "MQTT Connections"
        broker_labels = {str(node.label): node for node in self.topic_tree.root.children}

        for broker_name, data in self.broker_model.topic_data.items():
            broker_branch = broker_labels.get(broker_name)
            if broker_branch is None:
                broker_branch = self.topic_tree.root.add(broker_name)
            self.build_tree(data, broker_branch)

        self.topic_tree.root.expand()

    def build_tree(self, data, root):
        existing_labels = {str(child.label): child for child in root.children}
        for key, value in data.items():
            if key == "__value__":
                continue
            branch = existing_labels.get(key)
            if branch is None:
                branch = root.add(key)
            self.build_tree(value, branch)

    def action_add_broker(self) -> None:
        self.push_screen(AddBrokerScreen())

    def action_connect_broker(self):
        node = self.topic_tree.cursor_node
        if node and node.parent == self.topic_tree.root:
            broker_name = str(node.label)
            if broker_name not in self.broker_model.brokers:
                host, port = self.broker_model.get_broker_config(broker_name)
                self.add_broker(broker_name, host, port)

    def add_broker(self, broker_name: str, host: str, port: int):
        asyncio.create_task(self.mqtt_start(broker_name, host, port))

    async def mqtt_start(self, broker_name: str, host: str, port: int):
        client = self.broker_model.create_client(broker_name)
        client.on_connect = lambda *_: self.on_connect(broker_name)
        client.on_message = lambda *_args: self.on_message(broker_name, *_args)
        client.on_disconnect = lambda *_: self.on_disconnect(broker_name)

        self.broker_model.add_broker(broker_name, client)
        await client.connect(host, port)
        asyncio.create_task(client.listen())
        self.refresh_tree()

    def on_connect(self, broker_name: str):
        self.connection_status = f"Conectado: {broker_name}"
        self.broker_model.get_broker(broker_name).subscribe("#")

    def on_disconnect(self, broker_name: str):
        self.connection_status = f"Desconectado: {broker_name}"

    def on_message(self, broker_name: str, client, topic: str, payload, qos, properties):
        payload_str = payload.decode(errors="ignore")
        self.broker_model.update_topic_data(broker_name, topic, payload_str)
        self.refresh_tree()

        if self.current_selection:
            broker, *topic_parts = self.current_selection
            if broker == broker_name and '/'.join(topic_parts) == topic:
                self.display_payload(broker_name, topic_parts)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        parts = []
        current = node

        while current and current.parent is not None:
            parts.insert(0, str(current.label))
            current = current.parent

        if len(parts) < 2:
            self.current_selection = None
            self.payloads.clear()
            self.payloads.write("Selecione um tópico para ver os payloads.")
            return

        broker_name = parts[0]
        topic_parts = parts[1:]
        self.current_selection = parts
        self.display_payload(broker_name, topic_parts)

    def display_payload(self, broker_name: str, topic_parts: list):
        try:
            current_data = self.broker_model.get_topic_data(broker_name)
            for part in topic_parts:
                current_data = current_data.get(part, {})

            payload = current_data.get("__value__", None)
            self.payloads.clear()

            if payload:
                try:
                    parsed = json.loads(payload)
                    formatted_payload = json.dumps(parsed, indent=4, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    formatted_payload = payload

                message = f"\n[bold green]{broker_name}[/bold green] → [yellow]{'/'.join(topic_parts)}[/yellow]\n{formatted_payload}\n"
                self.payloads.write(message)
            else:
                self.payloads.write("Nenhum payload recebido para este tópico ainda.")

        except KeyError:
            self.payloads.clear()
            self.payloads.write("Nenhum dado para este tópico.")

    def action_stress_test(self) -> None:
        self.push_screen(StressTestScreen()) 