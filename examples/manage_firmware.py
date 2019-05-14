###
#
# Lenovo Redfish examples - Manage firmware
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
    """Create parameter for firmware management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform firmware management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_firmware_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_firmware_subcmds2subparsers(subparsers, subcmdlist):
    if 'getfw' in subcmdlist:
        # create the sub parser for the 'getfw' sub command
        parser_getfw = subparsers.add_parser('getfw', help='use getfw to get firmware information')
        parser_getfw.set_defaults(func=subcmd_getfw_main)
    
    if 'updatefw' in subcmdlist:
        # create the sub parser for the 'updatefw' sub command
        parser_updatefw = subparsers.add_parser('updatefw', help='use updatefw to update one specified firmware')
        subcmd_updatefw_add_parameter(parser_updatefw)
        parser_updatefw.set_defaults(func=subcmd_updatefw_main)


def subcmd_updatefw_add_parameter(subparser):
    """Add parameter for updatefw sub command"""
    
    from update_firmware import add_helpmessage as updatefw_add_helpmessage
    updatefw_add_helpmessage(subparser)


def subcmd_getfw_main(args, parameter_info):
    """call sub script to perform the getfw sub command"""
    
    from get_fw_inventory import get_fw_inventory
    result = get_fw_inventory(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])

    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['fw_version_detail'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])



def subcmd_updatefw_main(args, parameter_info):
    """call sub script to perform the updatefw sub command"""
    
    from update_firmware import update_fw
    result = update_fw(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.imageurl, args.targets, args.protocol)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getfw', 'updatefw']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
