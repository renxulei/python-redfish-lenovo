###
#
# Lenovo Redfish examples - Manage utilization
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
    """Create parameter for utilization management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform utilization management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_utilization_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_utilization_subcmds2subparsers(subparsers, subcmdlist):
    if 'getfan' in subcmdlist:
        # create the sub parser for the 'getfan' sub command
        parser_getfan = subparsers.add_parser('getfan', help='use getfan to get fan information')
        parser_getfan.set_defaults(func=subcmd_getfan_main)
    
    if 'gettemp' in subcmdlist:
        # create the sub parser for the 'gettemp' sub command
        parser_gettemp = subparsers.add_parser('gettemp', help='use gettemp to get temperature information')
        parser_gettemp.set_defaults(func=subcmd_gettemp_main)
    
    if 'getvolt' in subcmdlist:
        # create the sub parser for the 'getvolt' sub command
        parser_getvolt = subparsers.add_parser('getvolt', help='use getvolt to get voltage information')
        parser_getvolt.set_defaults(func=subcmd_getvolt_main)

    if 'getpower' in subcmdlist:
        # create the sub parser for the 'getpower' sub command
        parser_getpower = subparsers.add_parser('getpower', help='use getpower to get power metrics information')
        parser_getpower.set_defaults(func=subcmd_getpower_main)


def subcmd_getfan_main(args, parameter_info):
    """call sub script to perform the getfan sub command"""
    
    from get_fan_inventory import get_fan_inventory
    result = get_fan_inventory(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_gettemp_main(args, parameter_info):
    """call sub script to perform the gettemp sub command"""
    
    from get_temperatures_inventory import get_temperatures_inventory
    result = get_temperatures_inventory(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getvolt_main(args, parameter_info):
    """call sub script to perform the getvolt sub command"""
    
    from get_volt_inventory import get_volt_inventory
    result = get_volt_inventory(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getpower_main(args, parameter_info):
    """call sub script to perform the getpower sub command"""
    
    from get_power_metrics import get_power_metrics
    result = get_power_metrics(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getfan', 'gettemp', 'getvolt', 'getpower']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
