###
#
# Lenovo Redfish examples - Manage server location and asset tag
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
    """Create parameter for server location and asset tag management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform server location and asset tag management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_location_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_assettag_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_location_subcmds2subparsers(subparsers, subcmdlist):
    if 'getlocation' in subcmdlist:
        # create the sub parser for the 'getlocation' sub command
        parser_getlocation = subparsers.add_parser('getlocation', help='use getlocation to get server location and contact information')
        parser_getlocation.set_defaults(func=subcmd_getlocation_main)
    
    if 'setlocation' in subcmdlist:
        # create the sub parser for the 'setlocation' sub command
        parser_setlocation = subparsers.add_parser('setlocation', help='use setlocation to set server location and contact information')
        subcmd_setlocation_add_parameter(parser_setlocation)
        parser_setlocation.set_defaults(func=subcmd_setlocation_main)


def add_assettag_subcmds2subparsers(subparsers, subcmdlist):
    if 'getassettag' in subcmdlist:
        # create the sub parser for the 'getassettag' sub command
        parser_getassettag = subparsers.add_parser('getassettag', help='use getassettag to get server asset tag')
        parser_getassettag.set_defaults(func=subcmd_getassettag_main)
    
    if 'setassettag' in subcmdlist:
        # create the sub parser for the 'setassettag' sub command
        parser_setassettag = subparsers.add_parser('setassettag', help='use setassettag to set server asset tag')
        subcmd_setassettag_add_parameter(parser_setassettag)
        parser_setassettag.set_defaults(func=subcmd_setassettag_main)


def subcmd_setlocation_add_parameter(subparser):
    """Add parameter for setlocation sub command"""
    
    from lenovo_set_location import add_helpmessage as setlocation_add_helpmessage
    setlocation_add_helpmessage(subparser)


def subcmd_setassettag_add_parameter(subparser):
    """Add parameter for setassettag sub command"""
    
    from set_server_asset_tag import add_helpmessage as setassettag_add_helpmessage
    setassettag_add_helpmessage(subparser)


def subcmd_getlocation_main(args, parameter_info):
    """call sub script to perform the getlocation sub command"""
    
    from lenovo_get_location import get_location
    result = get_location(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setlocation_main(args, parameter_info):
    """call sub script to perform the setlocation sub command"""
    
    from lenovo_set_location import lenovo_set_location
    result = lenovo_set_location(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.contact, args.rack_name, args.room_no, args.building, args.lowest_u, args.address)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getassettag_main(args, parameter_info):
    """call sub script to perform the getassettag sub command"""
    
    from get_system_inventory import get_system_info
    result = get_system_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'][0]['AssetTag'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setassettag_main(args, parameter_info):
    """call sub script to perform the setassettag sub command"""
    
    from set_server_asset_tag import set_server_asset_tag
    result = set_server_asset_tag(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.assettag)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getlocation', 'setlocation', 'getassettag', 'setassettag']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
