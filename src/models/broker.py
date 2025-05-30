from dataclasses import dataclass
from typing import Dict, Tuple
from gmqtt import Client as MQTTClient
from datetime import datetime

@dataclass
class BrokerConfig:
    name: str
    host: str
    port: int

class BrokerModel:
    def __init__(self):
        self.brokers: Dict[str, MQTTClient] = {}
        self.broker_configs: Dict[str, Tuple[str, int]] = {}
        self.topic_data: Dict[str, Dict] = {}

    def add_broker_config(self, name: str, host: str, port: int) -> None:
        self.broker_configs[name] = (host, port)

    def create_client(self, broker_name: str) -> MQTTClient:
        client_id = f"mqtt-explorer-{broker_name}-{datetime.now().timestamp()}"
        return MQTTClient(client_id)

    def add_broker(self, broker_name: str, client: MQTTClient) -> None:
        self.brokers[broker_name] = client
        self.topic_data[broker_name] = {}

    def get_broker(self, broker_name: str) -> MQTTClient:
        return self.brokers.get(broker_name)

    def get_broker_config(self, broker_name: str) -> Tuple[str, int]:
        return self.broker_configs.get(broker_name)

    def update_topic_data(self, broker_name: str, topic: str, payload: str) -> None:
        path = topic.split("/")
        current = self.topic_data[broker_name]

        for p in path:
            current = current.setdefault(p, {})

        current["__value__"] = payload

    def get_topic_data(self, broker_name: str) -> Dict:
        return self.topic_data.get(broker_name, {}) 