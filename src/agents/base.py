from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, nom: str):
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
