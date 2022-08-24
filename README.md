# REDDIT DATA PIPELINE
The purpose of the project is to create a data pipeline to extract data from Reddit API and create a dashboard to analyse the data.
The data is extracted from the subreddit [r/Python](https://www.reddit.com/r/Python/).
The data is extracted daily and uploaded to S3 buckets, and copied to Redshift. 
The dashboard is created using Google Data Studio.

## Architecture

![workflow image](https://github.com/joyceannie/Reddit_Data_Pipeline/tree/main/images/Reddit Data Pipeline.drawio.png "Workflow Image")

1. Extract the data using [Reddit API](https://www.reddit.com/dev/api/)
2. Create AWS resources with Terraform
3. Load the data to [AWS S3](https://aws.amazon.com/s3/) bucket
4. Copy the data to [AWS Redshift](https://aws.amazon.com/redshift/)
5. Orchestrate with [Airflow](https://airflow.apache.org/) in [Docker](https://www.docker.com/)
6. Create dashboard [using Google Data Studio](https://datastudio.google.com/)


## Dashboard

<img src="https://github.com/joyceannie/Reddit_Data_Pipeline/tree/main/images/data_analysis.png">

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






