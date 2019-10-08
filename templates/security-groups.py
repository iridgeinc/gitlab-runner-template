import troposphere.ec2 as ec2
from troposphere import Output, Parameter, Ref, Tags, Template


class RunnerSecurityGroups:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description("Runner SecurityGroups")

    def add_parameters(self):
        self.runner_vpc = self.template.add_parameter(
            Parameter("RunnerVpc", Description="id of vpc", Type="String")
        )

        self.runner_allowed_ip = self.template.add_parameter(
            Parameter("RunnerAllowedIp", Description="ip allowed to ssh", Type="String")
        )

    def add_resources(self):
        self.runner_security_group = self.template.add_resource(
            ec2.SecurityGroup(
                "RunnerSecurityGroup",
                VpcId=Ref(self.runner_vpc),
                GroupDescription="runner_security_group",
                Tags=Tags(Name="runner_security_group"),
            )
        )

        self.runner_ingress_rule_01 = self.template.add_resource(
            ec2.SecurityGroupIngress(
                "RunnerIngressRule01",
                GroupId=Ref(self.runner_security_group),
                ToPort="22",
                IpProtocol="tcp",
                CidrIp=Ref(self.runner_allowed_ip),
                FromPort="22",
            )
        )

    def add_outputs(self):
        self.template.add_output(
            [Output("RunnerSecurityGroup", Value=Ref(self.runner_security_group))]
        )


def sceptre_handler(sceptre_user_data):
    _runner_security_groups = RunnerSecurityGroups(sceptre_user_data)
    _runner_security_groups.add_parameters()
    _runner_security_groups.add_resources()
    _runner_security_groups.add_outputs()
    return _runner_security_groups.template.to_json()
