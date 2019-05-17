###
#
# Lenovo Redfish examples - Get Sensors Information
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
import redfish
import json
import lenovo_utils as utils

def lenovo_get_sensors(ip, login_account, login_password):
    """Get sensors information
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :returns: returns get sensors information result when succeeded or error message when failed
        """

    properties = ['Description', 'EntityInstance', 'Id', 'Assertion',
                      'RecordType', 'OwnerLUN', 'OwnerID', 'SensorNumber',
                      'Name', 'State', 'SensorType', 'ReadingType',
                      'BaseUnit', 'Reading', 'EntityID', 'SensorTypeNumber',
                      'ThresholdLowerFatal', 'ThresholdLowerCritical', 'ThresholdLowerNonCritical', 'ThresholdUpperFatal',
                      'ThresholdUpperCritical', 'ThresholdUpperNonCritical', 'UnitModifier']
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
            #get sensors info
            for request in response_chassis_url.dict['Members']:
                request_url = request['@odata.id']
                response_url = REDFISH_OBJ.get(request_url, None)
                if response_url.status == 200:
                    #oem_resource = response_url.dict['Oem']['Lenovo']
                    #sensors_url = oem_resource['Configuration']['@odata.id']
                    sensors_url = response_url.dict['Oem']['Lenovo']['Sensors']['@odata.id']
                    response_sensors_url = REDFISH_OBJ.get(sensors_url, None)
                    if response_sensors_url.status == 200:
                        sensors_count = response_sensors_url.dict["Members@odata.count"]
                        sensor_index = 0
                        sensor_list = []
                        for sensor_index in range(0, sensors_count):
                            sensor = {}
                            single_sensor_url = response_sensors_url.dict["Members"][sensor_index]["@odata.id"]
                            response_single_sensor_url = REDFISH_OBJ.get(single_sensor_url, None)
                            if response_single_sensor_url.status == 200:
                                for property in properties:
                                    if property in response_single_sensor_url.dict:
                                        sensor[property] = response_single_sensor_url.dict[property]
                                sensor_list.append(sensor)
                    else:
                        error_message = utils.get_extended_error(response_sensors_url)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                            sensors_url, response_sensors_url.status, error_message)}
                        return result
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result
            result["ret"] = True
            result["entries"] = sensor_list
            return result
        else:
            error_message = utils.get_extended_error(response_chassis_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                chassis_url, response_chassis_url.status, error_message)}
            return result
    except Exception as e:
        result = {'ret': False, 'msg': "exception msg %s" % e}
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

    # Get fan inventory and check result
    result = lenovo_get_sensors(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])