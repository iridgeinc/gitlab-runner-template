from troposphere import GetAtt, Parameter, Ref, Template
from troposphere.autoscaling import LifecycleHook
from troposphere.awslambda import Permission
from troposphere.events import Rule, Target


class RunnerLifecycleHook:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description("Runner LifecycleHook")

    def add_parameters(self):
        self.runner_autoscaling_group = self.template.add_parameter(
            Parameter(
                "RunnerAutoscalingGroup",
                Description="runner_autoscaling_group",
                Type="String",
            )
        )

        self.runner_unregister_function = self.template.add_parameter(
            Parameter(
                "RunnerUnregisterFunction",
                Description="runner_unregister_function",
                Type="String",
            )
        )

        self.runner_unregister_function_arn = self.template.add_parameter(
            Parameter(
                "RunnerUnregisterFunctionArn",
                Description="runner_unregister_function_arn",
                Type="String",
            )
        )

        self.runner_terminate_target_id = self.template.add_parameter(
            Parameter(
                "RunnerTerminateTargetId",
                Description="runner_terminate_target_id",
                Type="String",
            )
        )

    def add_resources(self):
        self.runner_terminate_rule = self.template.add_resource(
            Rule(
                "RunnerTeminateRule",
                EventPattern={
                    "source": ["aws.autoscaling"],
                    "detail-type": ["EC2 Instance-terminate Lifecycle Action"],
                },
                State="ENABLED",
                Targets=[
                    Target(
                        Arn=Ref(self.runner_unregister_function_arn),
                        Id=Ref(self.runner_terminate_target_id),
                    )
                ],
            )
        )

        self.runner_unregister_permission = self.template.add_resource(
            Permission(
                "RunnerUnregisterPermission",
                Action="lambda:InvokeFunction",
                FunctionName=Ref(self.runner_unregister_function),
                Principal="events.amazonaws.com",
                SourceArn=GetAtt(self.runner_terminate_rule, "Arn"),
            )
        )

        self.runner_terminate_lifecyclehook = self.template.add_resource(
            LifecycleHook(
                "RunnerTerminateLifecycleHook",
                AutoScalingGroupName=Ref(self.runner_autoscaling_group),
                LifecycleTransition="autoscaling:EC2_INSTANCE_TERMINATING",
            )
        )


def sceptre_handler(sceptre_user_data):
    _runner_lifecyclehook = RunnerLifecycleHook(sceptre_user_data)
    _runner_lifecyclehook.add_parameters()
    _runner_lifecyclehook.add_resources()
    return _runner_lifecyclehook.template.to_json()
