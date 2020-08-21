###
#
# Lenovo Redfish examples - Lenovo Redfish Tool
#
# Copyright Notice:
#
# Copyright 2020 Lenovo Corporation
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

import sys
import argparse
import os
import json

from utils import *
from utils import add_common_parameter
from utils import parse_common_parameter
import lenovo_system_client
import lenovo_manager_client
import lenovo_chassis_client
import lenovo_update_client


def usage():
    lenovo_system_client.usage()
    lenovo_manager_client.usage()
    lenovo_chassis_client.usage()
    lenovo_update_client.usage()

def main(argv):
    """Lenovo Redfish client's main"""

    argget = argparse.ArgumentParser(description="Lenovo Redfish Tool")
    add_common_parameter(argget)
    
    subcommand_parsers = argget.add_subparsers(dest='subcommand_name', help='all subcommands')
    lenovo_system_client.add_sub_parameter(subcommand_parsers)
    lenovo_manager_client.add_sub_parameter(subcommand_parsers)
    lenovo_chassis_client.add_sub_parameter(subcommand_parsers)
    lenovo_update_client.add_sub_parameter(subcommand_parsers)

    # Parse the parameters
    args = argget.parse_args()

    if args.subcommand_name in lenovo_system_client.cmd_list.keys():
        result = lenovo_system_client.run_subcommand(args)
    elif args.subcommand_name in lenovo_manager_client.cmd_list.keys():
        result = lenovo_manager_client.run_subcommand(args)
    elif args.subcommand_name in lenovo_chassis_client.cmd_list.keys():
        result = lenovo_chassis_client.run_subcommand(args)
    elif args.subcommand_name in lenovo_update_client.cmd_list.keys():
        result = lenovo_update_client.run_subcommand(args)
    else:
        usage()
        result = {'ret': False, 'msg': "Please specify correct subcommand."}

    if 'msg' in result:
        print(result['msg'])
    if 'entries' in result:
        print(json.dumps(result['entries'], sort_keys=True, indent=2))
    if result['ret'] == False:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":

    main(sys.argv)