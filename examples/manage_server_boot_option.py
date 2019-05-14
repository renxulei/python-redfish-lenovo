###
#
# Lenovo Redfish examples - Manage server boot option
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
    """Create parameter for server boot option management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform server boot option management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_biosboot_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_biosboot_subcmds2subparsers(subparsers, subcmdlist):
    if 'getsysboot' in subcmdlist:
        # create the sub parser for the 'getsysboot' sub command
        parser_getsysboot = subparsers.add_parser('getsysboot', help='use getsysboot to get server boot option information')
        parser_getsysboot.set_defaults(func=subcmd_getsysboot_main)
    
    if 'setbootmode' in subcmdlist:
        # create the sub parser for the 'setbootmode' sub command
        parser_setbootmode = subparsers.add_parser('setbootmode', help='use setbootmode to set server boot mode')
        subcmd_setbootmode_add_parameter(parser_setbootmode)
        parser_setbootmode.set_defaults(func=subcmd_setbootmode_main)
    
    if 'setbootorder' in subcmdlist:
        # create the sub parser for the 'setbootorder' sub command
        parser_setbootorder = subparsers.add_parser('setbootorder', help='use setbootorder to change bios boot order')
        subcmd_setbootorder_add_parameter(parser_setbootorder)
        parser_setbootorder.set_defaults(func=subcmd_setbootorder_main)
    
    if 'setbootonce' in subcmdlist:
        # create the sub parser for the 'setbootonce' sub command
        parser_setbootonce = subparsers.add_parser('setbootonce', help='use setbootonce to set one time boot option')
        subcmd_setbootonce_add_parameter(parser_setbootonce)
        parser_setbootonce.set_defaults(func=subcmd_setbootonce_main)


def subcmd_setbootmode_add_parameter(subparser):
    """Add parameter for setbootmode sub command"""
    
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--legacy', action='store_true', help='set bootmode to legacy')
    group.add_argument('--uefi', action='store_true', help='set bootmode to uefi')


def subcmd_setbootorder_add_parameter(subparser):
    """Add parameter for setbootorder sub command"""
    
    from lenovo_set_bios_boot_order import add_helpmessage as setbootorder_add_helpmessage
    setbootorder_add_helpmessage(subparser)


def subcmd_setbootonce_add_parameter(subparser):
    """Add parameter for setbootonce sub command"""
    
    from set_server_boot_once import add_helpmessage as setbootonce_add_helpmessage
    setbootonce_add_helpmessage(subparser)


def subcmd_getsysboot_main(args, parameter_info):
    """call sub script to perform the getsysboot sub command"""
    
    boot_info = {}
    from get_bios_bootmode import get_boot_mode
    result = get_boot_mode(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        boot_info['BootMode'] = result['msg']['BootSourceOverrideMode']
    else:
        sys.stderr.write(result['msg'])
        return
        
    from get_server_boot_once import get_server_boot_once
    result = get_server_boot_once(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        boot_info['BootOnce'] = result['entries'][0]['BootSourceOverrideTarget']
    else:
        sys.stderr.write(result['msg'])
        return
        
    from lenovo_get_bios_boot_order import get_bios_boot_order
    result = get_bios_boot_order(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    if result['ret'] is True:
        del result['ret']
        boot_info['BootOrder'] = result['entries'][0]
    else:
        sys.stderr.write(result['msg'])
        return
        
    sys.stdout.write(json.dumps(boot_info, sort_keys=True, indent=2))


def subcmd_setbootmode_main(args, parameter_info):
    """call sub script to perform the setbootmode sub command"""
    
    from set_bios_bootmode_legacy import set_bios_bootmode_legacy
    from set_bios_bootmode_uefi import set_bios_bootmode_uefi
    
    if args.legacy:
        result = set_bios_bootmode_legacy(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    else:
        result = set_bios_bootmode_uefi(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setbootorder_main(args, parameter_info):
    """call sub script to perform the setbootorder sub command"""
    
    from lenovo_set_bios_boot_order import set_bios_boot_order
    result = set_bios_boot_order(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.bootorder)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setbootonce_main(args, parameter_info):
    """call sub script to perform the setbootonce sub command"""
    
    from set_server_boot_once import set_server_boot_once
    result = set_server_boot_once(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'], args.bootsource)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getsysboot', 'setbootmode', 'setbootorder', 'setbootonce']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
