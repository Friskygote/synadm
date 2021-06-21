# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2021 Johannes Tiefenbacher
#
# synadm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# synadm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" CLI commands executing regular Matrix API calls
"""

import click
import sys

from synadm import cli
from click_option_group import optgroup, MutuallyExclusiveOptionGroup


@cli.root.group()
def matrix():
    """ Execute Matrix API calls.

    """


@matrix.command(name="raw")
@click.argument(
    "endpoint", type=str)
@click.option(
    "--method", "-m", type=click.Choice(["get", "post", "put", "delete"]),
    help="""The HTTP method used for the request.""",
    default="get", show_default=True)
@optgroup.group(
    "Data input",
    cls=MutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--data", "-d", type=str, default='{}', show_default=True,
    help="""The JSON string sent in the body of post, put and delete requests -
    provided as a string. Make sure to escape it from shell interpretation by
    using single quotes. E.g '{"key1": "value1", "key2": 123}'
    """)
@optgroup.option(
    "--data-file", "-f", type=click.File("rt"),
    show_default=True,
    help="""Read JSON data from file. To read from stdin use "-" as the
    filename argument.
    """)
@optgroup.group(
    "Matrix token",
    cls=MutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--token", "-t", type=str, envvar='MTOKEN', show_default=True,
    help="""Token used for Matrix authentication instead of the configured admin
    user's token. If --token (and --prompt) option is missing, the token is read
    from environment variable $MTOKEN instead. To make sure a user's token
    does not show up in system logs, don't provided it on the shell directly but
    set $MTOKEN by using shell command `read MTOKEN`.""")
@optgroup.option(
    "--prompt", "-p", is_flag=True, show_default=True,
    help="""Prompt for the token used for Matrix authentication. This option
    always overrides $MTOKEN.""")
@click.pass_obj
def raw_request_cmd(helper, endpoint, method, data, data_file, token, prompt):
    """ Execute a raw request to the Matrix API.

    The endpoint argument is the part of the URL _after_ the configured base URL
    and Matrix path (see `synadm config`). A simple get request would e.g like
    this: `synadm matrix raw client/versions`

    Use either --token or --prompt to provide a user's token and execute Matrix
    commands on their behalf. Respect the privacy of others! Be responsible!

    The precedence rules for token reading are:
    1. Interactive input using --prompt; 2. Set on CLI via --token string;
    3. Read from environment variable $MTOKEN; 4. Preconfigured admin token
    set in synadm's config file.
    """
    if prompt:
        token = click.prompt("Matrix token", type=str)

    if data_file:
        raw_request = helper.matrix_api.raw_request(
            endpoint,
            method,
            data_file.read(),
            token=token
        )
    else:
        raw_request = helper.matrix_api.raw_request(endpoint, method, data,
                                                    token=token)

    if helper.batch:
        if raw_request is None:
            raise SystemExit(1)
        helper.output(raw_request)
    else:
        if raw_request is None:
            click.echo("The Matrix API's response was empty or JSON data could "
                       "not be loaded.")
            raise SystemExit(1)
        else:
            helper.output(raw_request)
