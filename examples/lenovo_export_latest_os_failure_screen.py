###
#
# Lenovo Redfish examples - Export latest os failure screen
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


def export_latest_failure_screen(ip, login_account, login_password):
    """Export latest os failure screen
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :returns: returns export latest os failure screen result when succeeded or error message when failed
    """

    # Connect using the address, account name, and password
    login_host = "https://" + ip 
    try:
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result

    try:
        # Get ServiceRoot resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1/Managers', None)
        # Get managers collection
        if response_base_url.status == 200:
            managers_list = response_base_url.dict['Members']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                '/redfish/v1/Managers', response_base_url.status, error_message)}
            return result

        # Get manager uri
        for i in managers_list:
            manager_uri = i["@odata.id"]
            response_manager_uri =  REDFISH_OBJ.get(manager_uri, None)
            if response_manager_uri.status == 200:
                # Get servicedata uri
                servicedata_uri = response_manager_uri.dict['Oem']['Lenovo']['ServiceData']['@odata.id']
            else:
                error_message = utils.get_extended_error(response_manager_uri)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                    manager_uri, response_manager_uri.status, error_message)}
                return result

            # Get servicedata resource from service data uri response
            response_servicedata_uri = REDFISH_OBJ.get(servicedata_uri, None)
            if response_servicedata_uri.status == 200:
                # Build post request body and Get the user specified parameter
                latest_os_failure_screen_uri = response_servicedata_uri.dict['Actions']['#LenovoServiceData.ExportLatestOSFailureScreen']['target']

                # Get latest os failure screen through post requests
                response_latest_os_failure_screen_uri = REDFISH_OBJ.post(latest_os_failure_screen_uri, None)
                if response_latest_os_failure_screen_uri.status == 200:
                    download_uri = response_latest_os_failure_screen_uri.dict["DownloadURI"]
                    result = download_lastest_os_failure_screen(ip, login_account, login_password, download_uri)
                    return result
                else:
                    error_message = utils.get_extended_error(response_latest_os_failure_screen_uri)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        latest_os_failure_screen_uri, response_latest_os_failure_screen_uri.status, error_message)}
                    return result
            else:
                error_message = utils.get_extended_error(response_servicedata_uri)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                    servicedata_uri, response_servicedata_uri.status, error_message)}
                return result
    except Exception as e:
        result = {'ret': False, 'msg': 'exception msg %s' % e}
        return result
    finally:
        REDFISH_OBJ.logout()


from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests

def download_lastest_os_failure_screen(ip, login_account, login_password, download_uri):
    """Download ffdc file from download_uri"""
    # closed ssl security warning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    download_sign = False
    download_uri = "https://" + ip + download_uri
    # Get session Id
    session_uri = "https://" + ip + "/redfish/v1/SessionService/Sessions/"
    body = {"UserName":login_account, "Password":login_password}
    headers = {"Content-Type": "application/json"}

    # Get session information via request session uri
    response_session_uri = requests.post(session_uri, data=json.dumps(body), headers = headers, verify=False)
    if response_session_uri.status_code == 201:
        x_auth_token = response_session_uri.headers['X-Auth-Token']
        location_uri = response_session_uri.headers['Location']
    else:
        result = {'ret': download_sign, 'msg': "error_code:%s" %response_session_uri.status_code}
        return result
    try:
        jsonHeader = {"X-Auth-Token":x_auth_token, "Content-Type":"application/json"}
        # Download latest os failure screen
        response_download_uri = requests.get(download_uri, headers=jsonHeader, verify=False)
        if response_download_uri.status_code == 200:
            failure_screen_name = download_uri.split('/')[-1]
            with open(os.getcwd() + os.sep + failure_screen_name, 'wb') as f:
                f.write(response_download_uri.content)
            download_sign = True
            result = {'ret': download_sign, 'msg': "The latest os failure screen is download to %s" %(os.getcwd() + os.sep + failure_screen_name)}
            return result
        else:
            result = {'ret': download_sign, 'msg': "Url '%s' response Error code %s" % (download_uri,response_session_uri.status_code)}
            return result

    except Exception as e:
        result = {'ret': download_sign, 'msg': 'exception msg %s' % e}
        return result
    finally:
        # Delete session
        delete_session_uri = "https://" + ip + location_uri
        jsonHeader = {"X-Auth-Token":x_auth_token, "Content-Type":"application/json"}
        requests.delete(delete_session_uri, headers=jsonHeader, verify=False)


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    argget = utils.create_common_parameter_list()
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Export latest failure screen result and check result
    result = export_latest_failure_screen(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])
