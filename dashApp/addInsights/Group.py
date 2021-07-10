from typing import List
from enum import Enum
from .Errors import Error
from .Addinsight import *

class GroupObjectTypeEnum(Enum):
    Camera = 'camera'
    CounterSite = 'counter_site'
    Device = 'device'
    Link = 'link'
    Route = 'route'
    Site = 'site'
    StaticBeacon = 'static_beacon'
    VariableMessageSign = 'variable_message_sign'
    SchoolCrossing = 'school_crossing'

class GroupObject:
    def __init__(self, object_id, group_object_type:GroupObjectTypeEnum):
        self.id = object_id
        self.groupObjectType = group_object_type
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    @classmethod
    def from_json(cls, data):
        id = data["object_id"]
        groupObjectType = GroupObjectTypeEnum(data["group_object_type"])
        return cls(id, groupObjectType)

class Group():
    def __init__(self, id, name, coordinates, includedObjects: List[GroupObject]):
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.includedObjects = includedObjects

    def __getitem__(self, key):
        return getattr(self, key)
    
    @classmethod
    def from_json(cls, data: dict):
        id = data["id"]
        name = data["name"]
        coordinates = data["coordinates"]
        includedObjects = list(map(GroupObject.from_json, data["included_objects"]))
        return cls(id, name, coordinates, includedObjects)
    
    # def GetIncludedObjectIdsForType(self, objectType:GroupObjectTypeEnum):
    #     objectIds = []
    #     for o in self.includedObjects:
    #         if o.groupObjectType == objectType:
    #             objectIds.append(o.id)
    #     return objectIds
    
    def GetAsFeature(self, data:dict = {}):
        feature = {}
        feature['type'] = 'Feature'
        feature['geometry'] = {}
        feature['geometry']['type'] = 'Polygon'
        feature['geometry']['coordinates'] = []
        feature['geometry']['coordinates'].append([])
        feature['geometry']['coordinates'][0] = self.coordinates
        feature['properties'] = {}
        feature['properties']['name'] = self.name
        feature['properties']['id'] = self.id
        for item in data:
            feature['properties'][item] = data[item]
        return feature

class GroupRequest():
    def __init__(self, addinsightConnection:Addinsight, expandProperties, categoryNameFilter):
        self.url = 'groups?'
        self.addinsight_connection = addinsightConnection
        self.request_parameters = {}
        self.request_parameters['expand'] = ','.join(expandProperties)
        self.request_parameters['category_name'] = categoryNameFilter
        self.groups = []
        self.extractData()

    def __getitem__(self, key):
        return getattr(self, str(key))

    def extractData(self):
        response = self.addinsight_connection.get(self.url, self.request_parameters)
        if response is not None:
            if isinstance(response, Error):
                print(str(response))
                return
            else:
                for g in response:
                    grp = Group.from_json(g)
                    self.groups.append(grp)

    def getGroupIds(self):
        groupIds = []
        for g in self.groups:
            groupIds.append(g.id)
        return groupIds


    def getGeoJson(self, saveName=None):
        """
        Extracts geo-features that already exist in this GroupRequest object inside of `self.groups`.

        If saveName exists then the file will be saved at that path. Either way it returns the GeoJson dictionary.

        Returns:
            A dictionary with a GeoJson string containing feature geometries. 
        """
        outputGeoJson = {}
        outputGeoJson['type'] = 'FeatureCollection'
        outputGeoJson['features'] = [g.GetAsFeature() for g in self.groups]

        if saveName:
            with open(saveName, 'w') as f:
                json.dump(outputGeoJson, f)

        return outputGeoJson


    # def getGeoJson(self, stats:dict, filePrefix:str):
    #     """
    #     Deprecated.
    #     Loops through each day and extracts the geo-features for each id that appears on that day.
    #     These geo-features already exist in this GroupRequest object inside of `self.groups`.
    #     """
        
    #     for intervalTime in stats: # Loops through days
    #         outputGeoJson = {}
    #         outputGeoJson['type'] = 'FeatureCollection'
    #         outputGeoJson['features'] = []
    #         for g in self.groups:
    #             if g.id in stats[intervalTime]:
    #                 outputGeoJson['features'].append(g.GetAsFeature(stats[intervalTime][g.id]))
    #         data = json.dumps(outputGeoJson, default=lambda o: o.__dict__,separators=(',', ':'))
    #         f = open(filePrefix + intervalTime.strftime("%Y_%m_%dT%H_%M") + "_geo.json", "w")
    #         f.write(data)
    #         f.close()


