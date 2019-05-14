###
#
# Lenovo Redfish examples - Export health report
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
import time
import os


def export_health_report(ip, login_account, login_password):
    """Export the health report    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :returns: returns health report file position result when succeeded or error message when failed
    """

    # Connect using the address, account name, and password
    login_host = "https://" + ip 
    try:
        # Create a REDFISH object
        result = {}
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result

    try:
        # Get ServiceRoot resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1/Managers', None)
        
        # Get the manager url collection
        if response_base_url.status == 200:
            managers_list = response_base_url.dict['Members']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '/redfish/v1/Managers' response Error code %s \nerror_message: %s" % (response_base_url.status, error_message)}
            return result
        
        # Loop all manager resource instance in manager list
        for i in managers_list:
            manager_uri = i["@odata.id"]
            response_manager_uri =  REDFISH_OBJ.get(manager_uri, None)
            if response_manager_uri.status == 200:
                # Get servicedata uri from manager resource instance
                servicedata_uri = response_manager_uri.dict['Oem']['Lenovo']['ServiceData']['@odata.id']
            else:
                error_message = utils.get_extended_error(response_manager_uri)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (manager_uri, response_manager_uri.status, error_message)}
                return result

            # Get servicedata resource instance
            response_servicedata_uri = REDFISH_OBJ.get(servicedata_uri, None)
            if response_servicedata_uri.status == 200:
                export_health_report_uri = response_servicedata_uri.dict['Actions']['#LenovoServiceData.ExportHealthReport']['target']
                
                # Get the health report through post requests health report url 
                response_export_health_report_uri = REDFISH_OBJ.post(export_health_report_uri, None)
                if response_export_health_report_uri.status == 200:

                    # Specify health report name is composed of timestamp and Ip
                    releaseDate = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                    health_report_name = ip+'_'+"health_report_"+ releaseDate+'.xml'
                    report_pwd = os.getcwd() + os.sep + health_report_name

                    # Write the response to the health report
                    with open(report_pwd, 'w') as f:
                        f.write(response_export_health_report_uri.dict['Report'])
                    result = {'ret': True, 'msg':  "The health report is saved as '%s' "  %(report_pwd)}
                else:
                    error_message = utils.get_extended_error(response_export_health_report_uri)
                    result = {'ret': False, 'msg': "Failure to export health report, Url '%s' response Error code %s \nerror_message: %s" % (export_health_report_uri, response_export_health_report_uri.status, error_message)}
                    return result
            else:
                error_message = utils.get_extended_error(response_servicedata_uri)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (servicedata_uri, response_servicedata_uri.status, error_message)}
                return result
    except Exception as e:
        result = {'ret': False, 'msg': "error_message: %s" % (e)}
    finally:
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

    # Get export health report result and check result
    result = export_health_report(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])
