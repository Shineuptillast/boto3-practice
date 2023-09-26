import os
import json
import boto3
import mongodb_last_date
import datetime
import certifi

import requests

bucket_name=os.getenv("BUCKET_NAME")

ca = certifi.where()
mongo_client = mongodb_last_date.mongodb_connection()

collection = os.getenv('COLLECTION')
db = mongo_client.create_database(os.getenv("DATABASE"))

if collection not in db.list_collection_names():
    db.create_collection(os.getenv("COLLECTION"))

data_source_url="https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?field=all&size=100&sort=relevance_desc&format=json&no_aggs=false&no_highlight=false&date_received_max={}&date_received_min={}"

def get_data_from_mongo():
    
    
    if collection in mongo_client.list_collection():
        result = mongo_client.latest_to_date(collection)
        if result:
            from_date=result[0]['to_date']
        else:
            from_date = "2023-08-17"
            from_date = datetime.datetime.strptime(from_date,"%Y-%m-%d")      
    to_date = datetime.datetime.now()

    response = {
        "form_date": from_date.strftime("%Y-%m-%d"),
        "to_date": to_date.strftime("%Y-%m-%d"),
        "from_date_obj": from_date,
        "to_date_obj": to_date
    }
    return response
def save_from_date_to_date(data, status=True):
    data.update({"status": status})
    mongo_client.insert_one_record(collection,data)

def lambda_handler(event,context):
    print(event,context)
    from_date,to_date,from_date_obj,to_date_obj = get_data_from_mongo().values()
    
    if to_date==from_date:
        return {
            'statusCode': 200,
            'body': json.dumps('Pipeline has already downloaded all data upto yesterday')
        }
    
    data_url=data_source_url.format(to_date,from_date)
    data = requests.get(data_url, params={'User-agent': f'your bot '})
  
    finance_complaint_data = list(map(lambda x: x["_source"],filter(lambda x: "_source" in x.keys(),json.loads(data.content))))
    print(finance_complaint_data)
    save_from_date_to_date({"from_date": from_date_obj, "to_date": to_date_obj})
    
    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket_name, f"inbox/{from_date.replace('-','_')}_{to_date.replace('-','_')}_finance_complaint.json")
    s3object.put(
        Body=(bytes(json.dumps(finance_complaint_data).encode('UTF-8')))
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }




