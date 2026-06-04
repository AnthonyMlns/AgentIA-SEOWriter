import time
import logging
from abc import ABC, abstractmethod

from src.client import DeepSeekClient


logger = logging.getLogger(__name__)


class Agent(ABC):
    def __init__(self, client: DeepSeekClient, nom: str):
        self.client = client
        self.nom = nom

    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    def formatter_entree(self, **kwargs) -> str:
        ...

    @abstractmethod
    def parser_sortie(self, texte: str, **kwargs):
        ...

    def executer(self, **kwargs):
        debut = time.time()
        logger.info({"event": "agent_start", "agent": self.nom})

        try:
            system = self.system_prompt()
            user = self.formatter_entree(**kwargs)
            reponse = self.client.chat(system, user)
            resultat = self.parser_sortie(reponse, **kwargs)
            duree = time.time() - debut
            logger.info({
                "event": "agent_end",
                "agent": self.nom,
                "duration_s": round(duree, 2),
            })
            return resultat

        except Exception as e:
            duree = time.time() - debut
            logger.error({
                "event": "agent_error",
                "agent": self.nom,
                "duration_s": round(duree, 2),
                "error": str(e),
            })
            raise
