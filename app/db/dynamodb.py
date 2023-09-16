import boto3
import utils.config as config

class DynamoDb:
    def __init__(self, table: str=''):
        self.client = self.DynamoDbClient()
        self.table = self.client.Table(table) if table else None

    class DynamoDbClient:
        _instance = None
        def __new__(cls):
            if not cls._instance:
                cls._instance = boto3.resource('dynamodb', region_name=config.AWS_DEFAULT_REGION)
            return cls._instance