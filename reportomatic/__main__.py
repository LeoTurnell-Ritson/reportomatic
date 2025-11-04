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
    "-d",
    "--stale-days",
    type=int,
    default=30,
    help="Number of days to consider an issue stale and ignore it, default is 30 days.",
)
@click.option(
    "-s",
    "--state",
    type=click.Choice(["open", "closed"], case_sensitive=False),
    default="open",
    help="Filter issues by state: open, closed, default is open.",
)
@click.option(
    "--prefix",
    type=str,
    default="+ ",
    help="Prefix to use for each issue in the output, default is '+ '.",
)
@click.option(
    "-t",
    "--strike-through",
    is_flag=True,
    help="Use strike-through formatting for issues.",
)
@click.pass_context
def issues(ctx, stale_days, state, prefix, strike_through):
    updated_after = datetime.now() - timedelta(days=stale_days)
    wraps = "~~" if strike_through else ""

    try:
        for issue in ctx.obj.issues(
            state=states.IssueState[state.upper()],
            updated_after=updated_after
        ):
            click.echo(f"{prefix}{wraps}{issue}{wraps}")
    except Exception as e:
        logger.error("Error fetching issues: %s", e)
        click.echo("Failed to fetch issues.")
        ctx.exit(1)


@cli.command()
@click.option(
    "-d",
    "--stale-days",
    type=int,
    default=14,
    help=(
        "Number of days to consider a merge/pull request "
        "stale and ignore it, default is 14 days."
    ),
)
@click.option(
    "-s",
    "--state",
    type=click.Choice(["open", "closed", "merged"], case_sensitive=False),
    default="open",
    help=(
        "Filter issues by state: open, closed, or merged, default is open."
        " n.b. 'merged' state is not applicable to GitHub repositories, and "
        "will be treated as 'closed' instead."
    ),
)
@click.option(
    "--prefix",
    type=str,
    default="+ ",
    help="Prefix to use for each merge/pull request in the output, default is '+ '.",
)
@click.pass_context
def pulls(ctx, stale_days, state, prefix):
    updated_after = datetime.now() - timedelta(days=stale_days)
    try:
        for mr in ctx.obj.pulls(
            state=states.PullState[state.upper()],
            updated_after=updated_after
        ):
            click.echo(f"{prefix}{mr}")
    except Exception as e:
        logger.error("Error fetching merge requests: %s", e)
        click.echo("Failed to fetch merge requests.")
        ctx.exit(1)


@cli.command()
@click.option(
    "-s",
    "--state",
    type=click.Choice(["open", "closed"], case_sensitive=False),
    default="open",
    help="Filter milestones by state: open, closed, default is open.",
)
@click.option(
    "-d",
    "--stale-days",
    type=int,
    default=30,
    help=(
        "Number of days to consider a milestone "
        "stale and ignore it, default is 30 days."
    ),
)
@click.option(
    "--prefix",
    type=str,
    default="+ ",
    help="Prefix to use for each milestone in the output, default is '+ '.",
)
@click.option(
    "--indent",
    type=int,
    default=4,
    help="Number of spaces to indent milestone issues, default is 4.",
)
@click.option(
    "-t",
    "--strike-through",
    is_flag=True,
    help="Use strike-through formatting for issues.",
)
@click.option(
    "--no-issues",
    is_flag=True,
    help="Do not list issues under each milestone.",
)
@click.pass_context
def milestones(ctx, state, stale_days, prefix, indent, strike_through, no_issues):
    updated_after = datetime.now() - timedelta(days=stale_days)
    wraps = "~~" if strike_through else ""
    try:
        for milestone in ctx.obj.milestones(
            state=states.MilestoneState[state.upper()],
            updated_after=updated_after
        ):
            click.echo(f"{prefix}{wraps}{milestone}{wraps}")
            if no_issues:
                continue

            for issue in milestone.issues:
                click.echo(f"{' ' * indent}{prefix}{wraps}{issue}{wraps}")
    except Exception as e:
        logger.error("Error fetching milestones: %s", e)
        click.echo("Failed to fetch milestones.")
        ctx.exit(1)


if __name__ == "__main__":
    cli()
