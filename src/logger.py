import json
import logging
import sys
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.msg, dict):
            return json.dumps(record.msg, ensure_ascii=False)
        return json.dumps({"message": record.getMessage()}, ensure_ascii=False)


def setup_logging(config) -> logging.Logger:
    niveau = getattr(logging, config.log_niveau.upper(), logging.INFO)
    logger = logging.getLogger("seo_agent")
    logger.setLevel(niveau)
    logger.handlers.clear()

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(niveau)

    if config.log_format == "json":
        console.setFormatter(JsonFormatter())
    else:
        console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.addHandler(console)

    if config.log_fichier:
        path = Path(config.log_fichier)
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setLevel(niveau)
        if config.log_format == "json":
            fh.setFormatter(JsonFormatter())
        else:
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)

    return logger
