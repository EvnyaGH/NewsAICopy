from abc import ABC, abstractmethod
from typing import Optional


class EmailClient(ABC):
    """Abstract base class for mail delivery backends."""

    @abstractmethod
    def send(
            self,
            to: list[str],
            subject: str,
            html: str,
            text: Optional[str] = None,
            from_: Optional[str] = None,
    ) -> dict:
        """Send an email message.

        Returns a provider response (dict).
        """
        raise NotImplementedError
