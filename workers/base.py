from abc import ABC, abstractmethod

class BaseWorker(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response for a given prompt."""
        pass
