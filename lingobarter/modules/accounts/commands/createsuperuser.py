# -*- coding: utf-8 -*-
import click
from mongoengine import DoesNotExist
from ..models import User, Role


@click.command()
@click.option('--name', help='Full name', prompt=True)
@click.option('--email', help='A valid email address', prompt=True)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
def cli(name, email, password):
    """Create a user with administrator permissions"""
    if all([name, email, password]):
        try:
            admin = Role.objects.get(name='admin')
        except DoesNotExist:
            admin = Role(name='admin')
            admin.save()
        user = User.createuser(name, email, password, roles=[admin])
    else:
        user = "Cant create the supersuser"

    click.echo(user)
