!#/bin/zsh

AWS_PROFILE="wm-esycat"
AWS_REGION=$1

alarm_topic="arn:aws:sns:${AWS_REGION}:284100372099:support"

subscribers=$(cat subscribers.json | jq -r '.[]')

for subscriber in $subscribers ; do
    echo "Subscribing ${subscriber}"
    aws --profile=${AWS_PROFILE} --region=${AWS_REGION} \
        sns subscribe \
            --topic-arn="${alarm_topic}" \
            --protocol="email" \
            --notification-endpoint="${subscriber}"
done
