###
#
# Lenovo Redfish examples - Get IPv4 server
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
import traceback

def get_ipv4(ip, login_account, login_password):
    """Get bmc IPv4 information
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :returns: returns get ipv4 result when succeeded or error message when failed
        """

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
            managers_url = response_base_url.dict['Managers']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                '/redfish/v1', response_base_url.status, error_message)}
            return result

        response_managers_url = REDFISH_OBJ.get(managers_url, None)
        if response_managers_url.status == 200:
            for request in response_managers_url.dict['Members']:
                request_url = request['@odata.id']
                response_url = REDFISH_OBJ.get(request_url, None)
                #Get Ethernet Interfaces url
                if response_url.status == 200:
                    interfaces_url = response_url.dict["EthernetInterfaces"]['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result
                # Get the NIC url form the interfaces url response
                response_interfaces_url = REDFISH_OBJ.get(interfaces_url, None)
                if response_interfaces_url.status == 200:
                    member_list = response_interfaces_url.dict["Members"]
                else:
                    error_message = utils.get_extended_error(response_interfaces_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        interfaces_url, response_interfaces_url.status, error_message)}
                    return result

                # Get the IPv4 information from the nic url response
                for member in member_list:
                    member_url = member["@odata.id"]
                    ipv4_dict = {}
                    if "NIC" in member_url:
                        response_nic_url = REDFISH_OBJ.get(member_url, None)
                        if response_nic_url.status == 200:
                            ipv4_address = response_nic_url.dict["IPv4Addresses"]
                            ipv4_addressAssignedby = response_nic_url.dict["Oem"]["Lenovo"]["IPv4AddressAssignedby"]
                            ipv4_dict["IPv4Addresses"] = ipv4_address
                            ipv4_dict["IPv4AddressAssignedby"] = ipv4_addressAssignedby
                            result = {'ret': True, 'msg': ipv4_dict}
                            return result
                        else:
                            error_message = utils.get_extended_error(response_nic_url)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                                member_url, response_nic_url.status, error_message)}
                            return result
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                managers_url, response_managers_url.status, error_message)}
            return result

    except Exception as e:
        traceback.print_exc()
        result = {'ret': False, 'msg': 'exception msg %s' % e}
        return result
    finally:
        REDFISH_OBJ.logout()


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    argget = utils.create_common_parameter_list()
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Get bmc ipv4 info and check result
    result = get_ipv4(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])