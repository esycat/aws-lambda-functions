#!/bin/zsh

METRICS_DIR="metrics"

AWS_PROFILE="esycat"
AWS_REGION=$1

alarm_topic="arn:aws:sns:${AWS_REGION}:284100372099:support"

instances=$(
    query='Reservations[*].Instances[*].{id:InstanceId,name:Tags[?Key==`Name`]|[0].Value}'
    aws --profile=${AWS_PROFILE} --region=${AWS_REGION} \
        ec2 describe-instances \
            --filters=file://instance-filters.json \
            --query=${query}
)

for instance in $(echo $instances | jq -c '.[][]') ; do
    instance_id=$(echo $instance | jq -r .id)
    instance_name=$(echo $instance | jq -r .name)

    echo "Setting up CPU Utilization alarm for ${instance_name}"

    alarm_name="${instance_name}.cpu"
    alarm_metrics=$(cat ${METRICS_DIR}/cpu.json | jq '.[0].MetricStat.Metric.Dimensions[0].Value = "'${instance_id}'"')

    aws --profile=${AWS_PROFILE} --region=${AWS_REGION} \
        cloudwatch put-metric-alarm \
            --alarm-name="${alarm_name}" \
            --alarm-actions="${alarm_topic}" \
            --evaluation-periods=10 \
            --threshold-metric-id=ad \
            --comparison-operator=GreaterThanUpperThreshold \
            --metrics="${alarm_metrics}" \

done
