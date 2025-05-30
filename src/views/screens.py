from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Tree, Static, Log, Input, Button, Select
from textual.containers import Container

class AddBrokerScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield Static("Adicionar novo Broker MQTT", id="titulo")
            yield Static("Nome para identificação:")
            self.name_input = Input(placeholder="Ex.: BrokerCasa")
            yield self.name_input
            yield Static("Endereço/IP do broker:")
            self.host_input = Input(placeholder="Ex.: 192.168.0.10")
            yield self.host_input
            yield Static("Porta do broker (default 1883):")
            self.port_input = Input(placeholder="1883")
            yield self.port_input
            yield Button("Conectar", id="connect_button")
            yield Button("Cancelar", id="cancel_button")
        yield Footer()

class StressTestScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield Static("Teste de Estresse MQTT", id="titulo")
            yield Static("Broker:")
            self.broker_select = Select([("", "Selecione um broker")], id="broker_select")
            yield self.broker_select
            yield Static("Tópico:")
            self.topic_input = Input(placeholder="Ex.: teste/estresse")
            yield self.topic_input
            yield Static("Número de mensagens:")
            self.message_count = Input(placeholder="100")
            yield self.message_count
            yield Static("Intervalo entre mensagens (ms):")
            self.interval = Input(placeholder="100")
            yield self.interval
            yield Static("Tamanho da mensagem (bytes):")
            self.message_size = Input(placeholder="1024")
            yield self.message_size
            yield Button("Iniciar Teste", id="start_test")
            yield Button("Cancelar", id="cancel_test")
            yield Button("Exportar CSV", id="export_csv", disabled=True)
            yield Log(id="test_log")
        yield Footer()

class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            with Container(id="left_panel"):
                yield Static("Tópicos", id="titulo")
                yield Tree("MQTT Connections", id="arvore")
            with Container(id="right_panel"):
                yield Static("Payloads", id="titulo")
                yield Log(highlight=True, id="payloads")
        yield Footer() 