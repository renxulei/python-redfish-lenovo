###
#
# Lenovo Redfish examples - Umount virtual media from RDOC
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


def umount_media_iso(ip, login_account, login_password, isoname):
    """Umount virtual media from RDOC
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params isoname: Input the umount virtual media name, default umount all virtual media from rdoc.
    :type isoname: string
    :returns: returns umount media iso result when succeeded or error message when failed
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
            result = {'ret': False, 'msg': "Url '/redfish/v1' response Error code %s \nerror_message: %s" % (response_base_url.status, error_message)}
            return result

        response_managers_url = REDFISH_OBJ.get(account_managers_url, None)
        if response_managers_url.status == 200:
            # Get manager url form manager resource instance
            count = response_managers_url.dict['Members@odata.count']
            for i in range(count):
                manager_url = response_managers_url.dict['Members'][i]['@odata.id']

                response_manager_url = REDFISH_OBJ.get(manager_url, None)
                if response_manager_url.status == 200:
                    # Get mount media iso url
                    remotecontrol_url = response_manager_url.dict['Oem']['Lenovo']['RemoteControl']['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_manager_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (manager_url, response_manager_url.status, error_message)}
                    return result

                response_remotecontrol_url = REDFISH_OBJ.get(remotecontrol_url, None)
                if response_remotecontrol_url.status == 200:
                    mount_image_url = response_remotecontrol_url.dict["MountImages"]["@odata.id"]
                else:
                    error_message = utils.get_extended_error(response_remotecontrol_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                        remotecontrol_url, response_remotecontrol_url.status, error_message)}
                    return result

                # Get all virtual media url from mount image url response
                response_mount_images = REDFISH_OBJ.get(mount_image_url, None)
                if response_mount_images.status == 200:
                    image_url_list = response_mount_images.dict["Members"]
                else:
                    error_message = utils.get_extended_error(response_mount_images)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                        mount_image_url, response_mount_images.status, error_message)}
                    return result

                for image in image_url_list:
                    image_url = image["@odata.id"]
                    if image_url.split("/")[-1].startswith("RDOC"):
                        # Umount all virtual media
                        if isoname == "all":
                            delete_image_response = REDFISH_OBJ.delete(image_url, None)
                            if delete_image_response.status not in [200, 204]:
                                error_message = utils.get_extended_error(delete_image_response)
                                result = {'ret': False,
                                          'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                                              image_url, delete_image_response.status, error_message)}
                                return result
                        # Umount user specify the virtual media
                        else:
                            get_image_response = REDFISH_OBJ.get(image_url, None)
                            if get_image_response.status == 200:
                                mount_iso_name = get_image_response.dict["Name"]
                                if isoname == mount_iso_name:
                                    umount_iso_response = REDFISH_OBJ.delete(image_url, None)
                                    if umount_iso_response.status in [200, 204]:
                                        result = {'ret': True,
                                                  'msg': "Virtual media iso (%s) umount successfully" % (isoname)}
                                        return result
                                    else:
                                        error_message = utils.get_extended_error(umount_iso_response)
                                        result = {'ret': False,
                                                  'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                                                      image_url, umount_iso_response.status, error_message)}
                                        return result
                                else:
                                    result = {"ret":False, "msg":"Please check the iso name is correct and has been mounted."}
                                    return result
                            else:
                                error_message = utils.get_extended_error(get_image_response)
                                result = {'ret': False,
                                          'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                                              image_url, get_image_response.status, error_message)}
                                return result
                result = {"ret":True, "msg":"Umount all virtual media successfully."}
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False,'msg': "Url '%s' response Error code %s \nerror_message: %s" % (account_managers_url, response_managers_url.status, error_message)}
    except Exception as e:
        result = {'ret': False, 'msg': "error_message: %s" % (e)}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result

def add_helpmessage(argget):
    argget.add_argument('--isoname', default="all", type=str, help='Input the umount virtual media name, default umount all virtual media from rdoc.')


def add_parameter():
    """Add set bios boot order parameter"""
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["isoname"] = args.isoname
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    ip = parameter_info["ip"]
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    system_id = parameter_info["sysid"]

    # Get set info from the parameters user specified
    try:
        isoname = parameter_info["isoname"]
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Umount virtual media iso result and check result
    result = umount_media_iso(ip, login_account, login_password, isoname)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])