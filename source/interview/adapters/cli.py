import click


def create_cli(alembic_run_cmd, MessageBus):

    @click.group()
    def cli():
        pass

    @cli.command(context_settings={"ignore_unknown_options": True})
    @click.argument('alembic_args', nargs=-1, type=click.UNPROCESSED)
    def alembic(alembic_args):
        alembic_run_cmd(*alembic_args)

    return cli
