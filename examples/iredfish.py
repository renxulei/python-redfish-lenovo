###
#
# Lenovo Redfish examples - A tool interface to manage all
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
import json
import lenovo_utils as utils
import redfish


def create_parameter(supported_subcmd_list):
    """Create parameter for inventory management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform server management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_inventory_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_poweraction_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_systemlog_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmcuser_subcmds2subparsers(subparsers, supported_subcmd_list)
    add_bmctime_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_inventory_subcmds2subparsers(subparsers, subcmdlist):
    if 'getinventories' in subcmdlist:
        # create the sub parser for the 'getinventories' sub command
        parser_getinventories = subparsers.add_parser('getinventories', help='use getinventories to get all inventory information')
        parser_getinventories.set_defaults(func=subcmd_getinventories_main)
        
    if 'getsystem' in subcmdlist:
        # create the sub parser for the 'getsystem' sub command
        parser_getsystem = subparsers.add_parser('getsystem', help='use getsystem to get system inventory information')
        parser_getsystem.set_defaults(func=subcmd_getsystem_main)
        
    if 'getcpu' in subcmdlist:
        # create the sub parser for the 'getcpu' sub command
        parser_getcpu = subparsers.add_parser('getcpu', help='use getcpu to get processor inventory information')
        parser_getcpu.set_defaults(func=subcmd_getcpu_main)
        
    if 'getmemory' in subcmdlist:
        # create the sub parser for the 'getmemory' sub command
        parser_getmemory = subparsers.add_parser('getmemory', help='use getmemory to get memory inventory information')
        parser_getmemory.set_defaults(func=subcmd_getmemory_main)
        
    if 'getstorage' in subcmdlist:
        # create the sub parser for the 'getstorage' sub command
        parser_getstorage = subparsers.add_parser('getstorage', help='use getstorage to get storage inventory information')
        parser_getstorage.set_defaults(func=subcmd_getstorage_main)
        
    if 'getnic' in subcmdlist:
        # create the sub parser for the 'getnic' sub command
        parser_getnic = subparsers.add_parser('getnic', help='use getnic to get nic inventory information')
        parser_getnic.set_defaults(func=subcmd_getnic_main)
        
    if 'getpsu' in subcmdlist:
        # create the sub parser for the 'getpsu' sub command
        parser_getpsu = subparsers.add_parser('getpsu', help='use getpsu to get powersupply inventory information')
        parser_getpsu.set_defaults(func=subcmd_getpsu_main)
        
    if 'getbmc' in subcmdlist:
        # create the sub parser for the 'getbmc' sub command
        parser_getbmc = subparsers.add_parser('getbmc', help='use getbmc to get BMC inventory information')
        parser_getbmc.set_defaults(func=subcmd_getbmc_main)


def subcmd_getinventories_main(args, parameter_info, subcmdlist):
    """call sub script to perform the getinventories sub command"""
    sys.stdout.write("{")
    sys.stdout.write("\n\"SystemInventory\":\n")
    subcmd_getsystem_main(args, parameter_info)
    if 'getcpu' in subcmdlist:
        sys.stdout.write(",\n\n\"CpuInventory\":\n")
        subcmd_getcpu_main(args, parameter_info)
    if 'getmemory' in subcmdlist:
        sys.stdout.write(",\n\n\"MemoryInventory\":\n")
        subcmd_getmemory_main(args, parameter_info)
    if 'getstorage' in subcmdlist:
        sys.stdout.write(",\n\n\"StorageInventory\":\n")
        subcmd_getstorage_main(args, parameter_info)
    if 'getnic' in subcmdlist:
        sys.stdout.write(",\n\n\"NicInventory\":\n")
        subcmd_getnic_main(args, parameter_info)
    if 'getpsu' in subcmdlist:
        sys.stdout.write(",\n\n\"PsuInventory\":\n")
        subcmd_getpsu_main(args, parameter_info)
    if 'getbmc' in subcmdlist:
        sys.stdout.write(",\n\n\"BmcInventory\":\n")
        subcmd_getbmc_main(args, parameter_info)
    sys.stdout.write("\n}")


def subcmd_getsystem_main(args, parameter_info):
    """call sub script to perform the getsystem sub command"""
    
    from get_system_inventory import get_system_info
    result = get_system_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getcpu_main(args, parameter_info):
    """call sub script to perform the getcpu sub command"""
    
    from get_cpu_inventory import get_cpu_info
    result = get_cpu_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getmemory_main(args, parameter_info):
    """call sub script to perform the getmemory sub command"""
    
    from get_memory_inventory import get_memory_inventory
    result = get_memory_inventory(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getstorage_main(args, parameter_info):
    """call sub script to perform the getstorage sub command"""
    
    from get_storage_inventory import get_storage_info
    result = get_storage_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getnic_main(args, parameter_info):
    """call sub script to perform the getnic sub command"""
    
    from get_nic_inventory import get_network_info
    result = get_network_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getpsu_main(args, parameter_info):
    """call sub script to perform the getpsu sub command"""
    
    from get_psu_inventory import get_psu_info
    result = get_psu_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entry_details'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_getbmc_main(args, parameter_info):
    """call sub script to perform the getbmc sub command"""
    
    from get_bmc_inventory import get_bmc_info
    result = get_bmc_info(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], parameter_info['sysid'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


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


def add_systemlog_subcmds2subparsers(subparsers, subcmdlist):
    if 'getlog' in subcmdlist:
        # create the sub parser for the 'getlog' sub command
        parser_getlog = subparsers.add_parser('getlog', help='use getlog to get system log')
        subcmd_getlog_add_parameter(parser_getlog)
        parser_getlog.set_defaults(func=subcmd_getlog_main)
        
    if 'clearlog' in subcmdlist:
        # create the sub parser for the 'clearlog' sub command
        parser_clearlog = subparsers.add_parser('clearlog', help='use clearlog to clear system log')
        parser_clearlog.set_defaults(func=subcmd_clearlog_main)


def subcmd_getlog_add_parameter(subparser):
    """Add parameter for getlog sub command"""
    
    from get_system_log import add_helpmessage as getlog_add_helpmessage
    getlog_add_helpmessage(subparser)


def subcmd_getlog_main(args, parameter_info):
    """call sub script to perform the getlog sub command"""
    
    from get_system_log import get_system_log, filter_system_log
    result = get_system_log(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], None)
    
    if result['ret'] is True:
        filtered_entries = filter_system_log(result['entries'], args.severity, args.date)
        sys.stdout.write(json.dumps(filtered_entries, sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_clearlog_main(args, parameter_info):
    """call sub script to perform the clearlog sub command"""
    
    from clear_system_log import clear_system_log
    result = clear_system_log(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], None)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


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


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getinventories', 'getsystem', 'getcpu', 'getmemory', 'getstorage', 'getnic', 'getpsu', 'getbmc', 'getsyspower', 'syspowerctl', 'restartbmc', 'getlog', 'clearlog', 'listuser', 'createuser', 'deleteuser', 'updatepasswd', 'updateauthority', 'gettime', 'settimezone', 'getntp', 'setntp', 'synctime']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        if parsed_args.func is subcmd_getinventories_main:
            parsed_args.func(parsed_args, parsed_parameter_info, subcmd_list)
        else:
            parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
