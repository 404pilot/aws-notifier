import boto3


class ParameterStore:
    def __init__(self, region) -> None:
        self.ssm_client = boto3.client("ssm", region_name=region)

    def get_parameter(self, path, with_decryption: bool = True):
        return self.ssm_client.get_parameter(Name=path, WithDecryption=with_decryption)[
            "Parameter"
        ]["Value"]
