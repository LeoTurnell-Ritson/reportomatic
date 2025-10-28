import logging
from datetime import datetime, timedelta

import click

from .__init__ import __version__
from .adapters import states
from .client import Client

logger = logging.getLogger(__name__)


def setup_logger(level):
    logging.basicConfig(
        format="%(levelname)-8s|%(message)s",
        level=level,
    )


@click.group()
@click.version_option(version=__version__)
@click.argument("url")
@click.option(
    "-v",
    count=True,
    help="Increase logging verbosity (-v, -vv, -vvv, etc.).",
)
@click.pass_context
def cli(ctx, url, v):
    """Automated markdown report generation for GitHub and GitLab repositories."""
    setup_logger(
        [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO][v]
        if v < 4 else logging.DEBUG
    )
    try:
        ctx.obj = Client(url)
    except Exception as e:
        logger.error("Error initializing client: %s", e)
        ctx.echo("Failed to initialize client.")
        ctx.exit(1)


@cli.command()
@click.option(
    "-s",
    "--stale-days",
    type=int,
    default=30,
    help="Number of days to consider an issue stale and ignore it, default is 30 days.",
)
@click.pass_context
def issues(ctx, stale_days):
    updated_after = datetime.now() - timedelta(days=stale_days)
    try:
        for issue in ctx.obj.issues(
            state=states.IssueState.OPEN,
            updated_after=updated_after
        ):
            click.echo(f"+ {issue}")

        for issue in ctx.obj.issues(
            state=states.IssueState.CLOSED,
            updated_after=updated_after
        ):
            click.echo(f"+ ~~{issue}~~")
    except Exception as e:
        logger.error("Error fetching issues: %s", e)
        click.echo("Failed to fetch issues.")
        ctx.exit(1)


@cli.command()
@click.option(
    "-s",
    "--stale-days",
    type=int,
    default=14,
    help=(
        "Number of days to consider a merge/pull request "
        "stale and ignore it, default is 14 days."
    ),
)
@click.pass_context
def pulls(ctx, stale_days):
    updated_after = datetime.now() - timedelta(days=stale_days)
    try:
        for mr in [
            *ctx.obj._adapter.pulls(
                state=states.PullState.OPEN,
                updated_after=updated_after
            ),
            *ctx.obj._adapter.pulls(
                state=states.PullState.MERGED,
                updated_after=updated_after
            )
        ]:
            click.echo(f"+ {mr}")
            for extra in mr.extras():
                click.echo(f"    + {extra}")

    except Exception as e:
        logger.error("Error fetching merge requests: %s", e)
        click.echo("Failed to fetch merge requests.")
        ctx.exit(1)


if __name__ == "__main__":
    cli()
