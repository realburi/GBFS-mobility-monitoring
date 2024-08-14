import json
import boto3 
from urllib.parse import unquote_plus
import psycopg2
import os

s3 = boto3.client('s3')

# Environment variables
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

def lambda_handler(event, context):
    for record in event['Records']:
        # Extract bucket name and object key from the S3 event
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        processed_data = process_json_file(bucket, key)
        print(processed_data)
        save_to_database(processed_data, city=key.split('_')[1])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def save_to_database(processed_data, city):
    conn = None
    try:
        # Connect to QuestDB
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        # Sample data
        data = processed_data
        
        # Insert data into QuestDB
        insert_query = """
        INSERT INTO my_table (current_range_meters, is_disabled_count, is_reserved_count, city, timestamp) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_query, 
            (data['current_range_meters'], data['is_disabled_count'], data['is_reserved_count'], city, data['timeStamp'])
        )
        conn.commit()
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data inserted into QuestDB!')
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
    
    finally:
        if conn is not None:
            conn.close()

def process_json_file(bucket, key):
    try:
        # Fetch the file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        # Load JSON data
        json_data = json.loads(file_content)
        result = {
            "timeStamp": json_data['last_updated'],
            "current_range_meters": 0,
            "is_disabled_count": 0,
            "is_reserved_count": 0
        }
        for data in json_data['data']['vehicles']:
            result['current_range_meters'] += data['current_range_meters']
            result['is_disabled_count'] += data['is_disabled']
            result['is_reserved_count'] += data['is_reserved']
        
        return result

    except Exception as e:
        print(f"Error processing file {key} from bucket {bucket}: {e}")
        raise e

# if __name__ == '__main__':
#     with open('lambda_function/event.json', 'r') as f:
#         event = json.load(f)
#     result = lambda_handler(event=event, context=None)
#     print(result)