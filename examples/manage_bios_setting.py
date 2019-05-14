###
#
# Lenovo Redfish examples - Manage bios settting
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
    """Create parameter for bios setting management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform bios setting via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_biossetting_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_biossetting_subcmds2subparsers(subparsers, subcmdlist):
    if 'getbiosallattr' in subcmdlist:
        # create the sub parser for the 'getbiosallattr' sub command
        parser_getbiosallattr = subparsers.add_parser('getbiosallattr', help='use getbiosallattr to get bios all attributes')
        subcmd_getbiosallattr_add_parameter(parser_getbiosallattr)
        parser_getbiosallattr.set_defaults(func=subcmd_getbiosallattr_main)
    
    if 'getbiosattr' in subcmdlist:
        # create the sub parser for the 'getbiosattr' sub command
        parser_getbiosattr = subparsers.add_parser('getbiosattr', help='use getbiosattr to get one specified bios attribute')
        subcmd_getbiosattr_add_parameter(parser_getbiosattr)
        parser_getbiosattr.set_defaults(func=subcmd_getbiosattr_main)
    
    if 'setbiosattr' in subcmdlist:
        # create the sub parser for the 'setbiosattr' sub command
        parser_setbiosattr = subparsers.add_parser('setbiosattr', help='use setbiosattr to set one specified bios attribute')
        subcmd_setbiosattr_add_parameter(parser_setbiosattr)
        parser_setbiosattr.set_defaults(func=subcmd_setbiosattr_main)
    
    if 'setbiospasswd' in subcmdlist:
        # create the sub parser for the 'setbiospasswd' sub command
        parser_setbiospasswd = subparsers.add_parser('setbiospasswd', help='use setbiospasswd to set bios password')
        subcmd_setbiospasswd_add_parameter(parser_setbiospasswd)
        parser_setbiospasswd.set_defaults(func=subcmd_setbiospasswd_main)
    
    if 'resetbiosdefault' in subcmdlist:
        # create the sub parser for the 'resetbiosdefault' sub command
        parser_resetbiosdefault = subparsers.add_parser('resetbiosdefault', help='use resetbiosdefault to reset bios setting to default')
        parser_resetbiosdefault.set_defaults(func=subcmd_resetbiosdefault_main)


def subcmd_getbiosallattr_add_parameter(subparser):
    """Add parameter for getbiosallattr sub command"""
    
    from get_all_bios_attribute import add_helpmessage as getbiosallattr_add_helpmessage
    getbiosallattr_add_helpmessage(subparser)


def subcmd_getbiosattr_add_parameter(subparser):
    """Add parameter for getbiosattr sub command"""
    
    from get_bios_attribute import add_helpmessage as getbiosattr_add_helpmessage
    getbiosattr_add_helpmessage(subparser)


def subcmd_setbiosattr_add_parameter(subparser):
    """Add parameter for setbiosattr sub command"""
    
    from set_bios_attribute import add_helpmessage as setbiosattr_add_helpmessage
    setbiosattr_add_helpmessage(subparser)


def subcmd_setbiospasswd_add_parameter(subparser):
    """Add parameter for setbiospasswd sub command"""
    
    from set_bios_password import add_helpmessage as setbiospasswd_add_helpmessage
    setbiospasswd_add_helpmessage(subparser)


def subcmd_getbiosallattr_main(args, parameter_info):
    """call sub script to perform the getbiosallattr sub command"""
    
    from get_all_bios_attribute import get_bios_attribute
    result = get_bios_attribute(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.bios)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['attributes'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getbiosattr_main(args, parameter_info):
    """call sub script to perform the getbiosattr sub command"""
    
    from get_bios_attribute import get_bios_attribute
    result = get_bios_attribute(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.name)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setbiosattr_main(args, parameter_info):
    """call sub script to perform the setbiosattr sub command"""
    
    from set_bios_attribute import set_bios_attribute
    result = set_bios_attribute(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.name, args.value)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])



def subcmd_setbiospasswd_main(args, parameter_info):
    """call sub script to perform the setbiospasswd sub command"""
    
    from set_bios_password import set_bios_password
    result = set_bios_password(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.name, args.biospasswd)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_resetbiosdefault_main(args, parameter_info):
    """call sub script to perform the resetbiosdefault sub command"""
    
    from reset_bios_default import reset_bios_default
    result = reset_bios_default(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getbiosallattr', 'getbiosattr', 'setbiosattr', 'setbiospasswd', 'resetbiosdefault']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
