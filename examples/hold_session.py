###
#
# Lenovo Redfish examples - Get power state and hold session for the time specified
#
# Copyright Notice:
#
# Copyright 2019 Lenovo Corporation
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
import json
import redfish
import time
import lenovo_utils as utils


def get_power_state(ip, login_account, login_password, system_id, session_time):
    """Get power state    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params system_id: ComputerSystem instance id(None: first instance, All: all instances)
    :type system_id: None or string
    :params session_time: the time during which session will be held, default is 60 seconds 
    :type session_time: int
    :returns: returns power state when succeeded or error message when failed
    """
    result = {}
    login_host = "https://" + ip
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                             password=login_password, default_prefix='/redfish/v1')
        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result
    
    # Wait seconds so that the session can be kept for testing GetSessions or ClearSessions
    time.sleep(session_time)
    
    # GET the ComputerSystem resource
    power_details = []
    system = utils.get_system_url("/redfish/v1", system_id, REDFISH_OBJ)
    if not system:
        result = {'ret': False, 'msg': "This system id is not exist or system member is None"}
        REDFISH_OBJ.logout()
        return result
    for i in range(len(system)):
        system_url = system[i]
        response_system_url = REDFISH_OBJ.get(system_url, None)
        if response_system_url.status == 200:
            # Get the response
            power_state = {}
            # Get the PowerState property
            PowerState = response_system_url.dict["PowerState"]
            power_state["PowerState"] = PowerState
            power_details.append(power_state)
        else:
            result = {'ret': False, 'msg': "response_system_url Error code %s" % response_system_url.status}
            REDFISH_OBJ.logout()
            return result

    result['ret'] = True
    result['entries'] = power_details
    # Logout of the current session
    REDFISH_OBJ.logout()
    return result


def add_helpmessage(parser):
    parser.add_argument('--time', type=str, required=False, help='Input the time during which session will be held, default is 60 seconds')


def add_parameter():
    """Add set chassis indicator led parameter"""
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info['time'] = args.time
    return parameter_info


if __name__ == '__main__':
    # Get connection and session time info from the parameters user specified
    parameter_info = add_parameter()
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    system_id = parameter_info['sysid']
    
    try:
        session_time = int(parameter_info['time'])
    except:
        session_time = 60
    
    #print(parameter_info)
    
    # Get power state and check result
    result = get_power_state(ip, login_account, login_password, system_id, session_time)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])
