from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def reply(self, message: str) -> str:
        """Return a reply; remote providers must be run outside the GUI thread."""
