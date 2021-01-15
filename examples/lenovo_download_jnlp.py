###
#
# Lenovo Redfish examples - download jnlp
#
# Copyright Notice:
#
# Copyright 2021 Lenovo Corporation
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

import requests
import lenovo_utils as utils
import os,sys
import json
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def download_jnlp(ip, login_account, login_password):
    """Doenload jnlp
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :returns: returns session list when succeeded or error message when failed
    """
    login_host = "https://" + ip
    headers = {"Content-Type": "application/json"}
    session_url = login_host + "/api/session"
    body = {'username':login_account,'password':login_password}
    # Create session connection
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    s = requests.session()
    response = s.post(session_url, headers=headers, data=json.dumps(body), verify=False)
    json_response = json.loads(response.content)
    if response.status_code == 200:
        # Download jnlp file
        jnlp_url = login_host + "/api/remote_control/get/kvm/launch"
        h = {"X-CSRFTOKEN": "%s" % (json_response["CSRFToken"])}
        response_download_uri = s.get(jnlp_url, headers=h, cookies=s.cookies.get_dict(), verify=False)
        print(response_download_uri.status_code)
        if response_download_uri.status_code == 200:
            jnlp_file_name = "jviewer_"+ ip + ".jnlp"
            with open(os.getcwd() + os.sep + jnlp_file_name, 'wb') as f:
                f.write(response_download_uri.content)
            result = {'ret': True, 'msg': "jnlp file is saved as %s " % (jnlp_file_name)}
            return result
        else:
            result = {'ret': False, 'msg': "Download jnlp Failed, response code  %s" % response_download_uri.status_code}
            return result

        # Delete session
        delete_url = login_host + "/api/session"
        s.get(delete_url, headers=h, cookies=s.cookies.get_dict(), verify=False)

    else:
        result = {'ret': False,
                  'msg': "Session connection failed, response code %s" % response.status_code}
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

    # Download jnlp file and check result
    result = download_jnlp(ip, login_account, login_password)

    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(result['msg'])
    else:
        sys.stderr.write(result['msg'])
