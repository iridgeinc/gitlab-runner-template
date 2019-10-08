from troposphere import GetAtt, Output, Parameter, Ref, Template
from troposphere.awslambda import Code, Function
from troposphere.iam import Policy, Role


class RunnerUnregisterLambda:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description("Lambda Function for Unregisteration of Runners")

    def add_parameters(self):
        self.runner_lambda_handler = self.template.add_parameter(
            Parameter(
                "RunnerLambdaHandler",
                Description="runner_lambda_handler",
                Type="String",
            )
        )

        self.runner_lambda_runtime = self.template.add_parameter(
            Parameter(
                "RunnerLambdaRuntime",
                Description="runner_lambda_runtime",
                Type="String",
            )
        )

    def add_resources(self):
        self.lambda_execution_role = self.template.add_resource(
            Role(
                "LambdaExecutionRole",
                Path="/",
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/AmazonSSMFullAccess",
                    "arn:aws:iam::aws:policy/AutoScalingFullAccess",
                ],
                Policies=[
                    Policy(
                        PolicyName="root",
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Action": ["logs:*"],
                                    "Resource": "arn:aws:logs:*:*:*",
                                    "Effect": "Allow",
                                }
                            ],
                        },
                    )
                ],
                AssumeRolePolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": ["sts:AssumeRole"],
                            "Effect": "Allow",
                            "Principal": {"Service": ["lambda.amazonaws.com"]},
                        }
                    ],
                },
            )
        )

        with open("lambda_functions/unregister_runner.py", "r") as f:
            self.runner_unregister_code = f.read()

        self.runner_unregister_function = self.template.add_resource(
            Function(
                "RunnerUnregisterFunction",
                Code=Code(ZipFile=self.runner_unregister_code),
                Handler=Ref(self.runner_lambda_handler),
                Role=GetAtt("LambdaExecutionRole", "Arn"),
                Runtime=Ref(self.runner_lambda_runtime),
                MemorySize="128",
                Timeout="30",
            )
        )

    def add_outputs(self):
        self.template.add_output(
            [
                Output(
                    "RunnerUnregisterFunction",
                    Value=Ref(self.runner_unregister_function),
                ),
                Output(
                    "RunnerUnregisterFunctionArn",
                    Value=GetAtt(self.runner_unregister_function, "Arn"),
                ),
            ]
        )


def sceptre_handler(sceptre_user_data):
    _runner_unregister_lambda = RunnerUnregisterLambda(sceptre_user_data)
    _runner_unregister_lambda.add_parameters()
    _runner_unregister_lambda.add_resources()
    _runner_unregister_lambda.add_outputs()
    return _runner_unregister_lambda.template.to_json()
