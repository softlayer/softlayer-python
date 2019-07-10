"""Manage LBaaS health checks."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils
from pprint import pprint as pp 

@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Manage LBaaS health checks."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    lb = mgr.get_lb(identifier)
    table = lbaas_table(lb)

    env.fout(table)
