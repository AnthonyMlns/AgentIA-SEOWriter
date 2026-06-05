from pathlib import Path

import yaml


class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self._raw = self._load_yaml(config_path)
        self._parse()

    def _load_yaml(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _parse(self):
        pipeline = self._raw.get("pipeline", {})
        self.max_iterations = pipeline.get("max_iterations", 3)
        self.score_seuil = pipeline.get("score_seuil", 7.0)
        self.timeout_global = pipeline.get("timeout_global", 120)

        logging = self._raw.get("logging", {})
        self.log_niveau = logging.get("niveau", "INFO")
        self.log_fichier = logging.get("fichier", "./logs/pipeline.log")
        self.log_format = logging.get("format", "json")

        sortie = self._raw.get("sortie", {})
        self.sortie_format = sortie.get("format", "markdown")
        self.sortie_dossier = sortie.get("dossier", "./output")
