###
#
# Lenovo Redfish examples - Set power redundant
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

import sys
import redfish
import json
import lenovo_utils as utils

def set_power_redundant(ip, login_account, login_password,redundancy_policy):
    """Set power redundant
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :returns: returns Set power redundant result when succeeded or error message when failed
        """
    #paramater check
    list = ["NonRedundant","Redundant"]
    if redundancy_policy not in list:
        result = {'ret':False,'msg':"rdpolicy scope must in [NonRedundant, Redundant],Please check help info"}
        return result

    result = {}
    login_host = "https://" + ip

    # Connect using the BMC address, account name, and password
    # Create a REDFISH object
    REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')

    # Login into the server and create a session
    try:
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result
    # Get ServiceBase resource
    try:
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
        # Get response_base_url
        if response_base_url.status == 200:
            chassis_url = response_base_url.dict['Chassis']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                '/redfish/v1', response_base_url.status, error_message)}
            return result
        response_chassis_url = REDFISH_OBJ.get(chassis_url, None)
        if response_chassis_url.status == 200:
            #Set power redundant
            for request in response_chassis_url.dict['Members']:
                request_url = request['@odata.id']
                response_url = REDFISH_OBJ.get(request_url, None)
                if response_url.status == 200:
                    # if chassis is not normal skip it
                    if "ComputerSystems" not in response_url.dict["Links"]:
                        continue
                    power_url = response_url.dict["Power"]['@odata.id']
                    response_power_url = REDFISH_OBJ.get(power_url, None)
                    if response_power_url.status == 200:
                        if redundancy_policy == "NonRedundant":
                            redundancy_policy = "NonRedundantWithThrottling"
                        else:
                            redundancy_policy = "RedundantWithThrottling"
                        parameter = {"Redundancy": [{"Oem":{"Lenovo":{"PowerRedundancySettings":{"PowerRedundancyPolicy":redundancy_policy}}}}]}
                        response_redundant_set_url = REDFISH_OBJ.patch(power_url, body=parameter)
                        if response_redundant_set_url.status == 200:
                            result = {"ret":True,"msg":"set redundant successfully"}
                            return result
                        else:
                            error_message = utils.get_extended_error(response_redundant_set_url)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                                power_url, response_redundant_set_url.status, error_message)}
                            return result
                    else:
                        error_message = utils.get_extended_error(response_power_url)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                            power_url, response_power_url.status, error_message)}
                        return result
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result
        else:
            error_message = utils.get_extended_error(response_chassis_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                chassis_url, response_chassis_url.status, error_message)}
            return result
    except Exception as e:
        result = {'ret': False, 'msg': 'exception msg %s' % e}
        return result
    finally:
        REDFISH_OBJ.logout()

def add_helpmessage(argget):
    help_str = "Input the redundancy policy you want to set,value scope only in [NonRedundant,Redundant]."
    help_str += "Redundant:The server is guaranteed to continue to remain operational with the loss of one power supply feed."
    help_str += "NonRedundant:The server is not guaranteed to remain operational with the loss of a power supply feed. The system may throttle if a power supply fails in an attempt to stay powered up and continue running."
    argget.add_argument('--rdpolicy', type=str, required=True, help=help_str)


def add_parameter():
    """Add Set power redundant parameter"""
    parameter_info = {}
    #syncmethod
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["rdpolicy"] = args.rdpolicy
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    redundancy_policy = parameter_info["rdpolicy"]

    # Set power redundant and check result
    result = set_power_redundant(ip, login_account, login_password,redundancy_policy)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])