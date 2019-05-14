###
#
# Lenovo Redfish examples - Set IPv4 server
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

def set_ipv4(ip, login_account, login_password, method, ipv4address, netmask, gateway):
    """set bmc ipv4
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :params method: Specify the IPv4 configuration methods
        :type method: string
        :params ipv4address: The value of this property shall be an IPv4 address assigned to this interface
        :type ipv4address: string
        :params netmask: The value of this property shall be the IPv4 subnet mask for this address
        :type netmask: string
        :params gateway: The value of this property shall be the IPv4 default gateway address for this interface
        :type gateway: string
        :returns: returns set bmc ipv4 result when succeeded or error message when failed
        """

    result = {}
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
                #Get Ethernet Interfaces url
                if response_url.status == 200:
                    interfaces_url = response_url.dict["EthernetInterfaces"]['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result

                # Get the NIC url form the interfaces url response
                response_interfaces_url = REDFISH_OBJ.get(interfaces_url, None)
                if response_interfaces_url.status == 200:
                    member_list = response_interfaces_url.dict["Members"]
                else:
                    error_message = utils.get_extended_error(response_interfaces_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        interfaces_url, response_interfaces_url.status, error_message)}
                    return result

                for member in member_list:
                    member_url = member["@odata.id"]
                    if "NIC" in member_url:
                        response_nic_url = REDFISH_OBJ.get(member_url, None)
                        if response_nic_url.status == 200:
                            ipv4_address = response_nic_url.dict["IPv4Addresses"]
                        else:
                            error_message = utils.get_extended_error(response_nic_url)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                                member_url, response_nic_url.status, error_message)}
                            return result
                        if len(ipv4_address) == 1:
                            ipv4_address[0] = {"Address": ipv4address,
                                               "SubnetMask": netmask,
                                               "Gateway": gateway,
                                               "AddressOrigin": method
                                               }
                        else:
                            if method in ["Static", "DHCPFirstThenStatic"]:
                                if ipv4address is None or netmask is None or gateway is None:
                                    result = {'ret':False, 'msg':"When the method is static or DHCPFirstThenStatic, the user needs to specify ipv4address, netmask and gateway."}
                                    return result
                                ipv4_address[0] = {"Address": ipv4address,
                                    "SubnetMask": netmask,
                                    "Gateway": gateway,
                                    "AddressOrigin": method
                                    }
                            elif method == "DHCP":
                                ipv4_address[1] = {"AddressOrigin": method}
                            else:
                                result = {'ret': False,
                                          'msg': "Please check the IPv4 configuration methods is correct, only support 'Static' or 'DHCP'."}
                                return result

                        # Modified the ethernet configuration through patch request
                        body = {"IPv4Addresses":ipv4_address,"Oem":{"Lenovo": {"IPv4AddressAssignedby": method}}}
                        response_nic_url = REDFISH_OBJ.patch(member_url, body=body)
                        if response_nic_url.status == 200:
                            result = {'ret': True, 'msg': "The Ethernet configuration settings '%s' successfully" %method}
                            return result
                        else:
                            error_message = utils.get_extended_error(response_nic_url)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                                member_url, response_nic_url.status, error_message)}
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


def add_helpmessage(parser):
    parser.add_argument('--method', type=str, required=True, choices= ["DHCP", "Static", "DHCPFirstThenStatic"], help='Specify the IPv4 configuration methods, Support:["DHCP", "Static", "DHCPFirstThenStatic"]'
                                                   'When specified the DHCP option, an IP address will be obtained through a Dynamic Host Configuration Protocol (DHCP) server on your network'
                                                   'When specified the static ip address, user need specify other parameter.')
    parser.add_argument('--ipv4address', type=str, help='The value of this property shall be an IPv4 address assigned to this interface. '
                                                        'If DHCPv4 is enabled on the interface, this property becomes read-only')
    parser.add_argument('--netmask', type=str, help='The value of this property shall be the IPv4 subnet mask for this address. '
                                                                             'If DHCPv4 is enabled on the interface, this property becomes read-only')
    parser.add_argument('--gateway', type=str, help='The value of this property shall be the IPv4 default gateway address for this interface. '
                                                    'If DHCPv4 is enabled on the interface and is configured to set the IPv4 default gateway address, this property becomes read-only')


def add_parameter():
    """Add set bmc IPv4 parameter"""
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    if args.method is not None:
        parameter_info["method"] = args.method
    parameter_info["ipv4address"] = args.ipv4address
    parameter_info["netmask"] = args.netmask
    parameter_info["gateway"] = args.gateway
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
        method = parameter_info["method"]
        ipv4address = parameter_info["ipv4address"]
        netmask = parameter_info["netmask"]
        gateway = parameter_info["gateway"]
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Set bmc IPv4 and check result
    result = set_ipv4(ip, login_account, login_password, method, ipv4address, netmask, gateway)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])