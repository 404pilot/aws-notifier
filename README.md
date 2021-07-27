# agent-cooper
[![CircleCI](https://circleci.com/gh/404pilot/agent-cooper.svg?style=shield)](https://circleci.com/gh/404pilot/agent-cooper)

Agent Cooper is deployed to AWS Cloud with the help of AWS SAM and CircleCi. It utilizes cloud watch schedule to run lambda services periodically and uses Gmail API to send out email notifications.

It provides a place that can run anything I like and it is free offered by AWS Free Tier :)



## Usage

### rachio 

[rachio](https://rachio.com/) is a great sprinkler controller that creates tailored smart schedules based on the weather and some configurations.

However, it never sends out a notification that tells me that my lawn will be watered the next day. It only pushes a mobile notification right before the watering event is about to happen which is usually between 5 AM and 7 AM in the morning. :( And I only know it after I wake up, and I can't do anything about it.

Agent Cooper is currently checking every day if there is a scheduled event for the next day. If there is an event, it will send out an email to me. So I can decide if I want to mow my lawn today or delay the service. 



## Memo

Fully automation is fantasic. However there are some manual steps:

1. setup AWS and gmail API
2. install `aws-cli`, `sam-cli`, `sops`
3. create a KMS key

```shell
# create a KMS key
$ aws kms create-key --region us-east-1
$ aws kms create-alias --alias-name alias/agent-cooper-secrets --target-key-id {{key_id}} --region us-east-1
# init the encrypted configuration file
$ sops --kms {{key_arn}} properties/conf.yaml

# decrypt a file
$ sops properties/conf.yaml
# update encrypted file
$ sops -i properties/conf.yaml
```

