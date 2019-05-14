###
#
# Lenovo Redfish examples - Manage chassis indicator LED
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
    """Create parameter for chassis indicator LED management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform chassis indicator LED management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_indicatorled_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_indicatorled_subcmds2subparsers(subparsers, subcmdlist):
    if 'getled' in subcmdlist:
        # create the sub parser for the 'getled' sub command
        parser_getled = subparsers.add_parser('getled', help='use getled to get chassis indicator LED light status')
        parser_getled.set_defaults(func=subcmd_getled_main)
    
    if 'setled' in subcmdlist:
        # create the sub parser for the 'setled' sub command
        parser_setled = subparsers.add_parser('setled', help='use setled to set chassis indicator LED light status (Off, Lit, Blinking)')
        subcmd_setled_add_parameter(parser_setled)
        parser_setled.set_defaults(func=subcmd_setled_main)


def subcmd_setled_add_parameter(subparser):
    """Add parameter for setled sub command"""
    
    from set_chassis_indicator_led import add_helpmessage as setled_add_helpmessage
    setled_add_helpmessage(subparser)


def subcmd_getled_main(args, parameter_info):
    """call sub script to perform the getled sub command"""
    
    from get_chassis_indicator_led import get_chassis_indicator_led
    result = get_chassis_indicator_led(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setled_main(args, parameter_info):
    """call sub script to perform the setled sub command"""
    
    from set_chassis_indicator_led import set_chassis_indicator_led
    result = set_chassis_indicator_led(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.ledstatus)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getled', 'setled']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
