#!/usr/bin/env python
from __future__ import print_function
import sys
import ast
import argparse
import globus_sdk
import os
import logging
import time

assert (sys.version_info >= (2, 7) or
        sys.version_info.major >= 3), "Python version 2.7 or 3+ needed"
try:
    import ConfigParser as configparser
except:
    import configparser


def parse_config(config_file):
    """
    Have configparser open the config file
    and generate a dict mapping sections
    and options in a dict(dict())

    Args:
        config_file: Path to config file

    Returns:
        config_dict: Dict(dict()) of the format
                     config[section_header][variable_name]=
                     variable_value
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_file)
    config_dict = config_options_dict(config)
    return config_dict


def config_options_dict(config):
    """
    Parsing config file

    Args:
        config: Python config parser object

    Returns:
        config_dict: A dict(dict()) with the different sections of the
                     config file and the literal values of the
                     configuraton objects
    """
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            val = config.get(section, option)
            try:
                val = ast.literal_eval(val)
            except Exception:
                pass
            config_dict[section][option] = val
    return config_dict


def get_globus_tokens(config):
    """
    Get Globus authenication tokens
    """
    client = globus_sdk.NativeAppAuthClient(
        config["globus"]["client_id"])
    client.oauth2_start_flow(refresh_tokens=True)
    token_file = os.path.join(os.path.expandvars("$HOME"), ".spt_transfer")
    if os.path.exists(token_file):
        # If we got the refresh tokens, use them!
        with open(token_file, "rt") as f:
            for line in f:
                transfer_refresh_token = line.rstrip("\n")
        return client, None, None, transfer_refresh_token
    else:
        # If we dont have refresh tokens... get some!
        authorize_url = client.oauth2_get_authorize_url()
        print('Please go to this URL and login: {0}'.format(authorize_url))
        # this is to work on Python2 and Python3 -- you can just
        # use raw_input() or input() for your specific version
        get_input = getattr(__builtins__, 'raw_input', input)
        auth_code = get_input(
            'Please enter the code you get after login here: ').strip()
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)

        globus_auth_data = token_response.by_resource_server['auth.globus.org']
        globus_transfer_data = token_response.by_resource_server[
            'transfer.api.globus.org']

        auth_token = globus_auth_data[
            'access_token']
        transfer_token = globus_transfer_data[
            'access_token']
        transfer_refresh_token = globus_transfer_data[
            'refresh_token']
        with open(token_file, "wt") as f:
            f.write(transfer_refresh_token)
        return client, auth_token, transfer_token, transfer_refresh_token