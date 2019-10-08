import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client("ssm")
asg = boto3.client("autoscaling")


def handler(event, context):
    try:
        instance_id = event["detail"]["EC2InstanceId"]
        auto_scaling_group = event["detail"]["AutoScalingGroupName"]
        life_cycle_hook = event["detail"]["LifecycleHookName"]

        # send gitlab runner unregister
        ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": ["/unregister.sh"], "executionTimeout": ["60"]},
        )

        asg.complete_lifecycle_action(
            LifecycleHookName=life_cycle_hook,
            AutoScalingGroupName=auto_scaling_group,
            LifecycleActionResult="ABANDON",
            InstanceId=instance_id,
        )

    except Exception as e:
        logger.error(e)
        raise e
