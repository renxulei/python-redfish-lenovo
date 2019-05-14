###
#
# Lenovo Redfish examples - Mount virtual media from network
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


def mount_media_iso(ip, login_account, login_password, fsprotocol, fsip, fsusername, fspassword, fsdir, isoname, readonly, domain, options):
    """Mount an ISO or IMG image file from a file server to the host as a DVD or USB drive.
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params fsprotocol:Specifies the protocol prefix for uploading image or ISO
    :type fsprotocol: string
    :params fsip:Specify the file server ip
    :type fsip: string
    :params fsusername:Username to access the file path, available for Samba, NFS, HTTP/HTTPS, SFTP/FTP
    :type fsusername: string
    :params fspassword:Password to access the file path, password should be encrypted after object creation, available for Samba, NFS, HTTP/HTTPS, SFTP/FTP
    :type fspassword: string
    :params fsdir:File path of the map image
    :type fsdir: string
    :params isoname: Mount media iso name
    :type isoname:string
    :params readonly:It indicates the map image status is readonly or read/write
    :type readonly: string
    :params domain:Domain of the username to access the file path, available for Samba only.
    :type domain: string
    :params options:It indicates the mount options to map the image of the file path, available for Samba and NFS only
    :type options: string
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
            result = {'ret': False, 'msg': " Url '/redfish/v1' response Error code %s \nerror_message: %s" % (response_base_url.status, error_message)}
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
                    remotemap_url = response_manager_url.dict['Oem']['Lenovo']['RemoteMap']['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_manager_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (manager_url, response_manager_url.status, error_message)}
                    return result

                response_remotemap_url = REDFISH_OBJ.get(remotemap_url, None)
                if response_remotemap_url.status == 200:
                    # Get MountImages url from remote map resource instance
                    images_member_url = response_remotemap_url.dict['MountImages']['@odata.id']
                    headers = {"Content-Type":"application/json"}

                    # Build request body for add images member
                    body = {}
                    protocol = fsprotocol.lower()
                    if protocol == "nfs":
                        body["FilePath"] =  fsip + ":/" + fsdir + "/" + isoname
                    elif protocol == "samba":
                        body["FilePath"] ="//" + fsip + '/' + fsdir + "/" + isoname
                    elif protocol in ['sftp', 'ftp', 'http', 'https']:
                        body["FilePath"] = protocol + "://" + fsip + '/' + fsdir + "/" + isoname
                    else:
                        result = {'ret':False, 'msg':'Mount media iso network only support protocol Samba, NFS, HTTP/HTTPS, SFTP/FTP'}
                        return result
                    body["Type"] = fsprotocol
                    body["Username"] = fsusername
                    body["Password"] = fspassword
                    body["Domain"] = domain
                    body["Readonly"] = bool(readonly)
                    body["Options"] = options
                    # Add image member
                    response_images_member = REDFISH_OBJ.post(images_member_url, headers=headers, body=body)
                    if response_images_member.status == 201:
                        print("Add image member successful.")
                    else:
                        error_message = utils.get_extended_error(response_images_member)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (images_member_url, response_images_member.status, error_message)}
                        return result

                    # Get mount image url form remote map resource instance
                    mount_image_url = response_remotemap_url.dict['Actions']['#LenovoRemoteMapService.Mount']['target']
                    response_mount_image = REDFISH_OBJ.post(mount_image_url, None)
                    if response_mount_image.status == 200:
                        result = {'ret': True, 'msg': "'%s' mount successfully" %isoname}
                    else:
                        error_message = utils.get_extended_error(response_mount_image)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (mount_image_url, response_mount_image.status, error_message)}
                        return result
                else:
                    error_message = utils.get_extended_error(response_remotemap_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (remotemap_url, response_remotemap_url.status, error_message)}
                    return result
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False,'msg': "Url '%s' response Error code %s \nerror_message: %s" % (account_managers_url, response_managers_url.status, error_message)}
    except Exception as e:
        result = {'ret': False, 'msg': "error_message: %s" % (e)}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


import argparse
import configparser
def add_helpmessage(argget):
    argget.add_argument('-c', '--config', type=str, default='config.ini',
                        help=('Configuration file(may be overrided by parameters from command line)'))
    argget.add_argument('-i', '--ip', type=str, help=('BMC IP address'))
    argget.add_argument('-u', '--user', type=str, help='BMC user name')
    argget.add_argument('-p', '--passwd', type=str, help='BMC user password')
    argget.add_argument('-s', '--sysid', type=str, default=None,
                        help='ComputerSystem instance id(None: first instance, All: all instances)')
    argget.add_argument('--fsprotocol', type=str, nargs='?', help='Specifies the protocol for uploading image or ISO.'
                                                                  'For the SFTP/FTP protocol, the iso size must be <= 50MB.\n'
                                                                  'Support: ["Samba","NFS","HTTP","SFTP","FTP"]')
    argget.add_argument('--fsip', type=str, nargs='?', help='Specify the file server ip')
    argget.add_argument('--fsusername', type=str, nargs='?', help='Username to access the file path, available for Samba, NFS, HTTP/HTTPS, SFTP/FTP')
    argget.add_argument('--fspassword', type=str, nargs='?', help='Password to access the file path, password should be encrypted after object creation, available for Samba, NFS, HTTP/HTTPS, SFTP/FTP')
    argget.add_argument('--fsdir', type=str, nargs='?', help='File path of the image')
    argget.add_argument('--isoname', type=str, required=True, help='Mount media iso name')
    argget.add_argument('--readonly', type=int, nargs='?', default=1, choices=[0, 1], help='It indicates the image is mapped as readonly or read/write. Support: [0:False, 1:True].')
    argget.add_argument('--domain', type=str, nargs='?', default='', help='Domain of the username to access the file path, available for Samba only.')
    argget.add_argument('--options', type=str, nargs='?', default='', help='It indicates the mount options to map the image of the file path, available for Samba and NFS only.')


def add_parameter():
    """Add mount media iso parameter"""
    argget = argparse.ArgumentParser(description="Mount media file from network, This feature is only supported when license is 'Lenovo XClarity Controller Enterprise'."
                                                 "Up to 4 files can be concurrently mounted to the server by the BMC")
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    config_file = args.config
    config_ini_info = utils.read_config(config_file)

    # Add FileServerCfg parameter to config_ini_info
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    config_ini_info["fsprotocol"] = cfg.get('FileServerCfg', 'FSprotocol')
    config_ini_info["fsip"] = cfg.get('FileServerCfg', 'FSip')
    config_ini_info["fsusername"] = cfg.get('FileServerCfg', 'FSusername')
    config_ini_info["fspassword"] = cfg.get('FileServerCfg', 'FSpassword')
    config_ini_info["fsdir"] = cfg.get('FileServerCfg', 'FSdir')
    # Parse the added parameters
    if args.isoname is None:
        sys.stderr.write("Please specify the ISO name that the user needs to mount.\n")
    else:
        parameter_info['isoname'] = args.isoname
    parameter_info['fsprotocol'] = args.fsprotocol
    parameter_info['fsip'] = args.fsip
    parameter_info['fsusername'] = args.fsusername
    parameter_info['fspassword'] = args.fspassword
    parameter_info['readonly'] = args.readonly
    parameter_info['fsdir'] = args.fsdir
    parameter_info['domain'] = args.domain
    parameter_info['options'] = args.options
    # The parameters in the configuration file are used when the user does not specify parameters
    for key in parameter_info:
        if not parameter_info[key]:
            if key in config_ini_info:
                parameter_info[key] = config_ini_info[key]
    # print(parameter_info)
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()
    
    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    
    # Get mount media iso info from the parameters user specified
    try:
        fsprotocol = parameter_info['fsprotocol']
        fsip = parameter_info['fsip']
        fsusername = parameter_info['fsusername']
        fspassword = parameter_info['fspassword']
        isoname = parameter_info['isoname']
        readonly = parameter_info['readonly']
        fsdir = parameter_info['fsdir']
        domain = parameter_info['domain']
        options = parameter_info['options']
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Get mount media iso result and check result
    result = mount_media_iso(ip, login_account, login_password, fsprotocol, fsip, fsusername, fspassword, fsdir, isoname, readonly, domain, options)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])
