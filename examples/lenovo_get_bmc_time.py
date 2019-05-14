###
#
# Lenovo Redfish examples - Get bmc time
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

def lenovo_get_bmc_time(ip, login_account, login_password):
    """Set Bios attribute
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
        manager_url = response_base_url.dict['Managers']['@odata.id']
    else:
        result = {'ret': False, 'msg': " response_base_url Error code %s" % response_base_url.status}
        REDFISH_OBJ.logout()
        return result
    response_manager_url = REDFISH_OBJ.get(manager_url, None)
    bmc_time_detail = []
    if response_manager_url.status == 200:
        for request in response_manager_url.dict['Members']:
            request_url = request['@odata.id']
            response_url = REDFISH_OBJ.get(request_url, None)
            if response_url.status == 200:
                #get datetime server url
                oem_resource = response_url.dict['Oem']['Lenovo']
                datetime_url = oem_resource['DateTimeService']['@odata.id']
                response_datetime_url = REDFISH_OBJ.get(datetime_url, None)
                if response_datetime_url.status == 200:
                    bmc_time_info = {}
                    bmc_time_info["DateTime"] = response_datetime_url.dict["DateTime"]
                    bmc_time_info["SettingMethod"] = response_datetime_url.dict["SettingMethod"]
                    bmc_time_info["UTCOffset"] = response_datetime_url.dict["UTCOffset"]
                    bmc_time_detail.append(bmc_time_info)
                else:
                    result = {'ret': False, 'msg': "response datetime Error code %s" % response_datetime_url.status}
                    REDFISH_OBJ.logout()
                    return result
            else:
                result = {'ret': False, 'msg': "response manager url Error code %s" % response_url.status}
                REDFISH_OBJ.logout()
                return result
        result = {'ret': True, 'entries': bmc_time_detail}
        REDFISH_OBJ.logout()
        return result
    else:
        result = {'ret': False, 'msg': "response manager url Error code %s" % response_manager_url.status}
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

    # Get BMC time and check result
    result = lenovo_get_bmc_time(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])