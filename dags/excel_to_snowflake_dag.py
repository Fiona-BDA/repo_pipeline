from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from etl.excel_to_snowflake_etl import excel_to_snowflake_etl
from etl.new_task import new_task_function
# add the new function here 
from etl.new_task_Fiona import new_task_function_Fiona

from etl.ETL_S3_SNOWFLAKES import execute_snowflake_sql
from etl.sf_to_postgresql import sf_to_postgresql
from dotenv import load_dotenv
load_dotenv()

with DAG(
    dag_id="excel_to_snowflake",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    etl_task = PythonOperator(
        task_id="excel_to_snowflake_etl",
        python_callable=excel_to_snowflake_etl,
    )

    new_task = PythonOperator(
        task_id="new_task",
        python_callable=new_task_function
    )
    SHAMPOO_task = PythonOperator(
        task_id="SHAMPOO_task",
        python_callable= new_task_function_Fiona
    )


    # Set task dependencies
    etl_task >> new_task >> SHAMPOO_task

