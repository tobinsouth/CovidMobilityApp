from enum import Enum
from datetime import *
from .Addinsight import Addinsight
from .Errors import Error

class TimePeriodicAggregationEnum(Enum):
    OneSecondOfDay = 'one_second_of_day'
    FifteenSecondOfDay = 'fifteen_second_of_day'
    ThirtySecondOfDay = 'thirty_second_of_day'
    OneMinuteOfDay = 'one_minute_of_day'
    FiveMinuteOfDay = 'five_minute_of_day'
    TenMinuteOfDay = 'ten_minute_of_day'
    FifteenMinuteOfDay = 'fifteen_minute_of_day'
    TwentyMinuteOfDay = 'twenty_minute_of_day'
    ThirtyMinuteOfDay = 'thirty_minute_of_day'
    HourOfDay = 'hour_of_day'
    DayOfWeek = 'day_of_week'

class AggregationOptionsEnum(Enum):
    NONE = 'none'
    FifteenSecond = 'fifteen_second'
    ThirtySecond = 'thirty_second'
    OneMinute = 'one_minute'
    FiveMinute = 'five_minute'
    TenMinute = 'ten_minute'
    FifteenMinute = 'fifteen_minute'
    TwentyMinute = 'twenty_minute'
    ThirtyMinute = 'thirty_minute'
    Hour = 'hour'
    Day = 'day'
    Week = 'week'
    Month = 'month'
    Year = 'year'
    EntireRange = 'entire_range'
    TimeOfDay = 'time_of_day'

class ReportData: # The structure of the data will depend on each report request type
    def __init__(self):
        pass
    @classmethod
    def from_json(cls):
        return cls()

class ReportDataset:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value
    @classmethod
    def from_json(cls, data):
        name = data["name"]
        type = data["type"]
        value = data["value"]
        return cls(name, type, value)
    def __eq__(self, other): 
        if not isinstance(other, ReportDataset):
            return False
        return self.name == other.name and self.type == other.type and self.value == other.value

class ReportHeader:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    @classmethod
    def from_json(cls, data):
        name = data["name"]
        type = data["type"]
        return cls(name, type)

class ReportGrouping:
    def __init__(self, header, dataset, data):
        self.header = header
        self.dataset = dataset
        self.data = data

    def __getitem__(self, key):
        return getattr(self, key)
    
    @classmethod
    def from_json(cls, data: dict):
        header = list(map(ReportHeader.from_json, data["header"]))
        dataset = list(map(ReportDataset.from_json, data["dataset"]))
        data = list(map(ReportData.from_json, data["data"])) # The structure of the data will depend on each report request type
        return cls(header, dataset, data)

class ReportRequestBase:
    def __init__(self, addinsightConnection:Addinsight, startDate:datetime, endDate:datetime, 
            startTimeOfDay=None, endTimeOfDay=None, daysOfWeek=[], 
            excludeSpecialDayTypeIds=[], includeSpecialDayTypeIds=[], 
            aggregate=None, aggregateMerge=None):
        self.addinsight_connection = addinsightConnection
        self.startDate = startDate
        self.endDate = endDate
        self.startTimeOfDay = startTimeOfDay
        self.endTimeOfDay = endTimeOfDay
        self.query_parameters = {}
        self.query_parameters['template'] = ''
        self.query_parameters['start_date'] = startDate
        self.query_parameters['end_date'] = endDate
        self.query_parameters['start_time_of_day'] = None if startTimeOfDay == None else startTimeOfDay
        self.query_parameters['end_time_of_day'] = None if startTimeOfDay == None else endTimeOfDay
        self.query_parameters['days_of_week'] = ','.join(daysOfWeek)
        self.query_parameters['exclude_special_day_type_ids'] = ','.join(map(str, excludeSpecialDayTypeIds))
        self.query_parameters['include_special_day_type_ids'] = ','.join(map(str, includeSpecialDayTypeIds))
        self.query_parameters['aggregate'] = aggregate
        self.query_parameters['aggregate_merge'] = aggregateMerge
        self.query_parameters['group_dataset_by'] = None
        self.url = ''
        self.results = []

    def extractData(self): # Exists for inheritance purposes
        pass

    # def findResultByDataset(self, other):
    #     for x in self.results:
    #         found = True
    #         for i in range(len(x.dataset)):
    #             if x.dataset[i] != other[i]:
    #                 found = False
    #                 break
    #         if found:
    #             return x
    #     return None