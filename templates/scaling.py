from troposphere import Parameter, Ref, Template
from troposphere.autoscaling import ScalingPolicy
from troposphere.cloudwatch import Alarm, MetricDimension


class RunnerScaling:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description("Runner Scaling Objects")

    def add_parameters(self):
        self.runner_autoscaling_group = self.template.add_parameter(
            Parameter(
                "RunnerAutoscalingGroup",
                Description="runner_autoscaling_group",
                Type="String",
            )
        )

        self.runner_scalein_threshold = self.template.add_parameter(
            Parameter(
                "RunnerScaleinThreshold",
                Description="runner_scalein_threshold",
                Type="Number",
            )
        )

        self.runner_scaleout_threshold = self.template.add_parameter(
            Parameter(
                "RunnerScaleoutThreshold",
                Description="runner_scaleout_threshold",
                Type="Number",
            )
        )

        self.runner_scalein_cooldown = self.template.add_parameter(
            Parameter(
                "RunnerScaleinCooldown",
                Description="runner_scalein_cooldown",
                Type="Number",
            )
        )

        self.runner_scaleout_cooldown = self.template.add_parameter(
            Parameter(
                "RunnerScaleoutCooldown",
                Description="runner_scaleout_cooldown",
                Type="Number",
            )
        )

    def add_resources(self):
        self.scaleout_policy = self.template.add_resource(
            ScalingPolicy(
                "RunnerScaleoutPolicy",
                AdjustmentType="ChangeInCapacity",
                AutoScalingGroupName=Ref(self.runner_autoscaling_group),
                Cooldown=Ref(self.runner_scaleout_cooldown),
                ScalingAdjustment="1",
            )
        )

        self.runner_cpu_alarm_high = self.template.add_resource(
            Alarm(
                "RunnerCPUAlarmHigh",
                EvaluationPeriods="1",
                Statistic="Average",
                Threshold=Ref(self.runner_scaleout_threshold),
                AlarmDescription="Alarm if CPU utilization too high",
                Period="60",
                AlarmActions=[Ref(self.scaleout_policy)],
                Namespace="AWS/EC2",
                Dimensions=[
                    MetricDimension(
                        Name="AutoScalingGroupName",
                        Value=Ref(self.runner_autoscaling_group),
                    )
                ],
                ComparisonOperator="GreaterThanThreshold",
                MetricName="CPUUtilization",
            )
        )

        self.scalein_policy = self.template.add_resource(
            ScalingPolicy(
                "RunnerScaleinPolicy",
                AdjustmentType="ChangeInCapacity",
                AutoScalingGroupName=Ref(self.runner_autoscaling_group),
                Cooldown=Ref(self.runner_scalein_cooldown),
                ScalingAdjustment="-1",
            )
        )

        self.runner_cpu_alarm_low = self.template.add_resource(
            Alarm(
                "RunnerCPUAlarmLow",
                EvaluationPeriods="1",
                Statistic="Average",
                Threshold=Ref(self.runner_scalein_threshold),
                AlarmDescription="Alarm if CPU utilization too low",
                Period="60",
                AlarmActions=[Ref(self.scalein_policy)],
                Namespace="AWS/EC2",
                Dimensions=[
                    MetricDimension(
                        Name="AutoScalingGroupName",
                        Value=Ref(self.runner_autoscaling_group),
                    )
                ],
                ComparisonOperator="LessThanThreshold",
                MetricName="CPUUtilization",
            )
        )


def sceptre_handler(sceptre_user_data):
    _runner_scaling = RunnerScaling(sceptre_user_data)
    _runner_scaling.add_parameters()
    _runner_scaling.add_resources()
    return _runner_scaling.template.to_json()
