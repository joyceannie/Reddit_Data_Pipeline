# REDDIT DATA PIPELINE
The purpose of the project is to create a data pipeline to extract data from Reddit API and create a dashboard to analyse the data.
The data is extracted from the subreddit [r/Python](https://www.reddit.com/r/Python/).
The data is extracted daily and uploaded to S3 buckets, and copied to Redshift. 
The dashboard is created using Google Data Studio.

## Architecture

![workflow image](https://github.com/joyceannie/Reddit_Data_Pipeline/blob/e835b89c08db335c5ad3832a65bf32fe605eff17/images/workflow.png "Workflow Image")

1. Extract the data using [Reddit API](https://www.reddit.com/dev/api/)
2. Create AWS resources with Terraform
3. Load the data to [AWS S3](https://aws.amazon.com/s3/) bucket
4. Copy the data to [AWS Redshift](https://aws.amazon.com/redshift/)
5. Orchestrate with [Airflow](https://airflow.apache.org/) in [Docker](https://www.docker.com/)
6. Create dashboard [using Google Data Studio](https://datastudio.google.com/)


## Dashboard

![Dashboard image](https://github.com/joyceannie/Reddit_Data_Pipeline/blob/37abba35138a12c808fa49e4f8051083489e0f40/images/data_analysis.png "Dashboard Image")

## Setup

Please follow the below steps to setup the pipeline. If you are using [AWS free tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all), there won't be any costs. Make sure that you terminate all the resources on a timely manner. If you don't termniate the resources within 2 months, you will have to pay for the AWS services. AWS free tier terms and conditions as it may change over time. 

Clone the repo

```
git clone https://github.com/joyceannie/Reddit_Data_Pipeline.git
cd  Reddit_Data_Pipeline
```

### Overview

The data is extracted using [PRAW](https://praw.readthedocs.io/en/stable/) API wrapper. The DAG pipeline extracts data every day and stores it in csv file. 
The data is then loaded into S3 buckets and copied to the data warehouse. This entire pipeline is running with Apache Airflow running woth Docker. 
The final step creates a dashboard to gain insights about the data. Google Data Studio is used for generateing the dashboard.

### Reddit API

The data is extracted from the subbreddit `r/Python`. 
In order to extarct Reddit data, we need to use the Reddit API. Follow the below steps.

* Create a [Reddit account](https://www.reddit.com/register/).
* Create an [app](https://www.reddit.com/prefs/apps).
* Note down the following details.
    * App Name
    * App ID
    * API secret key

### AWS

The extracted data is stored on AWS using AWS free tier. There are 2 services used.
1. [Simple Storage Service(S3)](https://aws.amazon.com/s3/): This is object storage. The data extracted from Reddit is uploaded to S3 buckets. We can store all our raw data in S3 buckets.
2. [Redshift](https://aws.amazon.com/redshift/): This is data warehousing service. Redshift uses massively parallell processing technology to execute operations on larger datasets faster. It is based on PostgeSQL, so we can use SQL to run operations on Redshift. 

This project can be done using a local SQL database as the data size is small. However, we are using ccloud technologies to learn more tools and technologies.

In order to get started, you should create a new [AWS account](https://portal.aws.amazon.com/billing/signup?nc2=h_ct&src=header_signup&redirect_url=https%3A%2F%2Faws.amazon.com%2Fregistration-confirmation#/start) and set up a free tier. Make sure you follow all the best practices to keep your account secure. Create a new IAM role and setup [CLI](https://aws.amazon.com/getting-started/guides/setup-environment/module-three/). Now, you will have a new folder in you home directory called `.aws` which contains a `credentials` file. The filw will look like this:
```
[default]
aws_access_key_id = XXXX
aws_secret_access_key = XXXX
```

### IaC using Terraform

We are using [Terraform](https://learn.hashicorp.com/terraform?utm_source=terraform_io)  to setup and destroy our cloud resources using code.
We are creating the following resources

 * Create S3 bucket: Used for storage

 * Create Redshift Cluster: Columnar data warehouse provided by AWS. 

 * IAM Role for Redshift: Role assigns Redshift the permission to read data from S3 buckets.

 * Security Group: Applied to Redshift to allow all incoming traffic so the dashboard can connect to it. In a real production environment, you should not allow all the traffic into your resource.


 Follow the below steps to create the resources

  1. Install terraform by following the [instructions](https://learn.hashicorp.com/tutorials/terraform/install-cli)

  2. Change into `terraform` directory.

  ```
  cd terraform
  ```

  3. Edit `variables.tf` file. Fill in the default parameters for Redshift DB password, S3 bucket name and region.

  4. Download the AWS plugin by running the below command from the `terraform` directory.

  ```
  terraform init
  ```

  5. Create a plan based on the `main.tf` and execute the planned changes to create AWS resources.

  ```
  terraform apply
  ```

  6. RUn this command to destroy all the resources after the whole project is completed, and no longer in use. 

  ```
  terraform destroy
  ```
  After yopu complete the steps, the resources will be visible in the AWS console.

### Configuration

* Setup a configuration file `configuration.conf` under `airflow/extraction/` folder.

* Fill in all the configuration variables in the config file. 

```
[aws_config]
bucket_name = XXXXX
redshift_username = awsuser
redshift_password = XXXXX
redshift_hostname =  XXXXX
redshift_role = RedShiftLoadRole
redshift_port = 5439
redshift_database = dev
account_id = XXXXX
aws_region = XXXXX

[reddit_config]
secret = XXXXX
developer = XXXXX
name = XXXXX
client_id = XXXXX
```

### Docker and Airflow

The pipeline is scheduled to get executed once every day using Airflow. There are 3 scripts in the extraction folder.

1. `reddit_extract_data.py` which extract Reddit data and saves it to csv file.

2. `s3_data_upload_etl.py` which uploads the csv file to the S3 bucket.

3. `redshift_data_upload_etl.py` which copies the data from S3 bucket to Redshift cluster.

The script `etl_reddit_pipeline.py` in `airflow\dags` folder is the DAG which runs daily to execute the above three files using Bash commands.

In order to set up the pipeline, first install Docker and Docker Compose. All the services needed for Airflow are defined in the `docker-compose.yaml` file. The `volumes` parameter is updated so that the local file system is connected to docker containers. The AWS  credentials are also mounted to the docker containers as ready only. 


Docker is used for containerization. 
All services needed for Airflow is defined in `docker-compose.yaml` file. 

In order to run Airflow, follow the below commands.
If you are runnning on Linux, run the following commands.

```
cd airflow

# Create folders required by airflow. 
# dags folder has already been created, and 
# contains the dag script utilised by Airflow
mkdir -p ./logs ./plugins

# This Airflow quick-start needs to know your
# host user id
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Initialize the airflow database. This will take a few minutes. 
```
sudo docker-compose up airflow-init
```

Create the airflow containers. This will take some time to rum.
```
sudo docker-compose up
```
Now, you can login at  http://localhost:8080.

Use the following command to shut down the container.

```
docker-compose down
```

Or if you want stop and delete containers, delete volumes with database data and download images, run the following. This can be useful if you want to remove everything and start from scratch. 

```
docker-compose down --volumes --rmi all

```




















