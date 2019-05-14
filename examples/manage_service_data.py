###
#
# Lenovo Redfish examples - Manage service data
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
    """Create parameter for service data management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform service data management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')
    
    add_servicedata_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_servicedata_subcmds2subparsers(subparsers, subcmdlist):
    if 'getffdc' in subcmdlist:
        # create the sub parser for the 'getffdc' sub command
        parser_getffdc = subparsers.add_parser('getffdc', help='use getffdc to export ffdc data')
        subcmd_getffdc_add_parameter(parser_getffdc)
        parser_getffdc.set_defaults(func=subcmd_getffdc_main)
    
    if 'gethealthreport' in subcmdlist:
        # create the sub parser for the 'gethealthreport' sub command
        parser_gethealthreport = subparsers.add_parser('gethealthreport', help='use gethealthreport to export health report')
        parser_gethealthreport.set_defaults(func=subcmd_gethealthreport_main)
    
    if 'getfailscreen' in subcmdlist:
        # create the sub parser for the 'getfailscreen' sub command
        parser_getfailscreen = subparsers.add_parser('getfailscreen', help='use getfailscreen to export OS failure screen')
        parser_getfailscreen.set_defaults(func=subcmd_getfailscreen_main)
    
    if 'getalldata' in subcmdlist:
        # create the sub parser for the 'getalldata' sub command
        parser_getalldata = subparsers.add_parser('getalldata', help='use getalldata to export ffdc data, health report and OS failure screen')
        parser_getalldata.set_defaults(func=subcmd_getalldata_main)


def subcmd_getffdc_add_parameter(subparser):
    """Add parameter for getffdc sub command"""
    
    from lenovo_export_ffdc_data import add_helpmessage as getffdc_add_helpmessage
    getffdc_add_helpmessage(subparser)


def subcmd_getffdc_main(args, parameter_info):
    """call sub script to perform the getffdc sub command"""
    
    from lenovo_export_ffdc_data import export_ffdc_data
    result = export_ffdc_data(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.exporturi, args.sftpuser, args.sftppwd)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stderr.write(result['msg'])
        sys.stderr.write('\n')


def subcmd_gethealthreport_main(args, parameter_info):
    """call sub script to perform the gethealthreport sub command"""
    
    from lenovo_export_health_report import export_health_report
    result = export_health_report(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stderr.write(result['msg'])
        sys.stderr.write('\n')


def subcmd_getfailscreen_main(args, parameter_info):
    """call sub script to perform the getfailscreen sub command"""
    
    from lenovo_export_lastest_os_failure_screen import export_latest_failure_screen
    result = export_latest_failure_screen(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stdout.write('No OS failure screen found.')
        sys.stderr.write('\n')


def subcmd_getalldata_main(args, parameter_info):
    """call sub script to perform the getalldata sub command"""
    
    from lenovo_export_ffdc_data import export_ffdc_data
    result = export_ffdc_data(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], None, None, None)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stderr.write(result['msg'])
        sys.stderr.write('\n')
        return
        
    from lenovo_export_health_report import export_health_report
    result = export_health_report(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stderr.write(result['msg'])
        sys.stderr.write('\n')
        return
        
    from lenovo_export_lastest_os_failure_screen import export_latest_failure_screen
    result = export_latest_failure_screen(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
        sys.stderr.write('\n')
    else:
        sys.stdout.write('No OS failure screen found.')
        sys.stderr.write('\n')


if __name__ == '__main__':    
    # Get parameters from config.ini and/or command line
    subcmd_list = ['getffdc', 'gethealthreport', 'getfailscreen', 'getalldata']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
