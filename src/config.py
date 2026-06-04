import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


class Config:
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self._raw = self._load_yaml(config_path)
        self._parse()

    def _load_yaml(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _parse(self):
        api = self._raw.get("api", {})
        self.api_model = api.get("model", "deepseek-chat")
        self.api_temperature = api.get("temperature", 0.7)
        self.api_max_tokens = api.get("max_tokens_per_call", 4096)
        self.api_timeout = api.get("timeout", 30)
        self.api_retry_attempts = api.get("retry_attempts", 2)
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

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

    @property
    def api_config(self) -> dict:
        return {
            "api_key": self.api_key,
            "base_url": self.api_base_url,
            "model": self.api_model,
            "temperature": self.api_temperature,
            "max_tokens": self.api_max_tokens,
            "timeout": self.api_timeout,
            "retry_attempts": self.api_retry_attempts,
        }
