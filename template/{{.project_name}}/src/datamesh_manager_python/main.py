import json
import os
import sys

import requests
import yaml
from pyspark.dbutils import DBUtils


# data mesh manager api base url
dmm_api_base_url = "https://api.datamesh-manager.com/api"

# data mesh manager api key from databricks secrets
dmm_api_key = DBUtils().secrets.get("datamesh_manager", "api_key")

# yaml file paths
files_path = sys.argv[1]
data_contract_path = os.path.join(files_path, 'datacontract.yml')
data_product_path = os.path.join(files_path, 'dataproduct.yml')


def main():
    data_mesh_manager = DataMeshManager(dmm_api_base_url, dmm_api_key)

    # send data contract to data mesh manager
    with open(data_contract_path, 'r') as file:
        data_contract = DataContract(file)
        data_mesh_manager.put_data_contract(data_contract)
        file.close()

    # send data product to data mesh manager
    with open(data_product_path, 'r') as file:
        data_product = DataProduct(file)
        data_mesh_manager.put_data_product(data_product)
        file.close()


class DataProduct:
    def __init__(self, yaml_file):
        self._data = yaml.safe_load(yaml_file)

    def id(self) -> str:
        return self._data["id"]

    def json(self) -> str:
        return json.dumps(self._data)


class DataContract:
    def __init__(self, yaml_file):
        self._data = yaml.safe_load(yaml_file)

    def id(self) -> str:
        return self._data["id"]

    def json(self) -> str:
        return json.dumps(self._data)


class DataMeshManager:
    def __init__(self, base_url, api_key):
        self._base_url = base_url
        self._api_key = api_key

    def put_data_product(self, data_product: DataProduct):
        self._put("dataproducts", data_product.id(), data_product.json())

    def put_data_contract(self, data_contract: DataContract):
        self._put('datacontracts', data_contract.id(), data_contract.json())

    def _put(self, entity_segment, entity_id, data):
        response = requests.put(
            url="%s/%s/%s" % (self._base_url, entity_segment, entity_id),
            data=data,
            headers={
                'x-api-key': self._api_key,
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(e, response.json()["detail"])


if __name__ == '__main__':
    main()
