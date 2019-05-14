###
#
# Lenovo Redfish examples - Set location
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

def check_param(contact,rack_name,room_no,building,lowest_u,address):
    result = {'ret': True,'msg':"check ok"}
    if len(contact) > 47:
        result = {'ret': False, 'msg': "The contact's Maximum is 47 characters."}
        sys.stderr.write(contact)
        return result
    if len(rack_name) > 47:
        result = {'ret': False, 'msg': "The rack_name's Maximum is 47 characters."}
        return result
    if len(room_no) > 47:
        result = {'ret': False, 'msg': "The room_no's Maximum is 47 characters."}
        return result
    if len(building) > 47:
        result = {'ret': False, 'msg': "The building's Maximum is 47 characters."}
        return result
    if len(address) > 300:
        result = {'ret': False, 'msg': "The address's Maximum is 300 characters."}
        return result
    if lowest_u < 1 or lowest_u > 99:
        result = {'ret': False, 'msg': "The lowest_u valid range is 1-99."}
        return result
    rang_contact = ('<','>','&')
    for i in rang_contact:
        if contact.find(i) != -1:
            result = {'ret': False, 'msg': "Special characters & < > are not allowed in contact "}
            return result

    rang_build = ('!','~','`','@','#','$','%','^','&','*','(',')','/',':',';','\\' , '\"', '\'',',','<','>','{',\
            '}','[',']','?','=','|','+')
    for i in rang_build:
        if building.find(i) != -1:
            result = {'ret': False,
                      'msg': "Special characters % ! ~ ` @ # $ % ^ & * ( ) / : ; \" ' , < > { } [ ] ? = | + are not allowed in building"}
            return result
    return result

def lenovo_set_location(ip, login_account, login_password,contact,rack_name,room_no,building,lowest_u,address):
    """Set location
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :params contact: contact by user specified
        :type contact: string
        :params rack_name: rack_name by user specified
        :type rack_name: string
        :params room_no: room_no by user specified
        :type room_no: string
        :params building: building by user specified
        :type building: string
        :params lowest_u: lowest_u by user specified
        :type lowest_u: string
        :params address: address by user specified
        :type address: string
        :returns: returns set timezone result when succeeded or error message when failed
        """

    result = {}
    result = check_param(contact,rack_name,room_no,building,lowest_u,address)
    if result['ret'] is False:
        return  result
    else:
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
    response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
    # Get response_base_url
    if response_base_url.status == 200:
        chassis_url = response_base_url.dict['Chassis']['@odata.id']
    else:
        result = {'ret': False, 'msg': " response_base_url Error code %s" % response_base_url.status}
        REDFISH_OBJ.logout()
        return result
    response_chassis_url = REDFISH_OBJ.get(chassis_url, None)
    if response_chassis_url.status == 200:
        for request in response_chassis_url.dict['Members']:
            request_url = request['@odata.id']
            response_url = REDFISH_OBJ.get(request_url, None)
            if response_url.status == 200:
                #set location url
                parameter = {"Oem":{"Lenovo":{"LocatedIn":{"Location":building,"ContactPerson":contact,\
                                                           "FullPostalAddress":address,"Rack":rack_name,\
                                                           "Room":room_no,"Position":lowest_u}}}}
                response_location_set_url = REDFISH_OBJ.patch(request_url, body=parameter)
                if response_location_set_url.status == 200:
                    result = {'ret': True, 'msg': " Set location successful"}
                    REDFISH_OBJ.logout()
                    return result
                else:
                    result = {'ret': False, 'msg': " Set location Error code %s" % response_location_set_url.status}
                    REDFISH_OBJ.logout()
                    return result
            else:
                result = {'ret': False, 'msg': "response chassis url Error code %s" % response_url.status}
                REDFISH_OBJ.logout()
                return result
    else:
        result = {'ret': False, 'msg': "response chassis url Error code %s" % response_chassis_url.status}
        REDFISH_OBJ.logout()
        return result



import argparse
def add_helpmessage(parser):
    help_str = "The Contact person allows you to specify the name and phone number of the person who should be contacted if there is a problem with this system. "
    parser.add_argument('--contact', type=str, required=True, help= help_str)
    help_str = "The Rack Name can be used to help locate the server to a particular rack.  "
    help_str += "The value is optional and is not configurable in a Flex node. "
    parser.add_argument('--rack_name', type=str, required=True, help= help_str)
    help_str = "The Room No can be used to help locate the server to a room within a data center,"
    help_str += "or for multiple data centers at a site. This could also be used to specify the floor or any other large container of racks."
    help_str += " The value is optional and is not configurable in a Flex node."
    parser.add_argument('--room_no', type=str, required=True, help= help_str)
    help_str = "The Building identifies where this system has been installed. "
    help_str +="The information in this parameter, along with Room No, Rack Name and lowest_u position (if provided) allow someone to quickly find the server when necessary for maintenance or other purposes. "
    help_str +="The value is required by SNMPv3 agent service. "
    parser.add_argument('--building', type=str, required=True, help= help_str)
    help_str = "The lowest_u can be used to help locate the server to a position within the rack. This value is not configurable in a Flex node."
    parser.add_argument('--lowest_u', type=int, required=True, help= help_str)
    help_str = "The Address is optional for full postal address."
    parser.add_argument('--address', type=str, required=True, help= help_str)


def add_parameter():
    """Add set location parameter"""
    parameter_info = {}
    argget = utils.create_common_parameter_list()
    add_helpmessage(argget)
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["contact"] = args.contact
    parameter_info["rack_name"] = args.rack_name
    parameter_info["room_no"] = args.room_no
    parameter_info["building"] = args.building
    parameter_info["lowest_u"] = args.lowest_u
    parameter_info["address"] = args.address
    return parameter_info

if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    try:
        ip = parameter_info["ip"]
        login_account = parameter_info["user"]
        login_password = parameter_info["passwd"]
        contact = parameter_info["contact"]
        rack_name = parameter_info["rack_name"]
        room_no = parameter_info["room_no"]
        building = parameter_info["building"]
        lowest_u = parameter_info["lowest_u"]
        address = parameter_info["address"]
    except:
        sys.stderr.write("Please run the coommand 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)
    #set location and get result
    result = lenovo_set_location(ip, login_account, login_password, contact,rack_name,room_no,building,lowest_u,address)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])