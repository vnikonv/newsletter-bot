from abc import ABC, abstractmethod

class GenerateResponse(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Interface function that must be implemented by subclasses."""
        pass
