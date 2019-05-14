###
#
# Lenovo Redfish examples - Manage power limit and redundancy
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
    """Create parameter for power limit and redundancy management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform power limit and redundancy management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_powerlimit_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_powerredundancy_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_powerlimit_subcmds2subparsers(subparsers, subcmdlist):
    if 'getpwrcap' in subcmdlist:
        # create the sub parser for the 'getpwrcap' sub command
        parser_getpwrcap = subparsers.add_parser('getpwrcap', help='use getpwrcap to get power capping limit information')
        parser_getpwrcap.set_defaults(func=subcmd_getpwrcap_main)
    
    if 'setpwrcap' in subcmdlist:
        # create the sub parser for the 'setpwrcap' sub command
        parser_setpwrcap = subparsers.add_parser('setpwrcap', help='use setpwrcap to set power capping limit information')
        subcmd_setpwrcap_add_parameter(parser_setpwrcap)
        parser_setpwrcap.set_defaults(func=subcmd_setpwrcap_main)


def add_powerredundancy_subcmds2subparsers(subparsers, subcmdlist):
    if 'getpwrredun' in subcmdlist:
        # create the sub parser for the 'getpwrredun' sub command
        parser_getpwrredun = subparsers.add_parser('getpwrredun', help='use getpwrredun to get power redundancy information')
        parser_getpwrredun.set_defaults(func=subcmd_getpwrredun_main)
    
    if 'setpwrredun' in subcmdlist:
        # create the sub parser for the 'setpwrredun' sub command
        parser_setpwrredun = subparsers.add_parser('setpwrredun', help='use setpwrredun to set power redundancy information')
        subcmd_setpwrredun_add_parameter(parser_setpwrredun)
        parser_setpwrredun.set_defaults(func=subcmd_setpwrredun_main)


def subcmd_setpwrcap_add_parameter(subparser):
    """Add parameter for setpwrcap sub command"""
    
    from lenovo_set_power_limit import add_helpmessage as setpwrcap_add_helpmessage
    setpwrcap_add_helpmessage(subparser)


def subcmd_setpwrredun_add_parameter(subparser):
    """Add parameter for setpwrredun sub command"""
    
    from lenovo_set_power_redundant import add_helpmessage as setpwrredun_add_helpmessage
    setpwrredun_add_helpmessage(subparser)


def subcmd_getpwrcap_main(args, parameter_info):
    """call sub script to perform the getpwrcap sub command"""
    
    from get_power_limit import get_power_limit
    result = get_power_limit(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setpwrcap_main(args, parameter_info):
    """call sub script to perform the setpwrcap sub command"""
    
    from lenovo_set_power_limit import set_power_limit
    result = set_power_limit(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.isenable, args.powerlimit)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getpwrredun_main(args, parameter_info):
    """call sub script to perform the getpwrredun sub command"""
    
    from get_power_redunant import get_power_redundant
    result = get_power_redundant(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setpwrredun_main(args, parameter_info):
    """call sub script to perform the setpwrredun sub command"""
    
    from lenovo_set_power_redundant import set_power_redundant
    result = set_power_redundant(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.rdpolicy)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getpwrcap', 'setpwrcap', 'getpwrredun', 'setpwrredun']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
