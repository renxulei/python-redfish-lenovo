###
#
# Lenovo Redfish examples - Umount all media iso
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


def umount_media_iso(ip, login_account, login_password):
    """ UMount media iso from network.
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :returns: returns mount media iso result when succeeded or error message when failed
    """
    result = {}
    login_host = "https://" + ip
    # Login into the server and create a session
    try:
        # Connect using the address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result
    try:
        # Get ServiceRoot resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
        # Get response_account_service_url
        if response_base_url.status == 200:
            account_managers_url = response_base_url.dict['Managers']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': " Url '/redfish/v1' response Error code %s \nerror_message: %s" % (
            response_base_url.status, error_message)}
            return result

        response_managers_url = REDFISH_OBJ.get(account_managers_url, None)
        if response_managers_url.status == 200:
            # Get manager url form manager resource instance
            manager_count = response_managers_url.dict['Members@odata.count']
            for i in range(manager_count):
                manager_url = response_managers_url.dict['Members'][i]['@odata.id']
                response_manager_url = REDFISH_OBJ.get(manager_url, None)
                if response_manager_url.status == 200:
                    # Get mount media iso url
                    remotemap_url = response_manager_url.dict['Oem']['Lenovo']['RemoteMap']['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_manager_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                    manager_url, response_manager_url.status, error_message)}
                    return result

                response_remotemap_url = REDFISH_OBJ.get(remotemap_url, None)
                if response_remotemap_url.status == 200:
                    # Get umount image url form remote map resource instance
                    umount_image_url = response_remotemap_url.dict['Actions']['#LenovoRemoteMapService.UMount']['target']
                    response_umount_image = REDFISH_OBJ.post(umount_image_url, None)
                    if response_umount_image.status in [202, 204]:
                        result = {'ret': True, 'msg': "All Media File from Network umount successfully"}
                    else:
                        error_message = utils.get_extended_error(response_umount_image)
                        result = {'ret': False, 'msg': "Umount media iso failed, '%s' response Error code %s \nerror_message: %s" % (remotemap_url, response_umount_image.status, error_message)}
                        return result
                else:
                    error_message = utils.get_extended_error(response_remotemap_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                    remotemap_url, response_remotemap_url.status, error_message)}
                    return result

        # Return error messages when the managers url response failed
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False,'msg': "Url '%s' response Error code %s \nerror_message: %s" % (account_managers_url, response_managers_url.status, error_message)}
    except Exception as e:
        result = {'ret':False, 'msg':e}
    finally:
        # Logout of the current session
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
    system_id = parameter_info['sysid']

    # Get umount media iso result and check result
    result = umount_media_iso(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])