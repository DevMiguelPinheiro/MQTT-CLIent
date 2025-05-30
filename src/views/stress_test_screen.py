from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Select, Input, Log, Button, Label
import asyncio

class StressTestScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Voltar"),
        ("f5", "run_test", "Executar Teste"),
    ]

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Teste de Estresse", classes="screen-title")
            
            with Vertical():
                with Horizontal():
                    yield Label("Broker:")
                    yield Select(id="broker_select")
                
                with Horizontal():
                    yield Label("Tópico:")
                    yield Input(id="topic_input", placeholder="Digite o tópico")
                
                with Horizontal():
                    yield Label("Número de Mensagens:")
                    yield Input(id="message_count", placeholder="100")
                
                with Horizontal():
                    yield Label("Intervalo (ms):")
                    yield Input(id="interval", placeholder="100")
                
                with Horizontal():
                    yield Label("Tamanho da Mensagem (bytes):")
                    yield Input(id="message_size", placeholder="1024")
                
                with Horizontal():
                    yield Button("Executar Teste", id="run_test", variant="primary")
                    yield Button("Exportar CSV", id="export_csv", variant="success", disabled=True)
                
                yield Log(id="test_log")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run_test":
            self.run_stress_test()
        elif event.button.id == "export_csv":
            self.export_results()

    def action_run_test(self) -> None:
        self.run_stress_test()

    def run_stress_test(self) -> None:
        controller = self.app.stress_test_controller
        asyncio.create_task(controller.run_stress_test())

    def export_results(self) -> None:
        controller = self.app.stress_test_controller
        controller.export_results() 