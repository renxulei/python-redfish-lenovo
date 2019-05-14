###
#
# Lenovo Redfish examples - Get location
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

def get_location(ip, login_account, login_password):
    """Get location
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :returns: returns get bmc time result when succeeded or error message when failed
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
    response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
    # Get response_base_url
    if response_base_url.status == 200:
        chassis_url = response_base_url.dict['Chassis']['@odata.id']
    else:
        result = {'ret': False, 'msg': " response base url Error code %s" % response_base_url.status}
        REDFISH_OBJ.logout()
        return result
    response_chassis_url = REDFISH_OBJ.get(chassis_url, None)
    location_list = []
    if response_chassis_url.status == 200:
        location_dict = {}
        #get location info
        for request in response_chassis_url.dict['Members']:
            request_url = request['@odata.id']
            response_url = REDFISH_OBJ.get(request_url, None)
            if response_url.status == 200:
                located = response_url.dict["Oem"]["Lenovo"]["LocatedIn"]
                location_dict["building"] = located["Location"]
                location_dict["contact"] = located["ContactPerson"]
                location_dict["address"] = located["FullPostalAddress"]
                location_dict["rack_name"] = located["Rack"]
                location_dict["room_no"] = located["Room"]
                try:
                    location_dict["lowest_u"] = located["Position"]
                except:
                    pass
                location_list.append(location_dict)
            else:
                result = {'ret': False, 'msg': " response chassis member url Error code %s" % response_base_url.status}
                REDFISH_OBJ.logout()
                return result
    else:
        result = {'ret': False, 'msg': " response chassis url Error code %s" % response_chassis_url.status}
        REDFISH_OBJ.logout()
        return result
    result["ret"] = True
    result["entries"] = location_list
    REDFISH_OBJ.logout()
    return result


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    argget = utils.create_common_parameter_list()
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Get location and check result
    result = get_location(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])