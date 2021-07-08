import yaml
import boto3
import time
import os

def getYamlConfig():
    fname = "example.yaml"
    with open(fname, 'r') as stream:
        try:
            parsed_config = yaml.safe_load(stream)
            return parsed_config
        except yaml.YAMLError as exc:
            print(exc)
    return None
    
def launchAmi(amiid):
    yamlConfig = getYamlConfig()
    if yamlConfig is None:
        return 
    v1d, v1sz =  yamlConfig['server']['volumes'][0]["device"], yamlConfig['server']['volumes'][0]["size_gb"]
    v2d, v2sz =  yamlConfig['server']['volumes'][1]["device"], yamlConfig['server']['volumes'][1]["size_gb"]
    
    blockDeviceMappings=[
        { 
            "DeviceName": v1d,
            "Ebs": {
                "VolumeSize": v1sz,
                'DeleteOnTermination': True,
                'VolumeType': 'gp2',
                'Encrypted': False
             }
         },
         {
            "DeviceName": v2d,
             "Ebs": {
                "VolumeSize": v2sz,
                'DeleteOnTermination': True,
                'VolumeType': 'gp2',
                'Encrypted': False
             }
         }
    ]
    
    #create user data from users:
    u1l, u1sshkey = yamlConfig['server']['users'][0]['login'], yamlConfig['server']['users'][0]['ssh_key']
    u2l, u2sshkey = yamlConfig['server']['users'][1]['login'], yamlConfig['server']['users'][1]['ssh_key']
    userData = '''
    #cloud-config
    users:
    - name: %s
      ssh-authorizated-keys:
      - %s 
    - name: %s
      ssh-authorizated-keys:
      - %s   
    ''' %(u1l,u1sshkey,u2l,u2sshkey)
   
    
    # in order to access instance, one should inject public key
    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(
        # set up various parameters from yaml to this
        InstanceType=yamlConfig['server']['instance_type'],
        MinCount=yamlConfig['server']['min_count'],
        MaxCount=yamlConfig['server']['max_count'],
        ImageId=amiid,
        UserData=userData,
        BlockDeviceMappings=blockDeviceMappings,
        KeyName=yamlConfig['server']['ssh_key_name']
        )
    # collect instance ids
    iids = [instance.id for instance in instances]
    ec2c = boto3.client('ec2')
    waiter = ec2c.get_waiter('instance_running')
    # wait until all instances are running
    waiter.wait(InstanceIds=iids)
    print('instance success')
    return iids[0]
        

def getImageId():
    ec2 = boto3.client('ec2')
    images = ec2.describe_images(
        Filters=[
        {
            'Name': 'architecture',
            'Values': ['x86_64']
        },
        {
            'Name': 'root-device-type',
            'Values': ['ebs' ]
        },
        { "Name" : "name",
          "Values" : ["amzn*"]
        },
        {
            'Name': 'virtualization-type',
            'Values': ['hvm' ]
        }
        ],
        Owners=['amazon']
    )

    for k, v in images.items():
        if k == 'Images':
            for image in v:
                amiid = image['ImageId']
                break
    return amiid

def getHostname(instanceid):
    ec2 = boto3.client('ec2')
    details = ec2.describe_instances(
    InstanceIds=[
        instanceid
    ])
    hostName = details["Reservations"][0]["Instances"][0]["PublicDnsName"]
    return hostName

if __name__ == "__main__":
    amiId = getImageId()
    print('amiid is ', amiId)
    instanceId = launchAmi(amiId)
    print('instance instance id : ', instanceId)
    hostName = getHostname(instanceId)
    print('instance public dns name: ', hostName)
    

