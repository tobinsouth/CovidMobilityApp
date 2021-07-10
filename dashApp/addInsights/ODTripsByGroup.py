from .ReportRequest import *
from datetime import *
import pandas as pd

class ODTripsByGroupReportData:
    def __init__(self, originGroupId, destGroupId, value, intervalTime):
        self.originGroupId = originGroupId
        self.destGroupId = destGroupId
        self.value = value
        self.intervalTime = datetime.strptime(intervalTime, '%Y-%m-%dT%H:%M:%S%z')
    @classmethod
    def from_json(cls, data):
        originGroupId = data[0]
        destGroupId = data[1]
        value = data[2]
        intervalTime = data[3][:-3] + data[3][-2:] #remove extra colon
        return cls(originGroupId, destGroupId, value, intervalTime)

class ODTripsByGroupReportGrouping:
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
        data = list(map(ODTripsByGroupReportData.from_json, data["data"]))
        return cls(header, dataset, data)


class ODTripsByGroupReport(ReportRequestBase):
    def __init__(self, addinsightConnection:Addinsight, startDate:datetime, endDate:datetime, 
            startTimeOfDay=None, endTimeOfDay=None, daysOfWeek=[], 
            excludeSpecialDayTypeIds=[], includeSpecialDayTypeIds=[], 
            aggregate=None, aggregateMerge=None, 
            originGroupIds=[], destGroupIds=[], SourceIdTypes=[], 
            includeTrackedVehicleTypeIds=[], excludeTrackedVehicleTypeIds=[]):
        super(ODTripsByGroupReport, self).__init__(addinsightConnection, startDate, endDate, 
            startTimeOfDay, endTimeOfDay, daysOfWeek, 
            excludeSpecialDayTypeIds, includeSpecialDayTypeIds,
            aggregate, aggregateMerge)
        self.query_parameters['template'] = 'templates/od_trips_by_group'
        self.query_parameters['origin_group_ids'] = ','.join(map(str, originGroupIds))
        self.query_parameters['dest_group_ids'] = ','.join(map(str, destGroupIds))
        self.query_parameters['source_id_types'] = ','.join(map(str, SourceIdTypes))
        self.query_parameters['include_tracked_vehicle_type_ids'] = ','.join(map(str, includeTrackedVehicleTypeIds))
        self.query_parameters['exclude_tracked_vehicle_type_ids'] = ','.join(map(str, excludeTrackedVehicleTypeIds))
        self.query_parameters['group_dataset_by'] = ','.join(['origin_group_id', 'dest_group_id'])
        self.url = 'reports/execute_query/probe_od_trips_by_group?'
        self.results = []
        self.extractData()

    def extractData(self):
        response = self.addinsight_connection.get(self.url, self.query_parameters)
        if response is not None:
            if isinstance(response, Error):
                # print(str(response))
                print('Response isinstance of Error.')
                return
            else:
                # print(response)
                for r in response:
                    if type(r) == dict:
                        reportGrouping = ODTripsByGroupReportGrouping.from_json(r)
                        self.results.append(reportGrouping)
                    else:
                        print('Not dict response')
            print('ODTripsByGroup data extracted')
        else:
            print('[!] Request Failed. No Response')


    def createFlowList(self):
        flow_data_long = []
        for result in self.results:
            for data in result.data:
                row = [data.destGroupId, data.originGroupId, data.value, data.intervalTime]
                flow_data_long.append(row)
        flow_data_long_df = pd.DataFrame(flow_data_long, 
                columns = ['destGroupId', 'originGroupId', 'value', 'intervalTime'])
        return flow_data_long_df

    # def aggregateResultsPerDatePerGroupByOrigin(self, groups:[]):
    #     aggregatedResults = {}
    #     for result in self.results:
    #         for data in result.data:
    #             if data.intervalTime not in aggregatedResults:
    #                 aggregatedResults[data.intervalTime] = {}
    #             if data.originGroupId not in aggregatedResults[data.intervalTime]:
    #                 aggregatedResults[data.intervalTime][data.originGroupId] = {}
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['total'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['change'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['changepercent'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['external_total'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['external_change'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['external_changepercent'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['internal_total'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['internal_change'] = 0
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['internal_changepercent'] = 0
    #             aggregatedResults[data.intervalTime][data.originGroupId]['total'] += data.value
    #             if data.originGroupId != data.destGroupId:
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['external_total'] += data.value
    #             else:
    #                 aggregatedResults[data.intervalTime][data.originGroupId]['internal_total'] += data.value
    #     for group in groups:
    #         # Find the max value for all time intervals for the group
    #         maxTotalValue = 0
    #         maxInternalValue = 0
    #         maxExternalValue = 0
    #         for intervalTime in aggregatedResults:
    #             if group.id in aggregatedResults[intervalTime]:
    #                 if aggregatedResults[intervalTime][group.id]['total'] > maxTotalValue:
    #                     maxTotalValue = aggregatedResults[intervalTime][group.id]['total']
    #                 if aggregatedResults[intervalTime][group.id]['internal_total'] > maxInternalValue:
    #                     maxInternalValue = aggregatedResults[intervalTime][group.id]['internal_total']
    #                 if aggregatedResults[intervalTime][group.id]['external_total'] > maxExternalValue:
    #                     maxExternalValue = aggregatedResults[intervalTime][group.id]['external_total']
    #         # Calculate the change values
    #         for intervalTime in aggregatedResults:
    #             if group.id in aggregatedResults[intervalTime]:
    #                 if maxTotalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['change'] = aggregatedResults[intervalTime][group.id]['total'] - maxTotalValue
    #                     aggregatedResults[intervalTime][group.id]['changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['change'] / maxTotalValue, 0)
    #                 if maxInternalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['internal_change'] = aggregatedResults[intervalTime][group.id]['internal_total'] - maxInternalValue
    #                     aggregatedResults[intervalTime][group.id]['internal_changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['internal_change'] / maxInternalValue, 0)
    #                 if maxExternalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['external_change'] = aggregatedResults[intervalTime][group.id]['external_total'] - maxExternalValue
    #                     aggregatedResults[intervalTime][group.id]['external_changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['external_change'] / maxExternalValue, 0)

    #     return aggregatedResults

    # def aggregateResultsPerDatePerGroupByDestination(self, groups:[]):
    #     aggregatedResults = {}
    #     for result in self.results:
    #         for data in result.data:
    #             if data.intervalTime not in aggregatedResults:
    #                 aggregatedResults[data.intervalTime] = {}
    #             if data.destGroupId not in aggregatedResults[data.intervalTime]:
    #                 aggregatedResults[data.intervalTime][data.destGroupId] = {}
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['total'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['change'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['changepercent'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['external_total'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['external_change'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['external_changepercent'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['internal_total'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['internal_change'] = 0
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['internal_changepercent'] = 0
    #             aggregatedResults[data.intervalTime][data.destGroupId]['total'] += data.value
    #             if data.destGroupId != data.originGroupId:
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['external_total'] += data.value
    #             else:
    #                 aggregatedResults[data.intervalTime][data.destGroupId]['internal_total'] += data.value
    #     for group in groups:
    #         # Find the max value for all time intervals for the group
    #         maxTotalValue = 0
    #         maxInternalValue = 0
    #         maxExternalValue = 0
    #         for intervalTime in aggregatedResults:
    #             if group.id in aggregatedResults[intervalTime]:
    #                 if aggregatedResults[intervalTime][group.id]['total'] > maxTotalValue:
    #                     maxTotalValue = aggregatedResults[intervalTime][group.id]['total']
    #                 if aggregatedResults[intervalTime][group.id]['internal_total'] > maxInternalValue:
    #                     maxInternalValue = aggregatedResults[intervalTime][group.id]['internal_total']
    #                 if aggregatedResults[intervalTime][group.id]['external_total'] > maxExternalValue:
    #                     maxExternalValue = aggregatedResults[intervalTime][group.id]['external_total']
    #         # Calculate the change values
    #         for intervalTime in aggregatedResults:
    #             if group.id in aggregatedResults[intervalTime]:
    #                 if maxTotalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['change'] = aggregatedResults[intervalTime][group.id]['total'] - maxTotalValue
    #                     aggregatedResults[intervalTime][group.id]['changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['change'] / maxTotalValue, 0)
    #                 if maxInternalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['internal_change'] = aggregatedResults[intervalTime][group.id]['internal_total'] - maxInternalValue
    #                     aggregatedResults[intervalTime][group.id]['internal_changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['internal_change'] / maxInternalValue, 0)
    #                 if maxExternalValue > 0:
    #                     aggregatedResults[intervalTime][group.id]['external_change'] = aggregatedResults[intervalTime][group.id]['external_total'] - maxExternalValue
    #                     aggregatedResults[intervalTime][group.id]['external_changepercent'] = round(100.0 * aggregatedResults[intervalTime][group.id]['external_change'] / maxExternalValue, 0)

    #     return aggregatedResults