import typer
from typing import Optional

from src.config import Config
from src.client import DeepSeekClient
from src.logger import setup_logging
from src.agents.strategie import AgentStrategie
from src.agents.recherche import AgentRecherche
from src.agents.redaction import AgentRedaction
from src.agents.critique import AgentCritique
from src.orchestrator import Orchestrator


app = typer.Typer()


@app.command()
def run(
    requete: str = typer.Argument(..., help="Sujet de l'article à rédiger"),
    mots_cles: str = typer.Option("", "--mots-cles", "-k",
                                  help="Mots-clés cibles (séparés par des virgules)"),
    ton: str = typer.Option("", "--ton", "-t",
                            help="Ton de rédaction (vulgarisation, technique, professionnel)"),
    longueur: str = typer.Option("", "--longueur", "-l",
                                 help="Intervalle de mots (ex: 1200-1500)"),
    audience: str = typer.Option("", "--audience", "-a",
                                 help="Audience cible"),
    sources: str = typer.Option("", "--sources", "-s",
                                help="URLs sources (séparées par des espaces)"),
    config_path: str = typer.Option("config.yaml", "--config", "-c",
                                    help="Chemin vers le fichier de configuration"),
    yes: bool = typer.Option(False, "--yes", "-y",
                             help="Mode non-interactif"),
):
    cfg = Config(config_path)
    log = setup_logging(cfg)
    log.info({"event": "cli_start", "requete": requete})

    if not cfg.api_key:
        typer.echo("Erreur : DEEPSEEK_API_KEY non définie. "
                   "Créez un fichier .env à partir de .env.example")
        raise typer.Exit(1)

    if not requete.strip():
        typer.echo("Erreur : la requête ne peut pas être vide.")
        raise typer.Exit(1)

    client = DeepSeekClient(cfg.api_config)

    agent_strategie = AgentStrategie(client)
    agent_recherche = AgentRecherche(client)
    agent_redaction = AgentRedaction(client)
    agent_critique = AgentCritique(client)

    orchestrator = Orchestrator(
        config=cfg,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
    )

    sources_list = [s.strip() for s in sources.split()] if sources else None

    resultat = orchestrator.executer(
        requete=requete,
        mots_cles=mots_cles,
        ton=ton,
        longueur=longueur,
        audience=audience,
        sources=sources_list,
    )

    typer.echo("")
    typer.echo("=== Résultat ===")
    typer.echo(f"  Article : {resultat['chemin_article']}")
    typer.echo(f"  Rapport : {resultat['chemin_rapport']}")
    typer.echo(f"  Score    : {resultat['score']}/10")
    typer.echo(f"  Itérations : {resultat['iterations']}")
    typer.echo(f"  Durée   : {resultat['duree_totale']}s")
    if resultat['seuil_atteint']:
        typer.echo("  ✅ Seuil atteint")
    else:
        typer.echo("  ⚠️  Seuil non atteint (meilleur draft conservé)")


if __name__ == "__main__":
    app()
