import click
import utils.DemoClient as client
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
import urllib3

@click.command()
@click.option('--username',required=True, help='username')
@click.option('--password',required=True, help='user password')
@click.option('--base_domain',required=True, help='Ades host')
@click.option('--jenkins_endpoint', default='http://127.0.0.1:8081/jenkins/', help='Jenkins endpoint')
@click.option('--workspace_prefix', default='rm-user', help='Workspace prefix')
def cli(username, password, base_domain, jenkins_endpoint,workspace_prefix):
    # user home path
    home = str(Path.home())

    printTitle(f"Retrieving access credentials for user {username}")

    # -------------------------------------------------------------------------------
    # Initialise client
    # -------------------------------------------------------------------------------
    try:
        demo = client.DemoClient(f"https://test.{base_domain}")
        demo.register_client()
        demo.save_state()
    except urllib3.exceptions.NewConnectionError as err:
        raise SystemExit(err)

    # -------------------------------------------------------------------------------
    # Authenticate as user 'eric' and get ID Token
    # -------------------------------------------------------------------------------
    USER_NAME = username
    USER_PASSWORD = password
    user_id_token = demo.get_id_token(USER_NAME, USER_PASSWORD)

    # Init
    workspace_url = "https://workspace-api." + base_domain
    workspace_access_token = None

    # Workspace - Get Details
    workspace_name = f"{workspace_prefix}-" + USER_NAME.lower()
    response, workspace_access_token = demo.workspace_get_details(
        workspace_url, workspace_name, id_token=user_id_token, access_token=workspace_access_token)
    workspace_details = response.json()
    printTitle("Access credential json")
    click.echo(json.dumps(workspace_details, indent=4))

    # Bucket details
    endpoint = workspace_details["storage"]["credentials"]["endpoint"]
    bucket_name = workspace_details["storage"]["credentials"]["bucketname"]
    s3_access = workspace_details["storage"]["credentials"]["access"]
    s3_secret = workspace_details["storage"]["credentials"]["secret"]
    s3_region = workspace_details["storage"]["credentials"]["region"]
    s3_projectid = workspace_details["storage"]["credentials"]["projectid"]

    # -------------------------------------------------------------------------------
    # S3CMD CONFIG FILE
    # -------------------------------------------------------------------------------
    printTitle("s3cmd creating/updating config file:")
    s3cmd_config_file = os.path.join(home,".s3cfg")
    s3cfgString = """
host_base = {endpoint}
host_bucket = {endpoint}
access_key = {s3_access}
secret_key = {s3_secret}
    """.format(endpoint=endpoint, s3_access=s3_access, s3_secret=s3_secret)
    click.echo(s3cfgString)

    confirm_s3cfg = True
    # checking if file already exists
    if os.path.exists(s3cmd_config_file):
        click.echo(
            f"{s3cmd_config_file} exists. Would you like to overwrite it?")
        confirm_s3cfg = confirm()

    else:
        click.echo(f"{s3cmd_config_file} does not exist. File will be created")

    if confirm_s3cfg:
        s3cmd_config = open(s3cmd_config_file, "w")
        s3cmd_config.write(s3cfgString)
        s3cmd_config.close()
    else:
        click.echo("Skipping writting/updating s3cfg file")

    # -------------------------------------------------------------------------------
    # AWS CONFIG FILE
    # -------------------------------------------------------------------------------
    printTitle("AWS CLI: creating/updating config file:")
    aws_config_file = os.path.join(home, '.aws/config')
    aws_credential_file = os.path.join(home, '.aws/credentials')

    ## Config file
    aws_config_file_string = """[profile {workspace_prefix}-{username}]
aws_access_key_id = {s3_access}
aws_secret_access_key = {s3_secret}
region = {s3_region}
s3 =
  endpoint_url = {endpoint}
  addressing_style = path
""".format(workspace_prefix= workspace_prefix, username=username, endpoint=endpoint, s3_access=s3_access, s3_secret=s3_secret, s3_region=s3_region)

    ## Credential file. This file will be used by Jenkins to grant access to the Workspace
    aws_credentials_file_string = """[{workspace_prefix}-{username}]
aws_access_key_id = {s3_access}
aws_secret_access_key = {s3_secret}
region = {s3_region}
s3 =
  endpoint_url = {endpoint}
  addressing_style = path
""".format(workspace_prefix= workspace_prefix, username=username, endpoint=endpoint, s3_access=s3_access, s3_secret=s3_secret, s3_region=s3_region)

    click.echo(aws_config_file_string)
    
    ################
    # Write/append config file
    if os.path.exists(aws_config_file):
        append_write = 'a'  # append if already exists
        click.echo(
            f".aws/config exists. Appending new config for user {username}")
        aws_config_file_string = f"\n\n{aws_config_file_string}"
    else:
        append_write = 'w'  # make a new file if not
        click.echo(".aws/config does not exist. File will be created")
    
    aws_config = open(aws_config_file, append_write)
    aws_config.write(aws_config_file_string)
    aws_config.close()

    ################
    # Write/append credential file
    if os.path.exists(aws_credential_file):
        append_write = 'a'  # append if already exists
        click.echo(
            f".aws/credentials exists. Appending new config for user {username}")
        aws_credentials_file_string = f"\n\n{aws_credentials_file_string}"
    else:
        append_write = 'w'  # make a new file if not
        click.echo(".aws/config does not exist. File will be created")


    aws_config = open(aws_credential_file, append_write)
    aws_config.write(aws_credentials_file_string)
    aws_config.close()

    # -------------------------------------------------------------------------------
    # JENKINS AWS VARIABLES
    # -------------------------------------------------------------------------------
    printTitle("JENKINS: creating secrets for workspace access")

    createJenkinsSecretTextCredentials(jenkinsApiEndpoint=jenkins_endpoint,
                                       textId="S3_Region",
                                       secret=s3_region)
    click.echo(f"S3_Region added to Jenkins Secrets")

    createJenkinsSecretTextCredentials(jenkinsApiEndpoint=jenkins_endpoint,
                                       textId="S3_Endpoint",
                                       secret=endpoint)

    click.echo(f"S3_Endpoint added to Jenkins Secrets")

    createJenkinsSecretTextCredentials(jenkinsApiEndpoint=jenkins_endpoint,
                                       textId="S3_Bucket",
                                       secret=bucket_name)

    click.echo(f"S3_Bucket added to Jenkins Secrets")

    createJenkinsSecretTextCredentials(jenkinsApiEndpoint=jenkins_endpoint,
                                       textId="S3_ProjectId",
                                       secret=s3_projectid)

    click.echo(f"S3_ProjectId added to Jenkins Secrets")


def confirm():
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("OK to push to continue [Y/N]? ").lower()
    return answer == "y"


def printTitle(title):
    """ Prints title """

    click.echo(
        f"\n################################################\n### {title} \n ")


def createJenkinsAWSCredentials(jenkinsApiEndpoint, credentialNameId, s3_access,  s3_secret, description="AWS Credentials", scope="GLOBAL"):
    """ Adds AWS Credentials to Jenkins """

    # create a session object
    s = requests.Session()

    # retrieve a crumb
    try:
        crumbIssuerPath = os.path.join(
            jenkinsApiEndpoint, 'crumbIssuer/api/json')
        r = s.get(crumbIssuerPath)
        r.raise_for_status()

        # parse response json and retrieve crumb property
        responseJson = json.loads(r.text)
        jenkinsCrumb = responseJson["crumb"]

        # retrieved CRUMB
        # print(f"CRUMB: {jenkinsCrumb}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # createCrendentials API
    try:
        createCredentialsApiPath = os.path.join(
            jenkinsApiEndpoint, 'credentials/store/system/domain/_/createCredentials')

        pl = {
            "credentials":
            {
                "scope": "GLOBAL",
                "id": credentialNameId,
                "description": description,
                "accessKey": s3_access,
                "secretKey": s3_secret,
                "$redact": "secretKey",
                "stapler-class": "com.cloudbees.jenkins.plugins.awscredentials.AWSCredentialsImpl"
            }
        }

        payload = {
            'json': json.dumps(pl),
            'Submit': "OK",
        }
        x = s.post(createCredentialsApiPath, data=payload,
                   headers={"Jenkins-Crumb": jenkinsCrumb})
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def createJenkinsSecretTextCredentials(jenkinsApiEndpoint, textId, secret, description="Secret text", scope="GLOBAL"):
    """ Adds Secret Text Credentials to Jenkins """

    # create a session object
    s = requests.Session()

    # retrieve a crumb
    try:
        crumbIssuerPath = os.path.join(
            jenkinsApiEndpoint, 'crumbIssuer/api/json')
        r = s.get(crumbIssuerPath)
        r.raise_for_status()

        # parse response json and retrieve crumb property
        responseJson = json.loads(r.text)
        jenkinsCrumb = responseJson["crumb"]

        # retrieved CRUMB
        # print(f"CRUMB: {jenkinsCrumb}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # createCrendentials API
    try:
        createCredentialsApiPath = os.path.join(
            jenkinsApiEndpoint, 'credentials/store/system/domain/_/createCredentials')

        pl = {
            "credentials": {
                "scope": scope,
                "secret": secret,
                "$redact": "secret",
                "id": textId,
                "description": description,
                "stapler-class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl"
            }
        }

        payload = {
            'json': json.dumps(pl),
            'Submit': "OK",
        }
        x = s.post(createCredentialsApiPath, data=payload,
                   headers={"Jenkins-Crumb": jenkinsCrumb})
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


if __name__ == '__main__':
    cli()
