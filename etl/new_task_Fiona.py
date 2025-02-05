def new_task_function_Fiona():

    print("This is a new task")
    # Import necessary libraries
    from pyspark.sql import SparkSession # type: ignore
    # pyspark.sql is a python library, SparkSession is a function from this libary
  
    import os

    # Load environment variables


    # Create a Spark session
    spark = SparkSession.builder \
        .appName("Snowflake to PostgreSQL") \
        .config("spark.jars.packages", "net.snowflake:spark-snowflake_2.12:2.10.0-spark_3.2,net.snowflake:snowflake-jdbc:3.13.3,org.postgresql:postgresql:42.2.23") \
        .getOrCreate()

    # Define Snowflake options
    snowflake_options = {
        "sfURL": f"{os.getenv('SNOWFLAKE_ACCOUNT')}.snowflakecomputing.com",
        "sfUser": os.getenv('SNOWFLAKE_USER'),
        "sfPassword": os.getenv('SNOWFLAKE_PASSWORD'),
        "sfDatabase": os.getenv('SNOWFLAKE_DATABASE'),
        "sfSchema": os.getenv('SNOWFLAKE_SCHEMA'),
        "sfWarehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
        "sfRole": os.getenv('SNOWFLAKE_ROLE')
    }

    def load_and_join_tables(snowflake_options: dict):
        # Load data from Snowflake
        Fleet_Service_df = spark.read \
            .format("snowflake") \
            .options(**snowflake_options) \
            .option("dbtable", "Fleet_Service_Data") \
            .load()
        
        ## Load and join Sales_Order_data
        #sales_order_df = spark.read \
        #    .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Sales_Order_data") \
        #    .load()
        # joined_df = sales_df.join(sales_order_df, on=['SALESORDERLINEKEY'], how='inner')
        
        ## Load and join Sales_Territory_data
        #sales_territory_df = spark.read \
        #   .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Sales_Territory_data") \
        #    .load()
        # joined_df = joined_df.join(sales_territory_df, on=['SALESTERRITORYKEY'], how='inner')
        
        ## Load and join Reseller_data
        #reseller_df = spark.read \
        #    .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Reseller_data") \
        #    .load()
        #joined_df = joined_df.join(reseller_df, on=['RESELLERKEY'], how='inner')
        
        ## Load and join Date_data
        #date_df = spark.read \
        #    .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Date_data") \
        #    .load()
        #joined_df = joined_df.join(date_df, joined_df["ShipDateKey"] == date_df["DateKey"], how='inner')
        
        ## Load and join Product_data
        #product_df = spark.read \
        #    .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Product_data") \
        #    .load()
        #joined_df = joined_df.join(product_df, on=['PRODUCTKEY'], how='inner')
        
        ## Load and join Customer_data
        #customer_df = spark.read \
        #    .format("snowflake") \
        #    .options(**snowflake_options) \
        #    .option("dbtable", "Customer_data") \
        #    .load()
        #joined_df = joined_df.join(customer_df, on=['CUSTOMERKEY'], how='inner')
        
        return Fleet_Service_df

    def load_from_snowflake_to_postgresql(snowflake_options: dict, pg_url: str, pg_properties: dict):
        Fleet_Service_df = load_and_join_tables(snowflake_options)
        
        # Ensure there are no empty column names and no duplicate column names
        Fleet_Service_df = Fleet_Service_df.toDF(*[col.replace(' ', '_').replace('"', '').replace('-', '_') if col else f"col_{i}" for i, col in enumerate(Fleet_Service_df.columns)])
        Fleet_Service_df = Fleet_Service_df.toDF(*[f"{col}_{i}" if Fleet_Service_df.columns.count(col) > 1 else col for i, col in enumerate(Fleet_Service_df.columns)])
        print(Fleet_Service_df.columns)
        
        # Truncate the existing table in PostgreSQL before loading new data
        from psycopg2 import connect
        # psycopg2 is a library for python

        conn = None  # Initialize conn to None
        try:
            # Ensure the URL is correctly formatted for psycopg2
            if pg_url.startswith('jdbc:'): #check if the postgresql url start with 'jdbc'
                pg_url = pg_url[5:] 
                # take the url from the 5th character
            
            conn = connect(  # create a connection to postgresql
                dbname=pg_url.split('/')[-1],
                user=pg_properties['user'],
                password=pg_properties['password'],
                host=pg_url.split('/')[2].split(':')[0],
                port=pg_url.split('/')[2].split(':')[1] if ':' in pg_url.split('/')[2] else '5432'
            )
            with conn.cursor() as cursor:  # use the connection to truncate the existing table
                cursor.execute("TRUNCATE TABLE Fleet_Service_Data RESTART IDENTITY CASCADE")
                conn.commit()
                print("Fleet_Service_Data table truncated successfully.")
        except Exception as e:
            print(f"Failed to truncate table Fleet_Service_Data: {e}")
        finally:
            if conn:
                conn.close()
        
        # Ensure the URL is correctly formatted for Spark JDBC
        jdbc_url = f"jdbc:postgresql://{pg_url.split('//')[1]}"

        # Write joined data to PostgreSQL
        if Fleet_Service_df:
            Fleet_Service_df.write \
                .jdbc(url=jdbc_url, table="Fleet_Service_Data", mode="overwrite", properties=pg_properties)
            print("Joined data written to PostgreSQL")
        else:
            print("No sheets could be joined due to missing common columns.")

    # Example usage
    load_from_snowflake_to_postgresql(snowflake_options, os.getenv('POSTGRESQL_URL'), {
        'user': os.getenv('POSTGRESQL_USER'),
        'password': os.getenv('POSTGRESQL_PASSWORD'),
        'driver': os.getenv('POSTGRESQL_DRIVER'),
        'currentSchema': os.getenv('POSTGRESQL_SCHEMA')
    })

    print('Joined data loaded from Snowflake and written to PostgreSQL successfully.')





   # new_task_function_Fiona()