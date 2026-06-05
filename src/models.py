from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BriefSEO:
    requete: str
    mots_cles_principaux: list[str]
    mots_cles_secondaires: list[str]
    intention_recherche: str
    structure_cible: list[str]
    longueur_min: int
    longueur_max: int
    ton: str
    audience_cible: str
    contraintes_supplementaires: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Synthese:
    brief: BriefSEO
    sources: list[dict]
    documents_fournis: Optional[list[str]]
    insights_cles: list[str]
    lacunes_identifiees: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Draft:
    brief: BriefSEO
    synthese: Synthese
    titre: str
    sections: dict[str, str]
    meta_description: str
    version: int = 1
    historique_critiques: Optional[list[dict]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RapportCritique:
    draft: Draft
    score_editorial: float
    score_seo: float
    score_global: float
    seuil_atteint: bool
    critiques: list[dict]
    suggestions_prioritaires: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RapportConformiteGoogle:
    draft: Draft
    score_eeat: float
    score_semantique: float
    score_lisibilite: float
    score_featured_snippet: float
    score_maillage: float
    score_meta: float
    score_structure: float
    score_originalite: float
    score_global: float
    conformite_atteinte: bool
    recommandations: list[dict]
    suggestions_prioritaires: list[str]

    def to_dict(self) -> dict:
        return asdict(self)
