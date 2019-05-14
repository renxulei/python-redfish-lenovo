###
#
# Lenovo Redfish examples - Manage BMC configuration
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
    """Create parameter for BMC configuration management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform BMC configuration management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_bmcuser_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmctime_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmcnet_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmccfg_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmcssh_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmcldap_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_bmcuser_subcmds2subparsers(subparsers, subcmdlist):
    if 'listuser' in subcmdlist:
        # create the sub parser for the 'listuser' sub command
        parser_listuser = subparsers.add_parser('listuser', help='use listuser to get BMC user account information')
        parser_listuser.set_defaults(func=subcmd_listuser_main)
        
    if 'createuser' in subcmdlist:
        # create the sub parser for the 'createuser' sub command
        parser_createuser = subparsers.add_parser('createuser', help='use createuser to add a new BMC user')
        subcmd_createuser_add_parameter(parser_createuser)
        parser_createuser.set_defaults(func=subcmd_createuser_main)
    
    if 'deleteuser' in subcmdlist:
        # create the sub parser for the 'deleteuser' sub command
        parser_deleteuser = subparsers.add_parser('deleteuser', help='use deleteuser to remove an existing BMC user')
        subcmd_deleteuser_add_parameter(parser_deleteuser)
        parser_deleteuser.set_defaults(func=subcmd_deleteuser_main)
    
    if 'updatepasswd' in subcmdlist:
        # create the sub parser for the 'updatepasswd' sub command
        parser_updatepasswd = subparsers.add_parser('updatepasswd', help='use updatepasswd to update password of an existing BMC user')
        subcmd_updatepasswd_add_parameter(parser_updatepasswd)
        parser_updatepasswd.set_defaults(func=subcmd_updatepasswd_main)
    
    if 'updateauthority' in subcmdlist:
        # create the sub parser for the 'updateauthority' sub command
        parser_updateauthority = subparsers.add_parser('updateauthority', help='use updateauthority to update authority of an existing BMC user')
        subcmd_updateauthority_add_parameter(parser_updateauthority)
        parser_updateauthority.set_defaults(func=subcmd_updateauthority_main)


def subcmd_createuser_add_parameter(subparser):
    """Add parameter for createuser sub command"""
    
    from create_bmc_user import add_helpmessage as create_add_helpmessage
    create_add_helpmessage(subparser)


def subcmd_deleteuser_add_parameter(subparser):
    """Add parameter for deleteuser sub command"""
    
    from delete_bmc_user import add_helpmessage as delete_add_helpmessage
    delete_add_helpmessage(subparser)


def subcmd_updatepasswd_add_parameter(subparser):
    """Add parameter for updatepasswd sub command"""
    
    from update_user_password import add_helpmessage as updatepasswd_add_helpmessage
    updatepasswd_add_helpmessage(subparser)


def subcmd_updateauthority_add_parameter(subparser):
    """Add parameter for updateauthority sub command"""
    
    from lenovo_update_bmc_user_privileges import add_helpmessage as updateauthority_add_helpmessage
    updateauthority_add_helpmessage(subparser)


def subcmd_listuser_main(args, parameter_info):
    """call sub script to perform the listuser sub command"""
    
    from lenovo_get_bmc_user_accounts import get_bmc_user_accounts
    result = get_bmc_user_accounts(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_createuser_main(args, parameter_info):
    """call sub script to perform the createuser sub command"""
    
    from create_bmc_user import create_bmc_user
    result = create_bmc_user(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.newusername, args.newuserpasswd, args.authority)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_deleteuser_main(args, parameter_info):
    """call sub script to perform the deleteuser sub command"""
    
    from delete_bmc_user import delete_bmc_user
    result = delete_bmc_user(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_updatepasswd_main(args, parameter_info):
    """call sub script to perform the updatepasswd sub command"""
    
    from update_user_password import update_user_password
    result = update_user_password(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username, args.newpasswd)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_updateauthority_main(args, parameter_info):
    """call sub script to perform the updateauthority sub command"""
    
    from lenovo_update_bmc_user_privileges import update_bmc_user_privileges
    result = update_bmc_user_privileges(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username, args.authority)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def add_bmctime_subcmds2subparsers(subparsers, subcmdlist):
    if 'gettime' in subcmdlist:
        # create the sub parser for the 'gettime' sub command
        parser_gettime = subparsers.add_parser('gettime', help='use gettime to get bmc time information')
        parser_gettime.set_defaults(func=subcmd_gettime_main)
    
    if 'settimezone' in subcmdlist:
        # create the sub parser for the 'settimezone' sub command
        parser_settimezone = subparsers.add_parser('settimezone', help='use settimezone to set bmc timezone')
        subcmd_settimezone_add_parameter(parser_settimezone)
        parser_settimezone.set_defaults(func=subcmd_settimezone_main)
    
    if 'getntp' in subcmdlist:
        # create the sub parser for the 'getntp' sub command
        parser_getntp = subparsers.add_parser('getntp', help='use getntp to get ntp server address')
        parser_getntp.set_defaults(func=subcmd_getntp_main)
    
    if 'setntp' in subcmdlist:
        # create the sub parser for the 'setntp' sub command
        parser_setntp = subparsers.add_parser('setntp', help='use setntp to set ntp server address')
        subcmd_setntp_add_parameter(parser_setntp)
        parser_setntp.set_defaults(func=subcmd_setntp_main)
    
    if 'synctime' in subcmdlist:
        # create the sub parser for the 'synctime' sub command
        parser_synctime = subparsers.add_parser('synctime', help='use synctime to sync BMC time with host or ntp server')
        subcmd_synctime_add_parameter(parser_synctime)
        parser_synctime.set_defaults(func=subcmd_synctime_main)


def subcmd_settimezone_add_parameter(subparser):
    """Add parameter for settimezone sub command"""
    
    from lenovo_set_bmc_timezone import add_helpmessage as settimezone_add_helpmessage
    settimezone_add_helpmessage(subparser)


def subcmd_setntp_add_parameter(subparser):
    """Add parameter for setntp sub command"""
    
    from set_bmc_ntp import add_helpmessage as setntp_add_helpmessage
    setntp_add_helpmessage(subparser)


def subcmd_synctime_add_parameter(subparser):
    """Add parameter for synctime sub command"""
    
    from lenovo_sync_bmc_time import add_helpmessage as synctime_add_helpmessage
    synctime_add_helpmessage(subparser)


def subcmd_gettime_main(args, parameter_info):
    """call sub script to perform the gettime sub command"""
    
    from lenovo_get_bmc_time import lenovo_get_bmc_time as get_bmc_time
    result = get_bmc_time(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_settimezone_main(args, parameter_info):
    """call sub script to perform the settimezone sub command"""
    
    from lenovo_set_bmc_timezone import lenovo_set_bmc_timezone as set_bmc_timezone
    result = set_bmc_timezone(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.timezone)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getntp_main(args, parameter_info):
    """call sub script to perform the getntp sub command"""
    
    from get_bmc_ntp import get_bmc_ntp
    result = get_bmc_ntp(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setntp_main(args, parameter_info):
    """call sub script to perform the setntp sub command"""
    
    from set_bmc_ntp import set_manager_ntp
    result = set_manager_ntp(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.ntpserver, args.enabled)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_synctime_main(args, parameter_info):
    """call sub script to perform the synctime sub command"""
    
    from lenovo_sync_bmc_time import lenovo_sync_bmc_time
    result = lenovo_sync_bmc_time(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.method)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def add_bmcnet_subcmds2subparsers(subparsers, subcmdlist):
    if 'getnetprotocol' in subcmdlist:
        # create the sub parser for the 'getnetprotocol' sub command
        parser_getnetprotocol = subparsers.add_parser('getnetprotocol', help='use getnetprotocol to get BMC network protocol information')
        parser_getnetprotocol.set_defaults(func=subcmd_getnetprotocol_main)
    
    if 'setnetprotocol' in subcmdlist:
        # create the sub parser for the 'setnetprotocol' sub command
        parser_setnetprotocol = subparsers.add_parser('setnetprotocol', help='use setnetprotocol to set BMC network protocol information')
        subcmd_setnetprotocol_add_parameter(parser_setnetprotocol)
        parser_setnetprotocol.set_defaults(func=subcmd_setnetprotocol_main)
    
    if 'getipv4' in subcmdlist:
        # create the sub parser for the 'getipv4' sub command
        parser_getipv4 = subparsers.add_parser('getipv4', help='use getipv4 to get BMC IPv4 address information')
        parser_getipv4.set_defaults(func=subcmd_getipv4_main)
    
    if 'setipv4' in subcmdlist:
        # create the sub parser for the 'setipv4' sub command
        parser_setipv4 = subparsers.add_parser('setipv4', help='use setipv4 to set BMC IPv4 address information')
        subcmd_setipv4_add_parameter(parser_setipv4)
        parser_setipv4.set_defaults(func=subcmd_setipv4_main)
    
    if 'setvlanid' in subcmdlist:
        # create the sub parser for the 'setvlanid' sub command
        parser_setvlanid = subparsers.add_parser('setvlanid', help='use setvlanid to set BMC vlan id information')
        subcmd_setvlanid_add_parameter(parser_setvlanid)
        parser_setvlanid.set_defaults(func=subcmd_setvlanid_main)


def subcmd_setnetprotocol_add_parameter(subparser):
    """Add parameter for setnetprotocol sub command"""
    
    from lenovo_set_networkprotocol import add_helpmessage as setnetprotocol_add_helpmessage
    setnetprotocol_add_helpmessage(subparser)


def subcmd_setipv4_add_parameter(subparser):
    """Add parameter for setipv4 sub command"""
    
    from lenovo_set_bmc_IPv4 import add_helpmessage as setipv4_add_helpmessage
    setipv4_add_helpmessage(subparser)


def subcmd_setvlanid_add_parameter(subparser):
    """Add parameter for setvlanid sub command"""
    
    from set_bmc_vlanid import add_helpmessage as setvlanid_add_helpmessage
    setvlanid_add_helpmessage(subparser)


def subcmd_getnetprotocol_main(args, parameter_info):
    """call sub script to perform the getnetprotocol sub command"""
    
    from get_networkprotocol_info import get_service_port
    result = get_service_port(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setnetprotocol_main(args, parameter_info):
    """call sub script to perform the setnetprotocol sub command"""
    
    from lenovo_set_networkprotocol import set_service_port
    result = set_service_port(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.service, args.enabled, args.port)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getipv4_main(args, parameter_info):
    """call sub script to perform the getipv4 sub command"""
    
    from lenovo_get_bmc_IPv4 import get_ipv4
    result = get_ipv4(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setipv4_main(args, parameter_info):
    """call sub script to perform the setipv4 sub command"""
    
    from lenovo_set_bmc_IPv4 import set_ipv4
    result = set_ipv4(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.method, args.ipv4address, args.netmask, args.gateway)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setvlanid_main(args, parameter_info):
    """call sub script to perform the setvlanid sub command"""
    
    from set_bmc_vlanid import set_manager_vlanid
    result = set_manager_vlanid(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.vlanid, args.vlanenable)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def add_bmccfg_subcmds2subparsers(subparsers, subcmdlist):
    if 'exportbmccfg' in subcmdlist:
        # create the sub parser for the 'exportbmccfg' sub command
        parser_exportbmccfg = subparsers.add_parser('exportbmccfg', help='use exportbmccfg to backup BMC configuration')
        subcmd_exportbmccfg_add_parameter(parser_exportbmccfg)
        parser_exportbmccfg.set_defaults(func=subcmd_exportbmccfg_main)
    
    if 'importbmccfg' in subcmdlist:
        # create the sub parser for the 'importbmccfg' sub command
        parser_importbmccfg = subparsers.add_parser('importbmccfg', help='use importbmccfg to restore BMC configuration from a backup configuration file')
        subcmd_importbmccfg_add_parameter(parser_importbmccfg)
        parser_importbmccfg.set_defaults(func=subcmd_importbmccfg_main)
    
    if 'defaultbmccfg' in subcmdlist:
        # create the sub parser for the 'defaultbmccfg' sub command
        parser_defaultbmccfg = subparsers.add_parser('defaultbmccfg', help='use defaultbmccfg to reset BMC configuration to default')
        parser_defaultbmccfg.set_defaults(func=subcmd_defaultbmccfg_main)


def subcmd_exportbmccfg_add_parameter(subparser):
    """Add parameter for exportbmccfg sub command"""
    
    from lenovo_bmc_config_backup import add_helpmessage as exportbmccfg_add_helpmessage
    exportbmccfg_add_helpmessage(subparser)


def subcmd_importbmccfg_add_parameter(subparser):
    """Add parameter for importbmccfg sub command"""
    
    from lenovo_bmc_config_restore import add_helpmessage as importbmccfg_add_helpmessage
    importbmccfg_add_helpmessage(subparser)


def subcmd_exportbmccfg_main(args, parameter_info):
    """call sub script to perform the exportbmccfg sub command"""
    
    from lenovo_bmc_config_backup import lenovo_bmc_config_backup
    result = lenovo_bmc_config_backup(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.backuppasswd, args.backupfile)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_importbmccfg_main(args, parameter_info):
    """call sub script to perform the importbmccfg sub command"""
    
    from lenovo_bmc_config_restore import lenovo_config_restore
    result = lenovo_config_restore(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.backuppasswd, args.backupfile)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_defaultbmccfg_main(args, parameter_info):
    """call sub script to perform the defaultbmccfg sub command"""
    
    from lenovo_set_bmc_config_default import lenovo_set_bmc_config_default
    result = lenovo_set_bmc_config_default(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def add_bmcssh_subcmds2subparsers(subparsers, subcmdlist):
    if 'getsshkey' in subcmdlist:
        # create the sub parser for the 'getsshkey' sub command
        parser_getsshkey = subparsers.add_parser('getsshkey', help='use getsshkey to get ssh public key for specified BMC user')
        subcmd_getsshkey_add_parameter(parser_getsshkey)
        parser_getsshkey.set_defaults(func=subcmd_getsshkey_main)
    
    if 'importsshkey' in subcmdlist:
        # create the sub parser for the 'importsshkey' sub command
        parser_importsshkey = subparsers.add_parser('importsshkey', help='use importsshkey to import ssh public key for specified BMC user')
        subcmd_importsshkey_add_parameter(parser_importsshkey)
        parser_importsshkey.set_defaults(func=subcmd_importsshkey_main)
    
    if 'removesshkey' in subcmdlist:
        # create the sub parser for the 'removesshkey' sub command
        parser_removesshkey = subparsers.add_parser('removesshkey', help='use removesshkey to remove ssh public key for specified BMC user')
        subcmd_removesshkey_add_parameter(parser_removesshkey)
        parser_removesshkey.set_defaults(func=subcmd_removesshkey_main)


def subcmd_getsshkey_add_parameter(subparser):
    """Add parameter for getsshkey sub command"""
    
    from lenovo_get_ssh_pubkey import add_helpmessage as getsshkey_add_helpmessage
    getsshkey_add_helpmessage(subparser)


def subcmd_importsshkey_add_parameter(subparser):
    """Add parameter for importsshkey sub command"""
    
    from lenovo_import_ssh_pubkey import add_helpmessage as importsshkey_add_helpmessage
    importsshkey_add_helpmessage(subparser)


def subcmd_removesshkey_add_parameter(subparser):
    """Add parameter for removesshkey sub command"""
    
    from lenovo_remove_ssh_pubkey import add_helpmessage as removesshkey_add_helpmessage
    removesshkey_add_helpmessage(subparser)


def subcmd_getsshkey_main(args, parameter_info):
    """call sub script to perform the getsshkey sub command"""
    
    from lenovo_get_ssh_pubkey import get_ssh_pubkey
    result = get_ssh_pubkey(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_importsshkey_main(args, parameter_info):
    """call sub script to perform the importsshkey sub command"""
    
    from lenovo_import_ssh_pubkey import import_ssh_pubkey
    dict_opcommand  = {}
    if args.sshpubkey:
        dict_opcommand["sshpubkey"] = args.sshpubkey
    else:
        dict_opcommand["sshpubkeyfile"] = args.sshpubkeyfile
    result = import_ssh_pubkey(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username, dict_opcommand)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_removesshkey_main(args, parameter_info):
    """call sub script to perform the removesshkey sub command"""
    
    from lenovo_remove_ssh_pubkey import remove_ssh_pubkey
    result = remove_ssh_pubkey(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.username)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def add_bmcldap_subcmds2subparsers(subparsers, subcmdlist):
    if 'getlogon' in subcmdlist:
        # create the sub parser for the 'getlogon' sub command
        parser_getlogon = subparsers.add_parser('getlogon', help='use getlogon to get BMC logon authentication mode information')
        parser_getlogon.set_defaults(func=subcmd_getlogon_main)
    
    if 'setlogon' in subcmdlist:
        # create the sub parser for the 'setlogon' sub command
        parser_setlogon = subparsers.add_parser('setlogon', help='use setlogon to set BMC logon authentication mode information')
        subcmd_setlogon_add_parameter(parser_setlogon)
        parser_setlogon.set_defaults(func=subcmd_setlogon_main)
    
    if 'getldap' in subcmdlist:
        # create the sub parser for the 'getldap' sub command
        parser_getldap = subparsers.add_parser('getldap', help='use getldap to get ntp server address')
        parser_getldap.set_defaults(func=subcmd_getldap_main)
    
    if 'setldap' in subcmdlist:
        # create the sub parser for the 'setldap' sub command
        parser_setldap = subparsers.add_parser('setldap', help='use setldap to set ntp server address')
        subcmd_setldap_add_parameter(parser_setldap)
        parser_setldap.set_defaults(func=subcmd_setldap_main)


def subcmd_setlogon_add_parameter(subparser):
    """Add parameter for setlogon sub command"""
    
    from lenovo_set_logon_mode import add_helpmessage as setlogon_add_helpmessage
    setlogon_add_helpmessage(subparser)


def subcmd_setldap_add_parameter(subparser):
    """Add parameter for setldap sub command"""
    
    from lenovo_set_ldap_server import add_helpmessage as setldap_add_helpmessage
    setldap_add_helpmessage(subparser)


def subcmd_getlogon_main(args, parameter_info):
    """call sub script to perform the getlogon sub command"""
    
    from lenovo_get_logon_mode import get_authentication_method
    result = get_authentication_method(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setlogon_main(args, parameter_info):
    """call sub script to perform the setlogon sub command"""
    
    from lenovo_set_logon_mode import set_authentication_method
    result = set_authentication_method(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.method)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getldap_main(args, parameter_info):
    """call sub script to perform the getldap sub command"""
    
    from lenovo_get_ldap_information import get_ldap_info
    result = get_ldap_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_setldap_main(args, parameter_info):
    """call sub script to perform the setldap sub command"""
    
    from lenovo_set_ldap_server import set_ldap_info
    result = set_ldap_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.method, args.ldapserver, args.port, args.domainname, args.binding_method, args.clientdn, args.clientpwd,
                           args.rootdn, args.uid_search_attribute, args.group_filter, args.group_search_attribute, args.login_permission_attribute, args.role_base_security, args.servername)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['listuser', 'createuser', 'deleteuser', 'updatepasswd', 'updateauthority', 'gettime', 'settimezone', 'getntp', 'setntp', 'synctime', 'getnetprotocol', 'setnetprotocol', 'getipv4', 'setipv4', 'setvlanid', 'exportbmccfg', 'importbmccfg', 'defaultbmccfg', 'getsshkey', 'importsshkey', 'removesshkey', 'getlogon', 'setlogon', 'getldap', 'setldap']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
