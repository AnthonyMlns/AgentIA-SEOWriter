import sys
from src.cli import app

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "run":
        sys.argv.insert(1, "run")
    app()
