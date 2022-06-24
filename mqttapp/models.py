from dataclasses import dataclass

import uuid as uuid


@dataclass
class MqttResponse:
    session: uuid.UUID
    topic: str
    text: str


@dataclass
class ProductResult:
    name: str
    art: str
    brand: str
