import asyncio
from datetime import datetime
from gmqtt import Client as MQTTClient

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Static, Log, Input, Button
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive
from textual.screen import Screen


class AddBrokerScreen(Screen):
    """Tela para adicionar um novo broker MQTT."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield Static("Adicionar novo Broker MQTT", id="titulo")
            yield Static("Nome para identificação:")
            self.name_input = Input(placeholder="Ex.: BrokerCasa", id="name_input")
            yield self.name_input
            yield Static("Endereço/IP do broker:")
            self.host_input = Input(placeholder="Ex.: 192.168.0.10", id="host_input")
            yield self.host_input
            yield Static("Porta do broker (default 1883):")
            self.port_input = Input(placeholder="1883", id="port_input")
            yield self.port_input
            yield Button("Conectar", id="connect_button")
            yield Button("Cancelar", id="cancel_button")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "connect_button":
            name = self.name_input.value.strip()
            host = self.host_input.value.strip()
            port = int(self.port_input.value.strip() or "1883")
            if name and host:
                self.app.add_broker(name, host, port)
            self.app.pop_screen()

        if event.button.id == "cancel_button":
            self.app.pop_screen()


class MQTTExplorer(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("a", "add_broker", "Adicionar Broker")
    ]

    connection_status = reactive("Desconectado")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="left_panel"):
                yield Static("Tópicos", id="titulo")
                yield Tree("MQTT Connections", id="arvore")
            with Vertical(id="right_panel"):
                yield Static("Payloads", id="titulo")
                yield Log(highlight=True, id="payloads")
        yield Footer()

    def on_mount(self) -> None:
        self.brokers = {}  # {broker_name: client}
        self.topic_data = {}  # {broker_name: {topic_tree}}
        self.topic_tree = self.query_one("#arvore", Tree)
        self.payloads = self.query_one("#payloads", Log)

    def action_refresh(self) -> None:
        self.refresh_tree()

    def action_add_broker(self) -> None:
        self.push_screen(AddBrokerScreen())

    def refresh_tree(self):
        self.topic_tree.root.label = "MQTT Connections"
        self.topic_tree.root.remove_children()

        for broker_name, data in self.topic_data.items():
            broker_branch = self.topic_tree.root.add(f"[green]{broker_name}[/green]")
            self.build_tree(data, broker_branch)

        self.topic_tree.root.expand()

    def build_tree(self, data, root):
        for key, value in data.items():
            if key == "__value__":
                continue
            branch = root.add(key)
            if "__value__" in value:
                branch.add(f"[Payload] {value['__value__']}")
            self.build_tree(value, branch)

    def add_broker(self, broker_name, host, port):
        asyncio.create_task(self.mqtt_start(broker_name, host, port))

    async def mqtt_start(self, broker_name, host, port):
        client_id = f"mqtt-explorer-{broker_name}-{datetime.now().timestamp()}"
        client = MQTTClient(client_id)

        client.on_connect = lambda *_: self.on_connect(broker_name)
        client.on_message = lambda *_args: self.on_message(broker_name, *_args)
        client.on_disconnect = lambda *_: self.on_disconnect(broker_name)

        await client.connect(host, port)

        self.brokers[broker_name] = client
        self.topic_data[broker_name] = {}

    def on_connect(self, broker_name):
        self.connection_status = f"Conectado: {broker_name}"
        self.brokers[broker_name].subscribe("#")

    def on_disconnect(self, broker_name):
        self.connection_status = f"Desconectado: {broker_name}"

    def on_message(self, broker_name, client, topic, payload, qos, properties):
        payload = payload.decode(errors="ignore")
        path = topic.split("/")
        current = self.topic_data[broker_name]

        for p in path:
            current = current.setdefault(p, {})

        current["__value__"] = payload

        self.payloads.write(f"[{broker_name} - {topic}] {payload}")

        self.refresh_tree()


if __name__ == "__main__":
    MQTTExplorer().run()
