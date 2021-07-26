import argparse
from typing import Any, Generator, List, Tuple

import boto3
import yaml

parser = argparse.ArgumentParser(
    description="Sync properties with System Manager Parameter Store")

parser.add_argument(
    "properties_file",
    metavar="properties_file",
    help="Location of the yaml file to use.",
    type=argparse.FileType("r"),
)
parser.add_argument(
    "--properties-type", "-pt", dest="properties_type", help="String | SecureString"
)
parser.add_argument(
    "--region", "-r", dest="region", help="aws region"
)
parser.add_argument(
    "--stage", "-s", dest="stage", default="dev", help="Stage name (like dev or prod)"
)
parser.add_argument(
    "--profile",
    "-p",
    dest="profile_name",
    help="aws profile name",
)
parser.add_argument(
    "--project-name",
    "-n",
    dest="project_name",
)

args = parser.parse_args()

session = boto3.Session(
    profile_name=f"{args.profile_name}", region_name=args.region
)

ssm_client = session.client("ssm")

prefix = f"/{args.project_name}/{args.stage}"


def flatten(exp: Any) -> Generator[Tuple[str, str], None, None]:
    def sub(exp: Any, res: List[str]) -> Generator[Tuple[str, Any], None, None]:
        if type(exp) == dict:
            for k, v in exp.items():
                yield from sub(v, res + [k])
        elif type(exp) == list:
            for v in exp:
                yield from sub(v, res)
        else:
            yield (f"{prefix}/{'/'.join(res)}", exp)

    yield from sub(exp, [])


data_loaded = yaml.load(args.properties_file, Loader=yaml.FullLoader)

data_tuples = flatten(data_loaded)

new_keys = []

for dt in data_tuples:
    new_keys.append(dt[0])
    print(f"Updating {dt[0]}")

    ssm_client.put_parameter(
        Name=dt[0], Value=dt[1], Type=f"{args.properties_type}", Overwrite=True,
    )

    ssm_client.add_tags_to_resource(
        ResourceType='Parameter',
        ResourceId=dt[0],
        Tags=[
            {
                'Key': 'Project',
                'Value': f"{args.project_name}"
            },
        ]
    )
