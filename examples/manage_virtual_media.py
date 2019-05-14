###
#
# Lenovo Redfish examples - Manage virtual media
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
    """Create parameter for virtual media management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform virtual media management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_vmedia_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_vmedia_subcmds2subparsers(subparsers, subcmdlist):
    if 'getvm' in subcmdlist:
        # create the sub parser for the 'getvm' sub command
        parser_getvm = subparsers.add_parser('getvm', help='use getvm to get mounted virtual media information')
        parser_getvm.set_defaults(func=subcmd_getvm_main)
        
    if 'mountfromnet' in subcmdlist:
        # create the sub parser for the 'mountfromnet' sub command
        parser_mountfromnet = subparsers.add_parser('mountfromnet', help='use mountfromnet to mount an ISO or IMG image file from a file server on network to the host as a DVD or USB drive')
        subcmd_mountfromnet_add_parameter(parser_mountfromnet)
        parser_mountfromnet.set_defaults(func=subcmd_mountfromnet_main)
    
    if 'mountoncard' in subcmdlist:
        # create the sub parser for the 'mountoncard' sub command
        parser_mountoncard = subparsers.add_parser('mountoncard', help='use mountoncard to upload an ISO or IMG image file to the BMC, and mount it to the host as a DVD or USB drive. The BMC storage space is restricted to 50MB in total')
        subcmd_mountoncard_add_parameter(parser_mountoncard)
        parser_mountoncard.set_defaults(func=subcmd_mountoncard_main)
        
    if 'umountfromnet' in subcmdlist:
        # create the sub parser for the 'umountfromnet' sub command
        parser_umountfromnet = subparsers.add_parser('umountfromnet', help='use umountfromnet to unmount the mounted virtual media from network')
        parser_umountfromnet.set_defaults(func=subcmd_umountfromnet_main)
        
    if 'umountoncard' in subcmdlist:
        # create the sub parser for the 'umountoncard' sub command
        parser_umountoncard = subparsers.add_parser('umountoncard', help='use umountoncard to unmount the mounted virtual media on card')
        subcmd_umountoncard_add_parameter(parser_umountoncard)
        parser_umountoncard.set_defaults(func=subcmd_umountoncard_main)


def subcmd_mountfromnet_add_parameter(subparser):
    """Add parameter for mountfromnet sub command"""
    
    from lenovo_mount_virtual_media_from_network import add_helpmessage as mountfromnet_add_helpmessage
    mountfromnet_add_helpmessage(subparser)


def subcmd_mountoncard_add_parameter(subparser):
    """Add parameter for mountoncard sub command"""
    
    from lenovo_mount_virtual_media_from_rdoc import add_helpmessage as mountoncard_add_helpmessage
    mountoncard_add_helpmessage(subparser)


def subcmd_umountoncard_add_parameter(subparser):
    """Add parameter for umountoncard sub command"""
    
    from lenovo_umount_virtual_media_from_rdoc import add_helpmessage as umountoncard_add_helpmessage
    umountoncard_add_helpmessage(subparser)


def subcmd_getvm_main(args, parameter_info):
    """call sub script to perform the getvm sub command"""
    
    from get_virtual_media import get_virtual_media
    result = get_virtual_media(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_mountfromnet_main(args, parameter_info):
    """call sub script to perform the mountfromnet sub command"""
    
    import configparser
    from lenovo_mount_virtual_media_from_network import mount_media_iso
    
    config_file = args.config
    config_ini_info = utils.read_config(config_file)
    # Add FileServerCfg parameter to config_ini_info
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    config_ini_info["fsprotocol"] = cfg.get('FileServerCfg', 'FSprotocol')
    config_ini_info["fsip"] = cfg.get('FileServerCfg', 'FSip')
    config_ini_info["fsusername"] = cfg.get('FileServerCfg', 'FSusername')
    config_ini_info["fspassword"] = cfg.get('FileServerCfg', 'FSpassword')
    config_ini_info["fsdir"] = cfg.get('FileServerCfg', 'FSdir')
    # Parse the added parameters
    parameter_info['isoname'] = args.isoname
    parameter_info['fsprotocol'] = args.fsprotocol
    parameter_info['fsip'] = args.fsip
    parameter_info['fsusername'] = args.fsusername
    parameter_info['fspassword'] = args.fspassword
    parameter_info['readonly'] = args.readonly
    parameter_info['fsdir'] = args.fsdir
    parameter_info['domain'] = args.domain
    parameter_info['options'] = args.options
    # The parameters in the configuration file are used when the user does not specify parameters
    for key in parameter_info:
        if not parameter_info[key]:
            if key in config_ini_info:
                parameter_info[key] = config_ini_info[key]
    
    result = mount_media_iso(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['fsprotocol'], parameter_info['fsip'], parameter_info['fsusername'], parameter_info['fspassword'], parameter_info['fsdir'], parameter_info['isoname'], parameter_info['readonly'], parameter_info['domain'], parameter_info['options'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_mountoncard_main(args, parameter_info):
    """call sub script to perform the mountoncard sub command"""
    
    import configparser
    from lenovo_mount_virtual_media_from_rdoc import mount_media_iso
    
    config_file = args.config
    config_ini_info = utils.read_config(config_file)
    # Add FileServerCfg parameter to config_ini_info
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    config_ini_info["fsprotocol"] = cfg.get('FileServerCfg', 'FSprotocol')
    config_ini_info["fsip"] = cfg.get('FileServerCfg', 'FSip')
    config_ini_info["fsusername"] = cfg.get('FileServerCfg', 'FSusername')
    config_ini_info["fspassword"] = cfg.get('FileServerCfg', 'FSpassword')
    config_ini_info["fsdir"] = cfg.get('FileServerCfg', 'FSdir')
    # Parse the added parameters
    parameter_info['fsprotocol'] = args.fsprotocol
    parameter_info['fsip'] = args.fsip
    parameter_info['fsusername'] = args.fsusername
    parameter_info['fspassword'] = args.fspassword
    parameter_info['readonly'] = args.readonly
    parameter_info['fsdir'] = args.fsdir
    parameter_info['isoname'] = args.isoname
    parameter_info['domain'] = args.domain
    parameter_info['options'] = args.options
    # The parameters in the configuration file are used when the user does not specify parameters
    for key in parameter_info:
        if not parameter_info[key]:
            if key in config_ini_info:
                parameter_info[key] = config_ini_info[key]
   
    result = mount_media_iso(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['fsprotocol'], parameter_info['fsip'], parameter_info['fsusername'], parameter_info['fspassword'], parameter_info['fsdir'], parameter_info['isoname'], parameter_info['readonly'], parameter_info['domain'], parameter_info['options'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_umountfromnet_main(args, parameter_info):
    """call sub script to perform the umountfromnet sub command"""
    
    from lenovo_umount_all_virtual_media_from_network import umount_media_iso
    result = umount_media_iso(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_umountoncard_main(args, parameter_info):
    """call sub script to perform the umountoncard sub command"""
    
    from lenovo_umount_virtual_media_from_rdoc import umount_media_iso
    result = umount_media_iso(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.isoname)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getvm', 'mountfromnet', 'mountoncard', 'umountfromnet', 'umountoncard']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
