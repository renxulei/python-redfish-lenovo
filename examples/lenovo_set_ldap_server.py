###
#
# Lenovo Redfish examples - set manager LDAP server
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
import traceback


def set_ldap_info(ip, login_account, login_password, method, ldapserver, port, domainname, binding_method, client_distinguished_name, client_password,
                           rootdn, uid_search_attribute, group_filter, group_search_attribute, login_permission_attribute, role_base_security, servername):
    """ Set manager LDAP information
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :params method: The LDAP servers to be used for authentication can either be manually configured or discovered dynamically via DNS SRV records
        :type method: string
        :params ldapserver: If you choose the pre-configured option, at least one server must be configured
        :type ldapserver: string
        :params port: The port number for each server is optional. If left blank, the default value of 389 is used for non-secured LDAP connections
        :type port: string
        :params domainname: This is only active under using DNS to find LDAP servers. If you choose to discover the LDAP servers dynamically, you will need to specify the search domain to be used
        :type domainname: string
        :params binding_method: This parameter controls how this initial bind to the LDAP server is performed.Support:["Anonymously", "Configured", "Login"]
        :type binding_method: string
        :params clientdn: Specify the Client Distinguished Name(DN) to be used for the initial bind. Note that LDAP Binding Method must be set to "Configured"
        :type clientdn: string
        :params clientpwd: Note that LDAP Binding Method must be set to "Configured"
        :type clientpwd: string
        :params rootdn: BMC uses the "ROOT DN" field in Distinguished Name format as root entry of directory tree.This DN will be used as the base object for all searches.
        :type rootdn: string
        :params uid_search_attribute: This search request must specify the attribute name used to represent user IDs on that server
        :type uid_search_attribute: string
        :params role_base_security:
        :type role_base_security: string
        :params servername: This parameter configure the BMC LDAP server Target Name setting
        :type servername: string
        :params group_filter: This field is used for group authentication, limited to 511 characters, and consists of one or more group names
        :type group_filter: string
        :params group_search_attribute: This field is used by the search algorithm to find group membership infomation for a specific user
        :type group_search_attribute: string
        :params login_permission_attribute: When a user successfully authenticates via a LDAP server, it is necessary to retrieve the login permissions for this user
        :type login_permission_attribute: string
        :returns: returns set manager LDAP user information result when succeeded or error message when failed
        """

    # Check user specified parameter
    result = check_parameter(method, ldapserver, domainname, binding_method, client_distinguished_name, client_password)
    if result["ret"] is False:
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
    try:
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
        # Get response_base_url
        if response_base_url.status == 200:
            managers_url = response_base_url.dict['Managers']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                '/redfish/v1', response_base_url.status, error_message)}
            return result

        response_managers_url = REDFISH_OBJ.get(managers_url, None)
        if response_managers_url.status == 200:
            for request in response_managers_url.dict['Members']:
                request_url = request['@odata.id']
                response_url = REDFISH_OBJ.get(request_url, None)
                # Get Network Protocol url from the manager url response
                if response_url.status == 200:
                    network_protocol_url = response_url.dict["NetworkProtocol"]['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result

                response_network_protocol_url = REDFISH_OBJ.get(network_protocol_url, None)
                if response_network_protocol_url.status == 200:
                    ldap_client_uri = response_network_protocol_url.dict["Oem"]["Lenovo"]["LDAPClient"]["@odata.id"]
                else:
                    error_message = utils.get_extended_error(response_network_protocol_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        network_protocol_url, response_network_protocol_url.status, error_message)}
                    return result

                # Build request body for set ldap server
                body = {}
                body["BindingMethod"] = {"ClientPassword":client_password,"ClientDN":client_distinguished_name, "Method":binding_method}
                body["ActiveDirectory"] = {"ServerTargetName": servername, "RoleBasedSecurity": bool(int(role_base_security))}
                body["RootDN"] = rootdn
                body["LoginPermissionAttribute"] = login_permission_attribute
                body["GroupFilter"] = group_filter
                body["GroupSearchAttribute"] = group_search_attribute
                body["UIDSearchAttribute"] = uid_search_attribute
                server_info = {}
                server_info["Method"] = method
                if method == "Pre_Configured":
                    for i in range(len(ldapserver)):
                        server_info["Server"+ str(i+1) +"HostName_IPAddress"] = ldapserver[i]
                        server_info["Server" + str(i+1) + "Port"] = port[i]
                else:
                    server_info["SearchDomain"] = domainname
                body["LDAPServers"] = server_info
                response_ldap_client = REDFISH_OBJ.patch(ldap_client_uri, body=body)
                if response_ldap_client.status == 200:
                    result =  {"ret": True, "msg":"Ldap server was successfully configured"}
                    return result
                else:
                    error_message = utils.get_extended_error(response_ldap_client)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        ldap_client_uri, response_ldap_client.status, error_message)}
                    return result
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                managers_url, response_managers_url.status, error_message)}
            return result

    except Exception as e:
        traceback.print_exc()
        result = {'ret': False, 'msg': 'exception msg %s' % e}
        return result
    finally:
        REDFISH_OBJ.logout()


def check_parameter(method, ldapserver, domainname, bind_method, client_name, client_pwd):
    if method == "Pre_Configured":
        if len(ldapserver) < 1:
            result = {"ret":False, "msg":"If you choose the pre-configured option, at least one server must be configured."}
            return result
        elif len(ldapserver) > 4:
            result = {"ret": False, "msg": "Users can specify up to four LDAP servers."}
            return result
    else:
        if not domainname:
            result = {"ret": False,
                      "msg": "If you choose the DNS option, the domain name must be configured."}
            return result

    if bind_method == "Configured":
        if client_name is None or client_pwd is None:
            result = {"ret": False,
                      "msg": "If the bind method is Configured, the client name and client password must be configured."}
            return result
    result = {"ret": True}
    return result


def add_helpmessage(argget):
    argget.add_argument('--method', type=str, choices=["Pre_Configured", "DNS"], required=True,
                        help='The LDAP servers to be used for authentication can either be manually configured or discovered dynamically via DNS SRV records.. Support:["Pre_Configured","DNS"]')
    argget.add_argument('--ldapserver', type=str, default=[], nargs="*",
                        help='If you choose the pre-configured option, at least one server must be configured.'
                             'you can configure up to 4 LDAP servers by entering each server IP address or hostname (assuming DNS is enabled).')
    argget.add_argument('--port', type=str, default=["389","389","389","389"], nargs="*",
                        help='The port number for each server is optional. If left blank, the default value of 389 is used for non-secured LDAP connections.'
                             'For secured connections, the default is 636.')
    argget.add_argument('--domainname', type=str,
                        help='This is only active under using DNS to find LDAP servers. If you choose to discover the LDAP servers dynamically, you will need to specify the search domain to be used.')

    argget.add_argument('--binding_method', type=str, choices=["Anonymously", "Configured", "Login"],
                        help='This parameter controls how this initial bind to the LDAP server is performed.Support:["Anonymously", "Configured", "Login"].'
                             'Parameter explain: "Anonymously": Bind without a DN or password. '
                             '"Configured": Bind with a DN and password. '
                             '"Login": Bind with the credentials supplied during the login process.')
    argget.add_argument('--clientdn', type=str,
                        help='Specify the Client Distinguished Name(DN) to be used for the initial bind. Note that LDAP Binding Method must be set to "Configured".')
    argget.add_argument('--clientpwd', type=str,
                        help='Note that LDAP Binding Method must be set to "Configured"')

    argget.add_argument('--rootdn', type=str,
                        help='BMC uses the "ROOT DN" field in Distinguished Name format as root entry of directory tree.This DN will be used as the base object for all searches.')
    argget.add_argument('--uid_search_attribute', type=str,
                        help='This search request must specify the attribute name used to represent user IDs on that server.'
                             'On Active Directory servers, this attribute name is usually sAMAccountName.'
                             'On Novell eDirectory and OpenLDAP servers, it is usually uid. '
                             'If this field is left blank, it defaults to uid.')

    argget.add_argument('--role_base_security', type=int, choices=[0, 1],default=0,
                        help='This parameter to enable(1) or disable(0) enhanced role-based security for Active Directory Users.')
    argget.add_argument('--servername', type=str,
                        help='This parameter configure the BMC LDAP server Target Name setting.'
                             'Note that Enhanced role-based security for Active Directory Users must be enabled for this setting to take effect.')

    argget.add_argument('--group_filter', type=str,
                        help='This field is used for group authentication, limited to 511 characters, and consists of one or more group names. '
                             'Note that Enhanced role-based security for Active Directory Users must be disabled for this setting to take effect.')
    argget.add_argument('--group_search_attribute', default="memberof", type=str,
                        help='This field is used by the search algorithm to find group membership infomation for a specific user. '
                             'Note that Enhanced role-based security for Active Directory Users must be disabled for this setting to take effect. '
                             'If this field is left blank, it will default to memberof.')
    argget.add_argument('--login_permission_attribute', type=str,
                        help='When a user successfully authenticates via a LDAP server, it is necessary to retrieve the login permissions for this user.')


def add_parameter():
    """Add set ldap server parameter"""
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["method"] = args.method
    parameter_info["ldapserver"] = args.ldapserver
    parameter_info["port"] = args.port
    parameter_info["domainname"] = args.domainname
    parameter_info["binding_method"] = args.binding_method
    parameter_info["client_distinguished_name"] = args.clientdn
    parameter_info["client_password"] = args.clientpwd
    parameter_info["rootdn"] = args.rootdn
    parameter_info["uid_search_attribute"] = args.uid_search_attribute

    parameter_info["role_base_security"] = args.role_base_security
    parameter_info["servername"] = args.servername

    parameter_info["group_filter"] = args.group_filter
    parameter_info["group_search_attribute"] = args.group_search_attribute
    parameter_info["login_permission_attribute"] = args.login_permission_attribute
    return parameter_info


if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    ip = parameter_info["ip"]
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Get set info from the parameters user specified
    try:
        method = parameter_info["method"]
        ldapserver = parameter_info["ldapserver"]
        port = parameter_info["port"]
        domainname = parameter_info["domainname"]
        binding_method = parameter_info["binding_method"]
        client_distinguished_name = parameter_info["client_distinguished_name"]
        client_password = parameter_info["client_password"]
        rootdn = parameter_info["rootdn"]
        uid_search_attribute = parameter_info["uid_search_attribute"]
        role_base_security = parameter_info["role_base_security"]
        servername = parameter_info["servername"]
        group_filter = parameter_info["group_filter"]
        group_search_attribute = parameter_info["group_search_attribute"]
        login_permission_attribute = parameter_info["login_permission_attribute"]
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Set ldap server and check result
    result = set_ldap_info(ip, login_account, login_password, method, ldapserver, port, domainname, binding_method, client_distinguished_name, client_password,
                           rootdn, uid_search_attribute, group_filter, group_search_attribute, login_permission_attribute, role_base_security, servername)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])
