# agent-cooper

# TODO add timestamp in s3/retention policy
# TODO add email to notify error
# TODO logging

1. add kops to add secret stuff
2. run rachio
3. hook email service


```
$ aws kms create-key --region us-east-1

$ aws kms create-alias --alias-name alias/agent-cooper-secrets --target-key-id {{key_id}} --region us-east-1

$ sops --kms {{key_arn}} properties/conf.yaml
```
