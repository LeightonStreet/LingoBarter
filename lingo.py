#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import click
from lingobarter import create_app
from lingobarter.core.db import db
from lingobarter.ext.blueprints import blueprint_commands

# create lingobarter application
app = create_app()
# expose celery for celery worker
celery = app.celery

# configure logging format
if app.config.get("LOGGER_ENABLED"):
    logging.basicConfig(
        level=getattr(logging, app.config.get("LOGGER_LEVEL", "DEBUG")),
        format=app.config.get(
            "LOGGER_FORMAT",
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'),
        datefmt=app.config.get("LOGGER_DATE_FORMAT", '%d.%m %H:%M:%S')
    )


@click.group()
def core_cmd():
    """ Core commands """
    pass


@core_cmd.command()
@click.option('--ipython/--no-ipython', default=True)
def shell(ipython):
    """Runs a Python shell with LingoBarter context
    :param ipython:
    """
    import code
    import readline
    import rlcompleter
    _vars = globals()
    _vars.update(locals())
    _vars.update(dict(app=app, db=db))
    readline.set_completer(rlcompleter.Completer(_vars).complete)
    readline.parse_and_bind("tab: complete")
    if ipython is True:
        from IPython import start_ipython
        start_ipython(argv=[], user_ns=_vars)
    else:
        bash = code.InteractiveConsole(_vars)
        bash.interact()


@core_cmd.command()
def check():
    """Prints app status"""
    from pprint import pprint
    print("Extensions.")
    pprint(app.extensions)
    print("Modules.")
    pprint(app.blueprints)
    print("App.")
    return app


@core_cmd.command()
@click.option(
    '-f',
    '--filename',
    help='Fixtures JSON path',
    default='./etc/fixtures/initial_data.json')
@click.option('-b', '--baseurl', help='base url to use', default=None)
def populate(filename, baseurl=None):
    """Populate the database with sample data
    :param filename:
    :param baseurl:
    """
    from lingobarter.utils.populate import Populate
    Populate(db, filepath=filename, baseurl=baseurl, app=app)()


@core_cmd.command()
@click.option(
    '-f',
    '--filename',
    help='Fixtures JSON path',
    default='./etc/fixtures/initial_data.json')
@click.option('-b', '--baseurl', help='base url to use', default=None)
def populate_reset(filename, baseurl=None):
    """De-Populate the database with sample data
    :param filename:
    :param baseurl:
    """
    from lingobarter.utils.populate import Populate
    Populate(db, filepath=filename, baseurl=baseurl, app=app).reset()


@core_cmd.command()
def showconfig():
    """Print all config variables"""
    from pprint import pprint
    print("Config.")
    pprint(dict(app.config.store))


@core_cmd.command()
@click.option('--reloader/--no-reloader', default=True)
@click.option('--debug/--no-debug', default=True)
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5000)
def runserver(reloader, debug, host, port):
    """Run the Flask development server i.e. app.run()
    normally, we will use command line, ./lingo.py runserver to start
    lingobarter.
    :param reloader:
    :param debug:
    :param host:
    :param port:
    """
    app.run(use_reloader=reloader, debug=debug, host=host, port=port)


help_text = """
    Subcommands are loaded from the module/commands folder dynamically.
    The module name and command file inside commands folder will be
    used for compose the command name.

    (For a file in the path 'mymodule/commands/sayhi.py' the command
    name will be 'mymodule_sayhi')

    The click command function must be named 'cli'.

    Example:

    \b
    import click
    @click.command()
    def cli():
        click.echo("Do whatever you want")
    """
manager = click.CommandCollection(help=help_text)
manager.add_source(core_cmd)
manager.add_source(blueprint_commands(app))

if __name__ == '__main__':
    with app.app_context():
        manager()
