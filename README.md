# aws-notifier

# TODO add timestamp in s3/retention policy
# TODO add email to notify error
# TODO logging

1. add kops to add secret stuff
2. run rachio
3. hook email service


```
$ aws kms create-key --region us-east-1

$ aws kms create-alias --alias-name alias/aws-notifier-secrets --target-key-id 4a64fd6b-eb6f-4f84-99b5-bf4d10a573d6 --region us-east-1

$ sops --kms arn:aws:kms:us-east-1:681487095092:key/4a64fd6b-eb6f-4f84-99b5-bf4d10a573d6 properties/conf.yaml
```
