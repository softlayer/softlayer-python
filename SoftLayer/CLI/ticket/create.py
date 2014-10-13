"""Create a support ticket"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import ticket

import click


@click.command()
@click.argument('identifier')
@click.option('--title', required=True, help="The title of the ticket")
@click.option('--subject-id',
              required=True,
              help="""The subject id to use for the ticket,
 issue 'sl ticket subjects' to get the list""")
@click.option('--body', help="The ticket body")
@environment.pass_env
def cli(env, identifier, title, subject_id, body):
    """Create a support ticket"""
    mgr = SoftLayer.TicketManager(env.client)

    if body is None:
        body = click.edit('\n\n' + ticket.TEMPLATE_MSG)

    created_ticket = mgr.create_ticket(title=title,
                                       body=body,
                                       subject=subject_id)
    return get_ticket_results(mgr, created_ticket['id'])
