import requests
import time
from typing import Dict, List, Optional


class B24Service:
    """Service for working with Bitrix24 API"""

    def __init__(self, domain: str, user_id: int, token: str):
        self.domain = domain
        self.user_id = user_id
        self.token = token

    def get(self, url: str, params: dict = None):
        """GET request to Bitrix24 API"""
        resp = requests.get(
            f'https://{self.domain}/rest/{self.user_id}/{self.token}/{url}',
            params=params
        )
        return resp

    def post(self, url: str, json: dict = None, data: dict = None, files: dict = None, wait_for_limit: bool = False):
        """POST request to Bitrix24 API"""
        if wait_for_limit:
            for k in range(0, 5):
                time.sleep(k * 10)
                resp = requests.post(
                    f'https://{self.domain}/rest/{self.user_id}/{self.token}/{url}',
                    json=json, files=files, data=data
                )
                if 'error' not in resp.json().keys():
                    return resp

        resp = requests.post(
            f'https://{self.domain}/rest/{self.user_id}/{self.token}/{url}',
            json=json, files=files, data=data
        )
        return resp

    def get_list(
        self,
        url: str,
        b24_filter: dict = None,
        select: list = None,
        entityTypeId: int = None,
        total_count_only: bool = False
    ) -> List[Dict]:
        """Get list of entities from Bitrix24 with pagination"""
        entities = []
        start_pos = 0
        total = 1

        while start_pos < total:
            data = {'start': start_pos, 'filter': b24_filter}
            if entityTypeId:
                data['entityTypeId'] = entityTypeId
            if select:
                data['select'] = select

            response = self.post(url, json=data).json()

            if 'error' in response.keys():
                if response['error'] == 'QUERY_LIMIT_EXCEEDED':
                    time.sleep(5)
                    print('delay 5s')
                    continue

            start_pos += 50

            if 'total' not in response:
                print('No total key in response:', response)
                total = None
            else:
                total = response['total']

            if total_count_only:
                return total

            if start_pos == 50:
                print(url, 'Total_count =', total)

            if start_pos % 1000 == 0:
                time.sleep(1)
                print('delay 1s')

            result = response['result']
            if entityTypeId:
                result = result['items']

            for entity in result:
                entities.append(entity)

        return entities

    def call(self, method: str, params: dict = None):
        """Direct API method call"""
        response = self.post(method, json=params).json()
        if 'error' in response:
            print(f"[API Error] Method: {method} — {response.get('error_description', 'Unknown error')}")
        return response
