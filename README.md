# Goal: 
Using python’s Boto3 to read a YAML configuration and deploy a AWS EC2 instance with 2 volumes and 2 users.

# To Run: 
1. pip install boto3
2. pip install PyYAML
3. In yaml file add in value for ssh_key_name to be able to ssh into the instance
4. Run python launch_ec2.py to create ec2 instance
5. Create security group to allow any ssh user to log into instance
6. Users not fully tested cloud.init script
7. Making a file System via ssh command: sudo mkfs -t xfs /dev/xvdf
8. Create Directory: sudo mkdir /data
9. Mount the file system: sudo mount /dev/xvdf/data
10. Ssh command: ssh -i ~/.ssh/{ssh_key_name corresponding private key} ec2-user@{hostName}
11. Users script is not fully tested; but found the specified solution from research

# Notes/Challenges:
Couldn't create 10Gb root volume, instead chose 35Gb because API rejected 10Gb
Limited error checking, for example no ami id, or couldn't create the instance, will just return

# Method Descriptions:
1. getYamlConfig(): Read in yaml file
2. launchAmi(amiid): Gather all necessary values from yaml file and create instance by passing in those values
3. getImageId(): get image id from 
4. getHostName(instanceid): get public host name
5. Main method:
    Get the ami id from architecture: x86_64, root device type: ebs, virtualization: hvm, amitype: amzn
    instanceId from launchAmi(amiId): launch with values and volumes, users and create the instance
    hostName from getHostName(instanceId): to ssh into instance


