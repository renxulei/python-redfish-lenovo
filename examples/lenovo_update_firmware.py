###
#
# Lenovo Redfish examples - Update Firmware
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
import time
import lenovo_utils as utils


def update_fw(ip, login_account, login_password, fixid, localpath, firmwarerole, fsprotocol, fsport, fsip, fsusername, fspassword, fsdir):
    """Update firmware    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params fixid: Specify the fixid of the firmware to be updated
    :type fixid: string
    :params localpath: Specify the absolute path of firmware locally
    :type localpath: string
    :params firmwarerole: Specify the absolute path of firmware locally
    :type firmwarerole: string
    :params fsip: Specify the file server ip
    :type fsip: string
    :params fsusername: Specify the file server username
    :type fsusername: string
    :params fspassword: Specify the file server password
    :type fspassword: string
    :params fsdir: Specify the file server dir to the firmware upload
    :type fsdir: string
    :returns: returns update firmware result when succeeded or error message when failed
    """
    result = {}
    download_flag = False
    xml_file = fixid + '.xml'

    # Check user specify parameter
    if not localpath:
        download_flag = sftp_download_xmlfile(xml_file, fsip, fsport, fsusername, fspassword, fsdir)
    else:
        # Parse the xml file if local path exits
        if not os.path.exists(localpath):
            result = {'ret': False, 'msg': "The local path doesn't exist."}
            return result

    # Defines a dictionary for storing pre request information.
    pre_req_info_dict = {}
    if not download_flag and localpath:
        xml_file_path = localpath + os.sep + fixid + '.xml'
    else:
        xml_file_path = os.getcwd() + os.sep + xml_file

    if os.path.isfile(xml_file_path):
        sups_info_dict = parse_xml(xml_file_path)
        if not localpath:
            # Delete xml file
            os.remove(xml_file_path)

    else:
        result = {'ret': False, 'msg': "The firmware xml doesn't exist, please download the firmware xml file."}
        return result

    # Get the fixID xml information
    payload = sups_info_dict['payload']
    prereq_list = sups_info_dict['prereq']
    pre_req_info_list = []
    if prereq_list:
        for pre_req in prereq_list:
            pre_req_file = pre_req +".xml"
            if not localpath:
                download_flag = sftp_download_xmlfile(pre_req_file, fsip, fsport, fsusername, fspassword, fsdir)
                if download_flag:
                    pre_req_xml = os.getcwd() + os.sep + pre_req_file
            else:
                pre_req_xml = localpath + os.sep + pre_req_file
            if os.path.isfile(pre_req_xml):
                pre_req_info_dict = parse_xml(pre_req_xml)
                pre_req_info_list.append(pre_req_info_dict)
            else:
                result = {'ret': False, 'msg': "The prerequest xml file doesn't exist, please download the %s." % pre_req}
                return result

    # Upload payload to file server
    if fsprotocol.upper() == "SFTP" and localpath is not None:
        upload_flag = sftp_upload_payload(localpath, payload, fsport, fsip, fsusername, fspassword, fsdir)
        if not upload_flag:
            result = {'ret': False, 'msg': "Upload payload file failed, please try again."}
            return result

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
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
        # Get response_update_service_url
        if response_base_url.status == 200:
            update_service_url = response_base_url.dict['UpdateService']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '/redfish/v1' response Error code %s \nerror_message: %s" % (response_base_url.status, error_message)}
            return result

        response_update_service_url = REDFISH_OBJ.get(update_service_url, None)
        if response_update_service_url.status == 200:
            update_firmware_inventory_url = response_update_service_url.dict['Actions']['#UpdateService.SimpleUpdate']['target']
            firmwareinventory_info_url = response_update_service_url.dict['FirmwareInventory']['@odata.id']

            # Confirm the target info and get the current version of firmware
            category = sups_info_dict['category']
            fw_role = firmwarerole
            current_info_dict = get_current_version(REDFISH_OBJ, firmwareinventory_info_url, category, fw_role)
            current_version = current_info_dict['current_version']

            # Check whether the prerequest version meets the requirements
            for pre_req_info_dict in pre_req_info_list:
                pre_req_flag = check_pre_req_info(REDFISH_OBJ, pre_req_info_dict, firmwareinventory_info_url)
                if not pre_req_flag:
                    result = {'ret': False, 'msg': "Update the firmware failed, Please check the pre request version."}
                    return result

            # Get the update firmware info.
            update_version = sups_info_dict['Version']
            target = current_info_dict['target']
            print("The firmware version will be updated from %s to %s." %(current_version, update_version))

            # Build post parameter
            remote_path = fsprotocol.lower() + "://" + fsusername + ":" + fspassword + "@" + fsip + "/" + fsdir + "/" + payload
            targets_list = [login_host + target]
            parameter = {"ImageURI": remote_path, "Targets": targets_list, "TransferProtocol": fsprotocol.upper()}

            # Update firmware via redfish api
            response_firmware_inventory = REDFISH_OBJ.post(update_firmware_inventory_url, body=parameter)
            if response_firmware_inventory.status == 202:
                if firmwarerole == "Primary":
                    firmware_type = category
                else:
                    firmware_type = category+"-"+firmwarerole
                task_uri = response_firmware_inventory.dict['@odata.id']
                while True:
                    task_detail_url = REDFISH_OBJ.get(task_uri, None)
                    if task_detail_url.status == 200:
                        task_state = task_detail_url.dict["TaskState"]
                        print('\r{0}'.format(task_state), end='', flush=True)
                        if task_state in ["Completed", "OK"]:
                            print()
                            result = {'ret': True, 'msg': "Update firmware(%s) [%s to %s]  successfully" % (
                            firmware_type, current_version, update_version)}
                            # Delete the task when the taskstate is completed
                            REDFISH_OBJ.delete(task_uri, None)
                            return result
                        elif task_state == 'Exception':
                            result = {'ret': False, 'msg': 'Taskstate exception'}
                            break
                        else:
                            time.sleep(1)
                            continue
                    else:
                        error_message = utils.get_extended_error(task_detail_url)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                            task_uri, task_detail_url.status, error_message)}

            else:
                error_message = utils.get_extended_error(response_firmware_inventory)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (update_firmware_inventory_url, response_firmware_inventory.status, error_message)}
        else:
            error_message = utils.get_extended_error(response_update_service_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (update_service_url, response_update_service_url.status, error_message)}
    except Exception as e:
        result = {'ret': False, 'msg': "error_message: %s" %e}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


def check_pre_req_info(REDFISH_OBJ, pre_req_info_dict, firmwareinventory_info_url):
    if len(pre_req_info_dict) != 0:
        category = pre_req_info_dict['category'].upper()
        if category in ['XCC', 'IMM']:
            pre_req_info_url = firmwareinventory_info_url + "BMC-Primary"
        elif category in ['UEFI']:
            pre_req_info_url = firmwareinventory_info_url + "UEFI"
        else:
            pre_req_info_url = firmwareinventory_info_url
        response_pre_req_info = REDFISH_OBJ.get(pre_req_info_url, None)
        if response_pre_req_info.status == 200:
            firmware_version = response_pre_req_info.dict['Version']
            if float(pre_req_info_dict['Version']) > float(firmware_version):
                print("Please update firmware %s to %s" % (category, pre_req_info_dict['Version']))
                return False
            else:
                return True
        else:
            return False
    else:
        return False


def get_current_version(REDFISH_OBJ, firmwareinventory_info_url, category, fw_role):
    current_dict = {}
    if category == "UEFI":
        target = "UEFI"
    elif category == "LXPM":
        target = "LXPM"
    elif category == "DRVLN":
        target = "LXPMLinuxDriver1"
    elif category == "DRVWN":
        target = "LXPMWindowsDriver1"
    elif category in ["IMM", "XCC"]:
        if fw_role.upper() == "PRIMARY":
            target = 'BMC-Primary'
        else:
            target = "BMC-Backup"
    else:
        target = "/redfish/v1/Systems/1"
    if not target.startswith("/redfish/v1/"):
        target = firmwareinventory_info_url + target
        response_firmware_inventory = REDFISH_OBJ.get(target, None)
        if response_firmware_inventory.status == 200:
            firmware_version = response_firmware_inventory.dict['Version']
            current_dict['current_version'] = firmware_version
            current_dict['target'] = target
        else:
            try:
                error_message = utils.get_extended_error(response_firmware_inventory)
            except:
                error_message = response_firmware_inventory
            print("response update service url Error code %s \nerror_message: %s" % (response_firmware_inventory.status, error_message))
    return current_dict


import xml.etree.ElementTree as ET
import os
import re
def parse_xml(xml_file_path):
    """Parse fixid xml files"""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    # Build an empty dictionary to store information in XML
    sups_dict = {}
    # Build an empty list to store prerequest information
    pre_req = []
    mt_list = []
    # Add MT
    info_list = ["category", "Version", "payload", "xmlFilename", "preReq", "buildNumber"]
    for node in root.iter('PROPERTY.ARRAY'):
        if "preReq" in node.attrib['NAME']:
            for value in node.iter('VALUE'):
                pre_req.append(value.text)
        if "applicableMachineTypes" in node.attrib['NAME']:
            for MT in node.iter('VALUE'):
                regularity = re.compile(r'[[](.*?)[]]')
                mt = regularity.findall(MT.text)
                mt_list.append(mt)
    sups_dict['prereq'] = pre_req
    for node in root.iter('PROPERTY'):
        for info_name in info_list:
            if node.attrib['NAME'] == info_name:
                for value in node.iter('VALUE'):
                    sups_dict[info_name] = value.text
    sups_dict['Version'] = sups_dict['Version'].split(' ')[1]
    sups_dict['mt_list'] = mt_list
    return sups_dict


import paramiko
def sftp_upload_payload(localpath, payload, fsport, fsip, fsusername, fspassword, fsdir):
    """Upload localpath firmware payload to remote file serverse"""
    upload_flag = False
    fw_payload = localpath + os.sep + payload
    if not os.path.exists(fw_payload):
        print("The firmware payload file doesn't exist.")
        return upload_flag
    # Connect file server using the fsip, fsusername, and fspassword
    try:
        sf = paramiko.Transport((fsip, fsport))
        sf.connect(username=fsusername, password=fspassword)
        sftp = paramiko.SFTPClient.from_transport(sf)
        # Judge whether the file is on SFTP.
        files_list = sftp.listdir(fsdir)
        if payload in files_list:
            # Compare the local file and remote file size
            remote_file_size = sftp.stat(fsdir + "/" + payload).st_size
            local_file_size = os.path.getsize(fw_payload)
            if remote_file_size == local_file_size:
                print("Firmware payload already exists on SFTP. ")
                upload_flag = True
            else:
                sftp.put(fw_payload, fsdir + "/" + payload)
                upload_flag = True 
        else:
            print("Uploading files may take several minutes.")
            sftp.put(fw_payload, fsdir + "/" + payload)
            upload_flag = True
        sf.close()
    except Exception as e:
        print('upload exception:',e)
    return upload_flag


def sftp_download_xmlfile(xml_file, fsip, fsport, fsusername, fspassword, fsdir):
    """Down load the firmware xml file"""
    # Connect file server using the fsip, fsusername, and fspassword
    download_flag = False
    try:
        sf = paramiko.Transport((fsip, int(fsport)))
        sf.connect(username=fsusername, password=fspassword)
        sftp = paramiko.SFTPClient.from_transport(sf)
        # Judge whether the file is on SFTP.
        files_list = sftp.listdir(fsdir)
        remote_path = "/"+ fsdir + "/"+ xml_file
        local_path = os.getcwd() + os.sep + xml_file

        if xml_file in files_list:
            sftp.get(remote_path, local_path)
            download_flag = True
        else:
            print("There is no firmware xml file on the remote server, please download the firmware xml file..")
        sf.close()

    except Exception as e:
        print('download exception:', e)
    return download_flag


import configparser
def add_parameter():
    """Add set bios attribute parameter"""
    argget = utils.create_common_parameter_list()
    argget.add_argument('--fixid', type=str,required=True, help='Specify the fixid of the firmware to be updated.')
    argget.add_argument('--localpath', type=str, help='Specify the absolute path of firmware locally.')
    argget.add_argument('--firmwarerole', type=str, default='primary', help='Specify the firmware role, role primary backup only for BMC. Support:["Primary"，"Backup"]')
    argget.add_argument('--fsprotocol', type=str, help='Specify the file server protocol.Support:["SFTP"]')
    argget.add_argument('--fsport', type=int, default='22', help='Specify the file server port')
    argget.add_argument('--fsip', type=str, help='Specify the file server ip.')
    argget.add_argument('--fsusername', type=str, help='Specify the file server username.')
    argget.add_argument('--fspassword', type=str, help='Specify the file server password.')
    argget.add_argument('--fsdir', type=str, help='Specify the file server dir to the firmware upload.')
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    config_file = args.config
    config_ini_info = utils.read_config(config_file)
    # Add FileServerCfg parameter to config_ini_info
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    config_ini_info["fsprotocol"] = cfg.get('FileServerCfg', 'FSprotocol')
    config_ini_info["fsport"] = cfg.get('FileServerCfg', 'FSport')
    config_ini_info["fsip"] = cfg.get('FileServerCfg', 'FSip')
    config_ini_info["fsusername"] = cfg.get('FileServerCfg', 'FSusername')
    config_ini_info["fspassword"] = cfg.get('FileServerCfg', 'FSpassword')
    config_ini_info["fsdir"] = cfg.get('FileServerCfg', 'FSdir')
    # Parse the added parameters
    if args.fixid is not None:
        parameter_info['fixid'] = args.fixid
    parameter_info['localpath'] = args.localpath
    parameter_info['firmwarerole'] = args.firmwarerole
    parameter_info['fsprotocol'] = args.fsprotocol
    parameter_info['fsport'] = args.fsport
    parameter_info['fsip'] = args.fsip
    parameter_info['fsusername'] = args.fsusername
    parameter_info['fspassword'] = args.fspassword
    parameter_info['fsdir'] = args.fsdir
    # The parameters in the configuration file are used when the user does not specify parameters
    for key in parameter_info:
        if not parameter_info[key]:
            if key in config_ini_info:
                parameter_info[key] = config_ini_info[key]
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()
    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Get set info from the parameters user specified
    try:
        fixid = parameter_info['fixid']
        localpath = parameter_info['localpath']
        firmwarerole = parameter_info['firmwarerole']
        fsprotocol = parameter_info['fsprotocol']
        fsport = parameter_info['fsport']
        fsip = parameter_info['fsip']
        fsusername = parameter_info['fsusername']
        fspassword = parameter_info['fspassword']
        fsdir = parameter_info['fsdir']
    except Exception as e:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Update firmware result and check result
    result = update_fw(ip, login_account, login_password, fixid, localpath, firmwarerole, fsprotocol, fsport, fsip, fsusername, fspassword, fsdir)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])