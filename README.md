# pde-context

*pde-context* is a command line tool that provides to a user working in a pde envrironment the means to access his workspace resources.


## Usage


* To call the help function type the following command:
  ```

  pde-context --help

  ```
  the output will be the following
  ```
  Usage: pde-context [OPTIONS]

  Options:
    --username TEXT          username  [required]
    --password TEXT          user password  [required]
    --base_domain TEXT       Ades host  [required]
    --jenkins_endpoint TEXT  Jenkins endpoint
    --workspace_prefix TEXT  Workspace prefix
    --help                   Show this message and exit.

  ```

* To run the pde-context script run the following command using your username, password and the resource manager endpoint url
  ```
  pde-context --username eric --password defaultPWD --base_domain 111.222.333.444.nip.io
  ```
  the ouptput should look like the following one:
  ```
  ################################################
  ### Retrieving access credentials for user eric 
  ...
 
  [Workspace Details] = 200 (OK)

  ################################################
  ### Access credential json 

  ...

  ################################################
  ### s3cmd creating/updating config file: 

  ...
  
  /home/jovyan/.s3cfg does not exist. File will be created

  ################################################
  ### AWS CLI: creating/updating config file: 

  ...

  ################################################
  ### JENKINS: creating secrets for workspace access 

  S3_Region added to Jenkins Secrets
  S3_Endpoint added to Jenkins Secrets
  S3_Bucket added to Jenkins Secrets
  S3_ProjectId added to Jenkins Secrets
  ```
  
 * **s3cmd**, **aws cli s3** and **Jenkins** should now be configured to access the workspace S3 repository.
