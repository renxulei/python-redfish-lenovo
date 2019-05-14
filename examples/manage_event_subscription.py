###
#
# Lenovo Redfish examples - Manage event subscription
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
    """Create parameter for event subscription management"""
    
    parser = utils.create_common_parameter_list("This tool can be used to perform event subscription management via Redfish.")
    subparsers = parser.add_subparsers(help='sub-command help')

    add_eventsubs_subcmds2subparsers(subparsers, supported_subcmd_list)
    
    ret_args = parser.parse_args()
    return ret_args


def add_eventsubs_subcmds2subparsers(subparsers, subcmdlist):
    if 'geteventsubs' in subcmdlist:
        # create the sub parser for the 'geteventsubs' sub command
        parser_geteventsubs = subparsers.add_parser('geteventsubs', help='use geteventsubs to get event subscription information')
        parser_geteventsubs.set_defaults(func=subcmd_geteventsubs_main)
    
    if 'addeventsubs' in subcmdlist:
        # create the sub parser for the 'addeventsubs' sub command
        parser_addeventsubs = subparsers.add_parser('addeventsubs', help='use addeventsubs to add a new event subscription')
        subcmd_addeventsubs_add_parameter(parser_addeventsubs)
        parser_addeventsubs.set_defaults(func=subcmd_addeventsubs_main)
    
    if 'deleventsubs' in subcmdlist:
        # create the sub parser for the 'deleventsubs' sub command
        parser_deleventsubs = subparsers.add_parser('deleventsubs', help='use deleventsubs to delete specified event subscription')
        subcmd_deleventsubs_add_parameter(parser_deleventsubs)
        parser_deleventsubs.set_defaults(func=subcmd_deleventsubs_main)
    
    if 'sendevent' in subcmdlist:
        # create the sub parser for the 'sendevent' sub command
        parser_sendevent = subparsers.add_parser('sendevent', help='use sendevent to trigger BMC to send a test event for event subscription verification')
        subcmd_sendevent_add_parameter(parser_sendevent)
        parser_sendevent.set_defaults(func=subcmd_sendevent_main)


def subcmd_addeventsubs_add_parameter(subparser):
    """Add parameter for addeventsubs sub command"""
    
    from add_event_subscriptions import add_helpmessage as addeventsubs_add_helpmessage
    addeventsubs_add_helpmessage(subparser)


def subcmd_deleventsubs_add_parameter(subparser):
    """Add parameter for deleventsubs sub command"""
    
    from del_event_subscriptions import add_helpmessage as deleventsubs_add_helpmessage
    deleventsubs_add_helpmessage(subparser)


def subcmd_sendevent_add_parameter(subparser):
    """Add parameter for sendevent sub command"""
    
    from send_test_event import add_helpmessage as sendevent_add_helpmessage
    sendevent_add_helpmessage(subparser)


def subcmd_geteventsubs_main(args, parameter_info):
    """call sub script to perform the geteventsubs sub command"""
    
    from get_event_subscriptions import get_event_subscriptions
    result = get_event_subscriptions(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'])
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_addeventsubs_main(args, parameter_info):
    """call sub script to perform the addeventsubs sub command"""
    
    from add_event_subscriptions import add_event_subscriptions
    result = add_event_subscriptions(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.destination, args.eventtypes, args.context)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_deleventsubs_main(args, parameter_info):
    """call sub script to perform the deleventsubs sub command"""
    
    from del_event_subscriptions import del_event_subscriptions
    dict_option = {}
    if args.destination:
        dict_option["destination"] = args.destination
    elif args.id:
        dict_option["id"] = args.id
    else:
        dict_option["all"] = "all"
    result = del_event_subscriptions(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], dict_option)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


def subcmd_sendevent_main(args, parameter_info):
    """call sub script to perform the sendevent sub command"""
    
    from send_test_event import add_event_subscriptions
    result = add_event_subscriptions(parameter_info['ip'], parameter_info['user'], parameter_info['passwd'], args.eventid, args.message, args.severity)
    
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    subcmd_list = ['geteventsubs', 'addeventsubs', 'deleventsubs', 'sendevent']
    parsed_args = create_parameter(subcmd_list)
    parsed_parameter_info = utils.parse_parameter(parsed_args)
    
    # Call related function to perform sub command
    if 'func' in parsed_args and parsed_args.func:
        parsed_args.func(parsed_args, parsed_parameter_info)
    else:
        sys.stderr.write('error: too few arguments. use -h to get help information')
