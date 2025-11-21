from aiokafka import AIOKafkaProducer
import json


class KafkaClient:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic: str, message: dict):
        if not self.producer:
            raise RuntimeError("Producer not started")
        await self.producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))
