import json
import requests
import time

class Addinsight:
    def __init__(self, token:str, base_url:str, resubmit_delay:float, resubmit_attempts:int, secureConnection=True):
        self.token = token
        self.base_url = base_url
        self.resubmit_delay = resubmit_delay
        self.resubmit_attempts = resubmit_attempts
        self.secure_connection = secureConnection
        self.headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(token)}
        url = '{0}/api'.format(self.base_url)
        response = requests.get(url=url, headers=self.headers, verify=self.secure_connection)
        if response.status_code != 200:
            e = json.loads(response.content.decode('utf-8'))
            raise Exception('Connection to Addinsight failed. {0}'.format(e))

        self.last_request = json.loads(response.content.decode('utf-8'))

    def get(self, apppendUrl:str, params:dict):
        url = '{0}/api/{1}'.format(self.base_url, apppendUrl)

        response = requests.get(url=url, headers=self.headers, params=params, verify=self.secure_connection)
        self.last_request = json.loads(response.content.decode('utf-8'))

        if response.status_code == 200: #Ok
            return json.loads(response.content.decode('utf-8'))
        elif response.status_code == 202: #Accepted
            print('Failed request, resubmitting.')
            counter = 0
            while counter < self.resubmit_attempts:
                time.sleep(self.resubmit_delay)
                response = requests.get(url=url, headers=self.headers, verify=self.secure_connection)
                if response.status_code == 200: #Ok
                    return json.loads(response.content.decode('utf-8'))
                elif response.status_code == 202: #Accepted
                    counter+=1
                else:
                    print('Failed resubmit - was not 200 or 202.')
                    return None
        elif response.status_code in [401,403,404,422]:
            return json.loads(response.content.decode('utf-8'))
        else:
            print('Response code not recognised.')
            return None
    
    # def post(self, apppendUrl:str, data:dict):
    #     url = '{0}/api/{1}'.format(self.base_url, apppendUrl)

    #     response = requests.post(url=url, headers=self.headers, data=data, verify=self.secure_connection)

    #     if response.status_code == 200 or response.status_code == 201:#Ok or Created
    #         return json.loads(response.content.decode('utf-8'))
    #     elif response.status_code in [401,403,404,422]:
    #         return json.loads(response.content.decode('utf-8'))
    #     else:
    #         return None
    
    # def patch(self, apppendUrl:str, data:dict):
    #     url = '{0}/api/{1}'.format(self.base_url, apppendUrl)

    #     response = requests.patch(url=url, headers=self.headers, data=data, verify=self.secure_connection)

    #     if response.status_code == 200:#Ok
    #         return json.loads(response.content.decode('utf-8'))
    #     elif response.status_code in [401,403,404,422]:
    #         return json.loads(response.content.decode('utf-8'))
    #     else:
    #         return None
    
    # def delete(self, apppendUrl:str):
    #     url = '{0}/api/{1}'.format(self.base_url, apppendUrl)

    #     response = requests.delete(url=url, headers=self.headers, verify=self.secure_connection)

    #     if response.status_code == 204:#No Content
    #         return json.loads(response.content.decode('utf-8'))
    #     elif response.status_code in [401,403,404,422]:
    #         return json.loads(response.content.decode('utf-8'))
    #     else:
    #         return None
