###
#
# Lenovo Redfish examples - Manage system log
#
# Copyright Notice:
#
# Copyright 2018 Lenovo Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
###


import sys, os
import redfish
import json
import lenovo_utils as utils


def create_parameter(supported_subcmd_list):
    """Create parameter for system event log management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform system log management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_systemlog_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_systemlog_subcmds2subparsers(subparsers, subcmdlist):
    if 'getlog' in subcmdlist:
        # create the sub parser for the 'getlog' sub command
        parser_getlog = subparsers.add_parser('getlog', help='use getlog to get system log')
        subcmd_getlog_add_parameter(parser_getlog)
        parser_getlog.set_defaults(func=subcmd_getlog_main)
        
    if 'clearlog' in subcmdlist:
        # create the sub parser for the 'clearlog' sub command
        parser_clearlog = subparsers.add_parser('clearlog', help='use clearlog to clear system log')
        parser_clearlog.set_defaults(func=subcmd_clearlog_main)


def subcmd_getlog_add_parameter(subparser):
    """Add parameter for getlog sub command"""
    
    from get_system_log import add_helpmessage as getlog_add_helpmessage
    getlog_add_helpmessage(subparser)


def subcmd_getlog_main(args, parameter_info):
    """call sub script to perform the getlog sub command"""
    
    from get_system_log import get_system_log, filter_system_log
    result = get_system_log(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], None)
    
    if result['ret'] is True:
        filtered_entries = filter_system_log(result['entries'], args.severity, args.date)
        sys.stdout.write(json.dumps(filtered_entries, sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_clearlog_main(args, parameter_info):
    """call sub script to perform the clearlog sub command"""
    
    from clear_system_log import clear_system_log
    result = clear_system_log(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], None)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getlog', 'clearlog']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
