from awacs import aws, sts
from awacs.aws import Allow, Principal, Statement
from troposphere import Base64, GetAtt, Join, Output, Parameter, Ref, Split, Template
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag
from troposphere.ec2 import BlockDeviceMapping, EBSBlockDevice
from troposphere.iam import InstanceProfile, Role


class RunnerAsg:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description("Runner ASG")

    def add_parameters(self):
        self.runner_subnets = self.template.add_parameter(
            Parameter("RunnerSubnets", Description="runner_subnets", Type="String")
        )

        self.runner_security_group = self.template.add_parameter(
            Parameter(
                "RunnerSecurityGroup",
                Description="runner_security_group",
                Type="String",
            )
        )

        self.runner_ami_id = self.template.add_parameter(
            Parameter("RunnerAmiId", Description="runner_ami_id", Type="String")
        )

        self.runner_server_instance_type = self.template.add_parameter(
            Parameter(
                "RunnerServerInstanceType",
                Description="runner_server_instance_type",
                Type="String",
            )
        )

        self.runner_key_pair = self.template.add_parameter(
            Parameter("RunnerKeyPair", Description="runner_key_pair", Type="String")
        )

        self.runner_desired_count = self.template.add_parameter(
            Parameter(
                "RunnerDesiredCount", Description="runner_desired_count", Type="Number"
            )
        )

        self.runner_min_count = self.template.add_parameter(
            Parameter("RunnerMinCount", Description="runner_min_count", Type="Number")
        )

        self.runner_max_count = self.template.add_parameter(
            Parameter("RunnerMaxCount", Description="runner_max_count", Type="Number")
        )

        self.runner_job_concurrency = self.template.add_parameter(
            Parameter(
                "RunnerJobConcurrency",
                Description="runner_job_concurrency",
                Type="Number",
            )
        )

        self.runner_tag_list = self.template.add_parameter(
            Parameter("RunnerTagList", Description="runner_tag_list", Type="String")
        )

        self.runner_register_token = self.template.add_parameter(
            Parameter(
                "RunnerRegisterToken",
                Description="runner_register_token",
                Type="String",
            )
        )

        self.runner_gitlab_url = self.template.add_parameter(
            Parameter("RunnerGitlabUrl", Description="runner_gitlab_url", Type="String")
        )

        self.runner_volume_size = self.template.add_parameter(
            Parameter(
                "RunnerVolumeSize", Description="runner_volume_size", Type="String"
            )
        )

        self.runner_version = self.template.add_parameter(
            Parameter("RunnerVersion", Description="runner_version", Type="String")
        )

    def add_resources(self):
        self.runner_ssm_role = self.template.add_resource(
            Role(
                "RunnerSsmRole",
                Path="/",
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
                ],
                AssumeRolePolicyDocument=aws.Policy(
                    Statement=[
                        Statement(
                            Action=[sts.AssumeRole],
                            Effect=Allow,
                            Principal=Principal("Service", ["ec2.amazonaws.com"]),
                        )
                    ]
                ),
            )
        )

        self.runner_ssm_instanceprofile = self.template.add_resource(
            InstanceProfile(
                "RunnerSsmInstanceProfile", Path="/", Roles=[Ref(self.runner_ssm_role)]
            )
        )

        self.runner_launch_config = self.template.add_resource(
            LaunchConfiguration(
                "RunnerLaunchConfiguration",
                UserData=Base64(
                    Join(
                        "",
                        [
                            "#!/bin/bash\n",
                            "#####install ssm######\n",
                            "yum install -y amazon-ssm-agent\n",
                            "systemctl enable amazon-ssm-agent\n",
                            "systemctl start amazon-ssm-agent\n",
                            "####install docker####\n",
                            "yum install -y docker\n",
                            "systemctl enable docker\n",
                            "systemctl start docker\n",
                            "####install runner####\n",
                            "yum install -y wget\n",
                            "wget -O /usr/local/bin/gitlab-runner ",
                            "https://gitlab-runner-downloads.s3.amazonaws.com/v",
                            Ref(self.runner_version),
                            "/binaries/gitlab-runner-linux-amd64\n",
                            "ln -s /usr/local/bin/gitlab-runner ",
                            "/usr/bin/gitlab-runner\n",
                            "chmod +x /usr/local/bin/gitlab-runner\n",
                            "useradd --comment 'GitLab Runner' ",
                            "--create-home gitlab-runner --shell /bin/bash\n",
                            "/usr/local/bin/gitlab-runner install ",
                            "--user=gitlab-runner "
                            "--working-directory=/home/gitlab-runner\n",
                            "systemctl enable gitlab-runner\n",
                            "systemctl start gitlab-runner\n",
                            "####register runner####\n",
                            "gitlab-runner register ",
                            "--config=/etc/gitlab-runner/config.toml ",
                            "--request-concurrency=",
                            Ref(self.runner_job_concurrency),
                            " ",
                            "--tag-list=",
                            Ref(self.runner_tag_list),
                            " ",
                            "--non-interactive ",
                            "--registration-token=",
                            Ref(self.runner_register_token),
                            " ",
                            "--run-untagged=true ",
                            "--locked=false ",
                            "--url=",
                            Ref(self.runner_gitlab_url),
                            " ",
                            "--executor=docker ",
                            "--docker-image=alpine:latest ",
                            "--docker-privileged=true\n",
                            "####create unregister script####\n",
                            "TOKEN=$(gitlab-runner list 2>&1 | grep Executor | ",
                            "awk '{ print $4 }' | awk -F= '{ print $2 }')\n",
                            "URL=$(gitlab-runner list 2>&1 | grep Executor | ",
                            "awk '{ print $5 }' | awk -F= '{ print $2 }')\n",
                            "echo gitlab-runner unregister ",
                            "--url $URL --token $TOKEN > /unregister.sh\n",
                            "chmod +x /unregister.sh",
                        ],
                    )
                ),
                ImageId=Ref(self.runner_ami_id),
                KeyName=Ref(self.runner_key_pair),
                BlockDeviceMappings=[
                    BlockDeviceMapping(
                        DeviceName="/dev/xvda",
                        Ebs=EBSBlockDevice(VolumeSize=Ref(self.runner_volume_size)),
                    )
                ],
                SecurityGroups=[Ref(self.runner_security_group)],
                InstanceType=Ref(self.runner_server_instance_type),
                IamInstanceProfile=GetAtt(self.runner_ssm_instanceprofile, "Arn"),
            )
        )

        self.runner_autoscaling_group = self.template.add_resource(
            AutoScalingGroup(
                "RunnerAutoscalingGroup",
                DesiredCapacity=Ref(self.runner_desired_count),
                LaunchConfigurationName=Ref(self.runner_launch_config),
                MinSize=Ref(self.runner_min_count),
                MaxSize=Ref(self.runner_max_count),
                VPCZoneIdentifier=Split(",", Ref(self.runner_subnets)),
                Tags=[Tag("Name", "gitlab-runner-created-by-asg", True)],
            )
        )

    def add_outputs(self):
        self.template.add_output(
            [
                Output(
                    "RunnerLaunchConfiguration", Value=Ref(self.runner_launch_config)
                ),
                Output(
                    "RunnerAutoscalingGroup", Value=Ref(self.runner_autoscaling_group)
                ),
            ]
        )


def sceptre_handler(sceptre_user_data):
    _runner_asg = RunnerAsg(sceptre_user_data)
    _runner_asg.add_parameters()
    _runner_asg.add_resources()
    _runner_asg.add_outputs()
    return _runner_asg.template.to_json()
