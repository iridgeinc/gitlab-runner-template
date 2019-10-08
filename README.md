# GitLab Runner AutoscalingGroup
By using this repository, you can deploy gitlab runner autoscaling group in your aws account. **This repository is featured on the iRidge Developer Blog!** [here!](https://iridge-tech.hatenablog.com/entry/gitlab-runner-deploy)

## Usage
### Preparation
* First, install dependent packages.

```
$ pip install -r ./requirements.txt
```

* Secound, copy variables yaml file.

```
$ cp variables.yaml.sample variables.yaml
```

* Thrid, set values of variables. The mean of each variable is follow;

|variable|description|
|------|----|
| runner_region| aws region in which runner is deployed |
| runner_vpc| vpc id in which runner is deployed |
| runner_allowed_ip| souce ip cidr to be allowed to ssh into runner|
| runner_ami_id| the id of ami for runner (recommendation: amazon linux 2 ami, restriction: redhat type distribution)|
| runner_instance_type| instance type for runner|
| runner_key_pair| key pair name of runner|
| runner_desired_count| initial count of runner|
| runner_min_count| minimum count of runner|
| runner_max_count| maximum count of runner|
| runner_subnets| comma separated subnet ids to which runner belongs|
| runner_job_concurrency| the count of jobs which runner execute in parallel (0 means infinity)|
| runner_tag_list| comma separated tags of runner|
| runner_register_token| the token to register runner into gitlab|
| runner_gitlab_url| the url of gitlab which runner connect|
| runner_volume_size| the size of ebs volume which is attached to runner (GB)|
| runner_scalein_threshold| the cpu usage in which runner scale-in (%)|
| runner_scaleout_threshold| the cpu usage in which runner scale-out (%)|
| runner_scalein_cooldown| the term of cooldown after scaling-in runner (secs)|
| runner_scaleout_cooldown| the term of cooldown after scaling-out runner (secs)|

* Forth, set your aws credential.

### Deploy runner
* deploy runner by only executing this command!

```
$ sceptre --var-file ./variables.yaml launch runners
```

### Destroy runner
* destroy runner by only executing this command...

```
$ sceptre --var-file ./variables.yaml delete runners
```
