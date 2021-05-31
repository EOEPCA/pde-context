
import os
import configparser
from pathlib import Path

def set_aws_cli(user_rm_section, s3_access, s3_secret, s3_region, endpoint):

    home = str(Path.home())

    if not os.path.exists(os.path.join(home, '.aws')):
        os.makedirs(os.path.join(home, '.aws'))

    aws_config_file = os.path.join(home, '.aws/config')
    aws_credential_file = os.path.join(home, '.aws/credentials')
    
    config = configparser.ConfigParser()

    if os.path.exists(aws_config_file):
        
        config.read(aws_config_file)

    # set the plugins section
    if 'plugins' in config.sections():
    
        if not 'endpoint' in config['plugins'].keys():

            config['plugins']['endpoint'] = 'awscli_plugin_endpoint'
    else: 
        
        config['plugins'] = {'endpoint': 'awscli_plugin_endpoint'}

    if user_rm_section in config.sections():

        config.remove_section(user_rm_section)

        config[user_rm_section] = {"aws_access_key_id": s3_access,
                            "aws_secret_access_key": s3_secret,
                            "region": s3_region,
                            "s3": f"\nendpoint_url = {endpoint}\naddressing_style = path"}

    with open(aws_config_file, 'w') as configfile:
        config.write(configfile)


    config = configparser.ConfigParser()

    if os.path.exists(aws_credential_file):
        
        os.remove(aws_credential_file)

    config[user_rm_section] = {"aws_access_key_id": s3_access,
                            "aws_secret_access_key": s3_secret,
                            "region": s3_region,
                            "s3": f"\nendpoint_url = {endpoint}\naddressing_style = path"}
    
    with open(aws_credential_file, 'w') as configfile:
        config.write(configfile)
