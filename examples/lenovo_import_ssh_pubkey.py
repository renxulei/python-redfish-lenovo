###
#
# Lenovo Redfish examples - Import SSH Pubkey
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
import logging
import json
import redfish
import lenovo_utils as utils


def import_ssh_pubkey(ip, login_account, login_password,user_name,pb_command):
    """Import SSH Pubkey    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params user_name: user name
    :type user_name: string
    :params pb_command: pub key
    :type pb_command: string
    :returns: returns import result
    """
    #parse paramater
    sshpubkey = ""
    for key in pb_command:
        if key == "sshpubkey":
            sshpubkey = pb_command[key]
        else:
            try:
                file = open(pb_command[key],"r")
                sshpubkey = file.read()
                sshpubkey = sshpubkey.split("\n")[0]
            except Exception as e:
                result = {"ret":False,"msg":"Open file:" + pb_command[key] + " fail,please check your input"}
                return result
    result = {}
    login_host = "https://" + ip
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                             password=login_password, default_prefix='/redfish/v1')
        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result
    try:
        # GET the Accounts resource
        response_base_url = REDFISH_OBJ.get("/redfish/v1", None)
        if response_base_url.status == 200:
            account_service_url = response_base_url.dict["AccountService"]["@odata.id"]
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '/redfish/v1' response Error code %s\nerror_message: %s" % (
                response_base_url.status, error_message)}
            return result

        response_account_service_url = REDFISH_OBJ.get(account_service_url, None)
        if response_account_service_url.status == 200:
            accounts_url = response_account_service_url.dict["Accounts"]["@odata.id"]
        else:
            error_message = utils.get_extended_error(response_account_service_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                account_service_url, response_account_service_url.status, error_message)}
            return result
        # Get all BMC user account
        accounts_url_response = REDFISH_OBJ.get(accounts_url, None)
        if accounts_url_response.status == 200:
            # Loop through Accounts and print info
            account_url_list = accounts_url_response.dict["Members"]
            for account_dict in account_url_list:
                account_url = account_dict["@odata.id"]
                account_url_response = REDFISH_OBJ.get(account_url)
                if account_url_response.status == 200:
                    if user_name == account_url_response.dict["UserName"]:
                        if "@odata.etag" in account_url_response.dict:
                            etag = account_url_response.dict['@odata.etag']
                        else:
                            etag = ""
                        headers = {"If-Match": etag}
                        parameter = {"Oem":{"Lenovo":{"SSHPublicKey":[sshpubkey]}}}
                        set_sshpubkey_response = REDFISH_OBJ.patch(account_url,body=parameter,headers=headers)
                        if set_sshpubkey_response.status == 200:
                            result = {"ret":True,"msg":"Import ssh public key successfully"}
                            return result
                        else:
                            error_message = utils.get_extended_error(set_sshpubkey_response)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                                account_url, set_sshpubkey_response.status, error_message)}
                            return result
                    else:
                        continue
                else:
                    error_message = utils.get_extended_error(account_url_response)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        account_url, account_url_response.status, error_message)}
                    return result
            result = {"ret":False,"msg":"User name is not existed,Please check your input"}
            return result
        else:
            error_message = utils.get_extended_error(accounts_url_response)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                accounts_url, accounts_url_response.status, error_message)}
            return result
    except Exception as e:
        result = {'ret': False, 'msg': "Error message %s" % e}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result

def add_helpmessage(argget):
    argget.add_argument('--username', type=str, help='The user name you want to import',required=True)
    group = argget.add_mutually_exclusive_group(required=True)
    group.add_argument('--sshpubkey', type=str, help='Ssh pubkey you want to set')
    group.add_argument('--sshpubkeyfile', type=str, help='File which contain ssh pubkey you want to set')

def add_parameter():
    """Import SSH pubkey parameter"""
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["username"] = args.username
    dict_opcommand  = {}
    if args.sshpubkey:
        dict_opcommand["sshpubkey"] = args.sshpubkey
    else:
        dict_opcommand["sshpubkeyfile"] = args.sshpubkeyfile
    parameter_info["pb_command"] = dict_opcommand
    return parameter_info

if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()
    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]
    user_name = parameter_info["username"]
    pb_command = parameter_info["pb_command"]

    # Get BMC inventory and check result
    result = import_ssh_pubkey(ip, login_account, login_password,user_name,pb_command)

    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])