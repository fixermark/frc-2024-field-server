from abc import ABC, abstractmethod
from enum import IntEnum

"""Generic message receiver."""

class Alliance(IntEnum):
    RED = 0
    BLUE = 1

class FieldElement(IntEnum):
    SPEAKER = 0
    AMP = 1

class Message(ABC):
    "A message."
    @property
    def name(self) -> str:
        return self.__class__.__name__


class Receiver(ABC):
    @abstractmethod
    def receive_message(self, alliance: Alliance, element: FieldElement, message: Message) -> None:
        """Receive a message."""
