###
#
# Lenovo Redfish examples - Manage power action
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
    """Create parameter for power action management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform power action management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')

    add_poweraction_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_poweraction_subcmds2subparsers(subparsers, subcmdlist):
    if 'getsyspower' in subcmdlist:
        # create the sub parser for the 'getsyspower' sub command
        parser_getsyspower = subparsers.add_parser('getsyspower', help='use getsyspower to get system power state')
        parser_getsyspower.set_defaults(func=subcmd_getsyspower_main)
    
    if 'syspowerctl' in subcmdlist:
        # create the sub parser for the 'syspowerctl' sub command
        parser_syspowerctl = subparsers.add_parser('syspowerctl', help='use syspowerctl to control system power')
        subcmd_syspowerctl_add_parameter(parser_syspowerctl)
        parser_syspowerctl.set_defaults(func=subcmd_syspowerctl_main)
    
    if 'restartbmc' in subcmdlist:
        # create the sub parser for the 'restartbmc' sub command
        parser_restartbmc = subparsers.add_parser('restartbmc', help='use restartbmc to restart BMC')
        parser_restartbmc.set_defaults(func=subcmd_restartbmc_main)


def subcmd_syspowerctl_add_parameter(subparser):
    """Add parameter for syspowerctl sub command"""
    
    from set_reset_system import add_helpmessage as syspowerctl_add_helpmessage
    syspowerctl_add_helpmessage(subparser)


def subcmd_getsyspower_main(args, parameter_info):
    """call sub script to perform the getsyspower sub command"""
    
    syspower_info = {}
    from get_power_state import get_power_state
    result = get_power_state(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        syspower_info.update(result['entries'][0])
    else:
        sys.stderr.write(result['msg'])
        return

    from get_system_reset_types import get_reset_types
    result = get_reset_types(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        syspower_info.update(result['entries'][0])
    else:
        sys.stderr.write(result['msg'])
        return
        
    sys.stdout.write(json.dumps(syspower_info, sort_keys=True, indent=2))


def subcmd_syspowerctl_main(args, parameter_info):
    """call sub script to perform the syspowerctl sub command"""
    
    from set_reset_system import set_reset_system
    result = set_reset_system(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.resettype)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_restartbmc_main(args, parameter_info):
    """call sub script to perform the restartbmc sub command"""
    
    from restart_bmc import restart_manager
    result = restart_manager(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getsyspower', 'syspowerctl', 'restartbmc']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
