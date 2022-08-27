from datetime import datetime, timedelta
from textwrap import dedent
from airflow import DAG
from os import remove
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

'''
DAG used to perform 3 operations.
    1. Extract Reddit data
    2. Load data to S3 bucket
    3. Copy data to Redshift
'''

#output name of the extracted file. This filename is passed to each DAG task as input.
output_name = datetime.now().strftime('%Y-%m-%d')

# Run our DAG daily and ensures DAG run will kick off
# once Airflow is started, as it will try to "catch up"
schedule_interval = "@daily"
start_date = days_ago(1)

default_args = {"owner": "airflow", "depends_on_past": False, "retries": 1}

with DAG(
    dag_id="elt_reddit_pipeline",
    description='Reddit ELT pipeline',
    schedule_interval=schedule_interval,
    start_date=start_date,
    catchup=True,
    tags=["RedditETL"],
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    reddit_extract_data = BashOperator(
        task_id="extract_reddit_data",
        bash_command=f"python /opt/airflow/extraction/reddit_extract_data.py {output_name}",
        dag=dag,
    )
    reddit_extract_data.doc_md = "Extract Reddit data and store as CSV"
    
    s3_data_upload = BashOperator(
        task_id = "s3_data_upload",
        bash_command=f"python /opt/airflow/extraction/s3_data_upload.py {output_name}",
        dag=dag
    )
    s3_data_upload.doc_md = "Store data to S3 bucket"
    
    redshift_data_upload_etl = BashOperator(
        task_id = "redshift_data_upload_etl",
        bash_command=f"python /opt/airflow/extraction/redshift_data_upload_etl.py {output_name}",
        dag=dag
    ) 
    redshift_data_upload_etl.doc_md = "copy S3 bucket data to Redshift"

    reddit_extract_data >> s3_data_upload >> redshift_data_upload_etl