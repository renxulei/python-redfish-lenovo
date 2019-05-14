###
#
# Lenovo Redfish examples - Set bmc timezone
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

def lenovo_set_bmc_timezone(ip, login_account, login_password,timezone):
    """Set Bios attribute
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :params timezone: timezone by user specified
        :type timezone: string
        :returns: returns set timezone result when succeeded or error message when failed
        """
    result = {}

    list = ("+0:00", "+1:00", "+2:00-EasternEurope", "+2:00-Turkey", "+2:00-Beirut", "+2:00-Amman", "+2:00-Jerusalem",
            "+3:00", "+3:30", "+4:00", "+4:30", "+5:00", "+5:30", "+5:45", "+6:00", "+6:30", "+7:00", "+8:00", "+9:00",
            "+9:30","+10:00", "+11:00", "+12:00", "+13:00", "-12:00", "-11:00", "-10:00", "-9:00","-8:00",
            "-7:00-Canada_USA","-7:00-Mazatlan", "-6:00-Mexico", "-6:00-Canada_USA", "-5:00-Cuba", "-5:00-Eastern",
            "-4:30","-4:00-Asuncion","-4:00-Cuiaba", "-4:00-Santiago", "-4:00-Canada", "-3:30", "-3:00-Godthab",
            "-3:00-Montevideo","-3:00-Brazil","-2:00", "-1:00")
    if timezone not in list:
        result = {'ret': False, 'msg': "the value you set is not in the list of timezone values,please check your input and get help info"}
        return result
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
                    parameter = {"UTCOffset": timezone}
                    response_datetime_set_url = REDFISH_OBJ.patch(datetime_url, body=parameter)
                    if response_datetime_set_url.status == 200:
                        result = {'ret': True, 'msg': " Set bmc timezone successful"}
                        REDFISH_OBJ.logout()
                        return result
                    else:
                        result = {'ret': False, 'msg': " Set bmc timezone  Error code %s" % response_datetime_set_url.status}
                        REDFISH_OBJ.logout()
                        return result
                else:
                    result = {'ret': False, 'msg': "response datetime url Error code %s" % response_datetime_url.status}
                    REDFISH_OBJ.logout()
                    return result
            else:
                result = {'ret': False, 'msg': "response manager url Error code %s" % response_url.status}
                REDFISH_OBJ.logout()
                return result


import argparse
def add_helpmessage(argget):
    help_str = "Input the time zone you want to set,you can  set the value only in the list:"
    help_str += "[" + "+0:00, " + "+1:00, " +  "+2:00-EasternEurope, " + "+2:00-Turkey, " + "+2:00-Beirut, " + "+2:00-Amman, " + "+2:00-Jerusalem, "
    help_str += "+3:00, " + "+3:30, " + "+4:00, " + "+4:30, " + "+5:00, " + "+5:30, " + "+5:45, " + "+6:00, " + "+6:30, " + "+7:00, " + "+8:00, "
    help_str +=  "+9:00, " + "+9:30, " + "+10:00, " + "+11:00, " + "+12:00, " + "+13:00, " + "-12:00, "  + "-11:00, " +  "-10:00, " + "-9:00, "
    help_str += "-8:00, " + "-7:00-Canada_USA, " + "-7:00-Mazatlan, " + "-6:00-Mexico, " + "-6:00-Canada_USA, " + "-5:00-Cuba, " + "-5:00-Eastern, "
    help_str += "-4:30, " + "-4:00-Asuncion, " + "-4:00-Cuiaba, " + "-4:00-Santiago, " + "-4:00-Canada, " + "-3:30, " + "-3:00-Godthab, "
    help_str += "-3:00-Montevideo, " + "-3:00-Brazil, " + "-2:00, " + "-1:00" + "]"
    argget.add_argument('--timezone', type=str, required=True, help=help_str)


def add_parameter():
    """Add set bmc timezone parameter"""
    parameter_info = {}
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["timezone"] = args.timezone
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    ip = parameter_info["ip"]
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    timezone = parameter_info["timezone"]

    #set bmc timezone
    result = lenovo_set_bmc_timezone(ip, login_account, login_password, timezone)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])