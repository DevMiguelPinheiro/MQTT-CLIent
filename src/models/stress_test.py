from dataclasses import dataclass
from typing import List, Dict
import csv
from pathlib import Path
from datetime import datetime
import random
import string
import os

@dataclass
class StressTestResult:
    message_number: int
    timestamp: str
    message_size_bytes: int
    interval_ms: float
    total_time_ms: float
    topic: str
    broker: str

class StressTestModel:
    def __init__(self):
        self.test_results: List[Dict] = []
        self.test_completed = False

    def generate_random_payload(self, size: int) -> str:
        """Gera uma string aleatória do tamanho especificado."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

    def add_test_result(self, result: Dict) -> None:
        """Adiciona um resultado de teste à lista."""
        self.test_results.append(result)

    def clear_results(self) -> None:
        """Limpa os resultados anteriores."""
        self.test_results = []
        self.test_completed = False

    def calculate_metrics(self) -> Dict:
        """Calcula métricas com base nos resultados do teste."""
        if not self.test_results:
            return {
                'total_time_seconds': 0,
                'messages_per_second': 0,
                'avg_interval_ms': 0
            }

        total_time = self.test_results[-1]['total_time_ms'] / 1000  # Converter para segundos
        message_count = len(self.test_results)
        
        # Calcular intervalo médio entre mensagens
        intervals = [result['interval_ms'] for result in self.test_results[1:]]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        return {
            'total_time_seconds': total_time,
            'messages_per_second': message_count / total_time if total_time > 0 else 0,
            'avg_interval_ms': avg_interval
        }

    def mark_test_completed(self) -> None:
        """Marca o teste como concluído."""
        self.test_completed = True

    def export_to_csv(self) -> str:
        """Exporta os resultados para um arquivo CSV."""
        if not self.test_results:
            return None

        # Criar diretório de resultados se não existir
        os.makedirs('results', exist_ok=True)

        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'results/stress_test_{timestamp}.csv'

        # Escrever resultados no arquivo CSV
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = self.test_results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.test_results:
                writer.writerow(result)

        return filename 