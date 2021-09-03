#!/usr/bin/env python3
__author__ = 'stephane.ploix@g-scop.grenoble-inp.fr'
__all__ = []

import http.client
import json
import datetime
from time import strftime, localtime, strptime, mktime
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom


def toEpochMsDate(datestring):
    try:
        thedate = mktime(strptime(datestring, '%d/%m/%Y %H:%M:%S'))
    except (OverflowError, ValueError):
        thedate = mktime(strptime(datestring + ' 0:0:0', '%d/%m/%Y %H:%M:%S'))
    return int(thedate) * 1000


def toStringDate(epochmsDate):
    return strftime('%d/%m/%Y %H:%M:%S', localtime(epochmsDate // 1000))


def toDatetime(epochmsDate):
    return datetime.datetime.fromtimestamp(epochmsDate // 1000)


def getDatetimeWithDayDelta(numberofdays: int=0):
    return (datetime.datetime.now() - datetime.timedelta(days=numberofdays)).strftime('%d/%m/%Y %H:%M:%S')


class HttpConnector():
    def __init__(self, sitename: str='InpgViallet'):
        """
        :param sitename: InpgViallet or Predis
        """
        self.webserviceurl = '37.187.134.115'
        self.serverPORT = 80
        self.timeout = 3600
        self.user = 'stephane.ploix'
        self.password = 'malone38'
        self.webserviceprefix = '/' + sitename + '/service/'
        self.sitename = sitename
        self.site_element = Element('site', attrib={'name':sitename})
        self.buildings = list()
        buildingsdata = json.loads(self.requestService('getBuildingList', {'format': 'compact_json'}))
        for buildingdata in buildingsdata:
            building = Building(buildingdata['Id'], buildingdata['Label'], buildingdata['State'])
            self.buildings.append(building)
            building_element = Element('building', attrib={'name':buildingdata['Id']})
            self.site_element.append(building_element)
            floorsdata = json.loads(self.requestService('getAllServiceVariables', {'building': buildingdata['Id'], 'format': 'compact_json', 'sort': 'byTopology'}))[buildingdata['Id']]['floors']
            for floordata in floorsdata:
                floor = Floor(floorsdata[floordata]['name'])
                building.addFloor(floor)
                floor_element = Element('floor', attrib={'name':floorsdata[floordata]['name']})
                building_element.append(floor_element)
                zonesdata = floorsdata[floordata]['zones']
                for zonedata in zonesdata:
                    zoneName = zonesdata[zonedata]['name']
                    zone = Zone(zoneName)
                    floor.addZone(zone)
                    zone_element = Element('zone', attrib={'name':zoneName})
                    floor_element.append(zone_element)
                    servicesdata = zonesdata[zonedata]['services']
                    for servicedata in servicesdata:
                        deviceID = servicedata
                        device = Device(deviceID, servicesdata[deviceID]['device']['name'], float(servicesdata[deviceID]['device']['x']), float(servicesdata[deviceID]['device']['y']))
                        zone.addDevice(device)
                        device_element = Element('device', attrib={'name': servicesdata[deviceID]['device']['name']})
                        zone_element.append(device_element)
                        variablesdata = servicesdata[deviceID]['variables']
                        for variabledata in variablesdata:
                            if variabledata['value'] != 'null':
                                variable = Variable(variabledata['name'], variabledata['value'], variabledata['unit'], self)
                            else:
                                variable = Variable(variabledata['name'], 0, variabledata['unit'], self)
                            device.addVariable(variable)
                            variable_element = Element('variable', attrib={'name': variabledata['name'], 'select':'no'})
                            device_element.append(variable_element)

    def requestService(self, service: str, parameters: dict=None)->str:
        connection = http.client.HTTPConnection(self.webserviceurl, self.serverPORT, timeout=self.timeout)
        service = self.webserviceprefix + service + '.php?user=' + self.user + '&password=' + self.password
        if parameters is not None:
            for parameterName in parameters:
                service = service + '&' + parameterName + '=' + str(parameters[parameterName])
        print('\nhttp://' + self.webserviceurl + ':' + str(self.serverPORT) + service)
        try:
            connection.request('GET', service)
            response = connection.getresponse()
        except http.client.HTTPException:
            print('Http connection is out!')
        message = response.read().decode('utf-8')
        connection.close()
        return message

    def getBuildings(self)->list:
        return self.buildings

    def getBuilding(self, name: str):
        for building in self.buildings:
            if building.name == name:
                return building
        return None

    def generateSetupFile(self, file_name: str = None):
        if file_name is None:
            file_name = self.sitename
        raw_xml_string = tostring(self.site_element, method='xml', encoding='UTF-8')
        xml_document = minidom.parseString(raw_xml_string)
        pretty_xml_string = xml_document.toprettyxml(indent='\t', encoding='UTF-8').decode('UTF-8')
        with open(file_name + '.xml', 'w') as file:
            file.write(pretty_xml_string) # xml_declaration=True, pretty_print=True


class Building():

    def __init__(self, name: str, label: str, state: str):
        self.name = name
        self.label = label
        self.state = state
        self.floors = list()

    def addFloor(self, floor):
        floor.setBuilding(self)
        self.floors.append(floor)

    def getFloors(self)->list:
        return self.floors

    def getFloor(self, name: str):
        for floor in self.floors:
            if floor.name == name:
                return floor
        return None

    def __str__(self):
        string = '\nbuildingID: ' + self.name + ' label: ' + self.label + ' state: ' + self.state
        for floor in self.floors:
            string += floor.__str__()
        return string


class Floor():

    def __init__(self, name: str):
        self.name = name
        self.zones = list()
        self.building = None

    def setBuilding(self, building):
        self.building = building

    def addZone(self, zone):
        zone.setFloor(self)
        self.zones.append(zone)

    def getZones(self):
        return self.zones

    def getZone(self, name: str):
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def __str__(self):
        string = '\n\tfloor: ' + self.name
        for zone in self.zones:
            string += zone.__str__()
        return string


class Zone():

    def __init__(self, name: str):
        self.name = name
        self.devices = list()
        self.building = ''
        self.floor = None

    def setFloor(self, floor):
        self.floor = floor

    def addDevice(self, device):
        device.setZone(self)
        self.devices.append(device)

    def getDevices(self):
        return self.devices

    def getDevice(self, name: str):
        for device in self.devices:
            if device.name == name:
                return device
        return None

    def __str__(self):
        string = '\n\t\tzone: ' + self.name
        for device in self.devices:
            string += device.__str__()
        return string


class Device():

    def __init__(self, identifier: str, name: str, x: float, y: float):
        self.id = identifier
        self.name = name
        self.x = x
        self.y = y
        self.variables = list()
        self.zone = None

    def setZone(self, zone):
        self.zone = zone

    def addVariable(self, variable):
        variable.addDevice(self)
        self.variables.append(variable)

    def getVariables(self):
        return self.variables

    def getVariable(self, name: str):
        for variable in self.variables:
            if variable.name == name:
                return variable
        return None

    def __str__(self):
        string = '\n\t\t\tdevice: ' + self.name
        for variable in self.variables:
            string += variable.__str__()
        return string


class Variable():

    def __init__(self, name: str, value, unit: str, httpconnector):
        self.name = name
        self.value = value
        self.unit = unit
        self.device = None
        self.httpconnector = httpconnector

    def addDevice(self, device):
        self.device = device

    def getHistory(self, startdate: str=None, enddate: str=None):
        if enddate is None:
            enddate = toEpochMsDate(getDatetimeWithDayDelta())
        else:
            enddate = toEpochMsDate(enddate)
        if startdate is None:
            startdate = enddate - 24 * 3600 * 1000
        else:
            startdate = toEpochMsDate(startdate)
        historydata = json.loads(self.httpconnector.requestService('getVariableHistory', {'service': self.device.id, 'variable': self.name, 'format': 'compact_json', 'start': startdate, 'end': enddate, 'building': self.device.zone.floor.building.name}))['variable']['history']
        values = list()
        for data in historydata:
            values.append(Value(data[0], data[1]))
        return VariableValues(self, values)

    def __str__(self):
        return '\n\t\t\t\tvariable: ' + self.name + ' (current value: ' + str(self.value) + self.unit + ')'


class Value():

    def __init__(self, epochtime, value):
        self.epochtime = int(epochtime)
        if value != 'null':
            self.value = value
        else:
            self.value = 0

    def get(self):
        return self.value

    def getEpochTimeInMs(self):
        return self.epochtime

    def getDatetime(self):
        return datetime.datetime.fromtimestamp(self.epochtime / 1000)

    def getTimestamp(self):
        return toStringDate(self.epochtime)

    def __str__(self):
        return self.getTimestamp() + ': ' + str(self.value)


class VariableValues():

    def __init__(self, variable, values):
        self.variable = variable
        self.values = values

    def getValues(self):
        return self.values

    def __str__(self):
        string = self.variable.__str__()
        for value in self.values:
            string += '\n' + value.__str__()
        return string


class VariableDataset():

    def __init__(self, site: str, building: str, floor: str, zone: str, device: str, variable: str, startdate: str, enddate: str=None):  # date format: '17/02/2015 00:00:00':
        self.site = site
        self.building = building
        self.floor = floor
        self.zone = zone
        self.device = device
        self.variable = variable
        building = HttpConnector(site).getBuilding(building)
        self.values = dict()
        for value in building.getFloor(floor).getZone(zone).getDevice(device).getVariable(variable).getHistory(startdate=startdate, enddate=enddate).getValues():
            self.values[value.getEpochTimeInMs()] = float(value.get())
        self.epochtimes = list(self.values.keys())
        self.epochtimes.sort()

    def getEpochTimes(self):
        return self.epochtimes

    def getValue(self, epochtime):
        return self.values[epochtime]

    def getValues(self, epochtimes=None):
        if epochtimes is None:
            epochtimes = self.epochtimes
        return [self.values[epochtime] for epochtime in epochtimes]

if __name__ == '__main__':
    HttpConnector('InpgViallet').generateSetupFile('H358')
    #HttpConnector('Predis').generateSetupFile('H358')
