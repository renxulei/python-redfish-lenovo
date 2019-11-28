###
#
# Lenovo Redfish examples - Hold session for the time specified
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


def hold_session(ip, login_account, login_password, session_time):
    """Get power state    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params session_time: the time during which session will be held, default is 30 seconds 
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
        result = {'ret': False, 'msg': "Error_message: %s. Please check if username, password and IP are correct" % repr(e)}
        return result
    
    try:
        sessionkey = REDFISH_OBJ.get_session_key()
        sessionlocation = REDFISH_OBJ.get_session_location()
        # Wait seconds so that the session can be kept for testing GetSessions or ClearSessions
        time.sleep(session_time)
        REDFISH_OBJ.logout()
        result = {'ret': True, 'msg': "Log out normally, hold %s seconds totally. sessionkey is %s, location is %s." % (session_time, sessionkey, sessionlocation)}
    except Exception as e:
        result = {'ret': True, 'msg': "Session has been deleted. Message: %s." % repr(e)}
    finally:
        return result


def add_helpmessage(parser):
    parser.add_argument('--time', type=str, required=False, help='Input the time during which session will be held, default is 30 seconds')


def add_parameter():
    """Add time parameter"""
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
    
    try:
        session_time = int(parameter_info['time'])
    except:
        session_time = 30
    
    # hold session
    result = hold_session(ip, login_account, login_password, session_time)
    if result['ret'] is True:
        sys.stdout.write(result['msg'] + '\n')
    else:
        sys.stderr.write(result['msg'] + '\n')
