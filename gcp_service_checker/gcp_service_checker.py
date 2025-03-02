# Purpose: Can be useful to check the enabled api services on the listed projects

# How to run the script: 
#  pip3 install -r requirements.txt
#  python3 <script name>.py

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.cloud import storage
import csv
import subprocess

output_path = "result_api_check.csv"
output_paas = "result_paas_check.csv"
output_bucket = "result_bucket_check.csv"

def check_enabled_services(project_id):
    credentials = GoogleCredentials.get_application_default()

    project = f'projects/{project_id}'

    service = discovery.build('serviceusage', 'v1', credentials=credentials)
    request = service.services().list(parent=project,filter='state:ENABLED')

    response = ''

    try:
        response = request.execute()
    except Exception as e:
        print(e)
        exit(1)

    # FIX - This code does not process the nextPageToken
    next = response.get('nextPageToken')

    services = response.get('services')

    for index in range(len(services)):
        item = services[index]

        name = item['config']['name']
        state = item['state']

        print("%s,%s,%s" % (project_id, name, state))
        data_full = [[ project_id, name, state ]]

        with open(output_path, 'a') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data_full)

def check_paas_is_exists(project_id):
    
    result_cloudsql = result_memcached = result_redis = result_pubsub = ""
    cloudsql_is_exists = memcached_is_exists = redis_is_exists = pubsub_is_exists = True

    print(f"checking PaaS existance on project {project_id}")

    try:
        result_cloudsql = subprocess.check_output(f"gcloud sql instances list --project {project_id} --quiet", shell=True, text=True)
        result_redis = subprocess.check_output(f"gcloud redis instances list --project {project_id} --region asia-southeast1 --quiet", shell=True, text=True)
        result_memcached = subprocess.check_output(f"gcloud memcache instances list --project {project_id} --region asia-southeast1  --quiet", shell=True, text=True)
        result_pubsub = subprocess.check_output(f"gcloud pubsub topics list --project {project_id} --quiet", shell=True, text=True)
    except Exception as e:
        print(e)
    
    if result_cloudsql == "":
        cloudsql_is_exists = False
    
    if result_redis == "":
        redis_is_exists = False
    
    if result_memcached == "":
        memcached_is_exists = False

    if result_pubsub == "":
        pubsub_is_exists = False

    summary = cloudsql_is_exists or redis_is_exists or memcached_is_exists or pubsub_is_exists

    data_full = [[ project_id, cloudsql_is_exists, redis_is_exists, memcached_is_exists, pubsub_is_exists, summary]]

    with open(output_paas, 'a') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(data_full)

def get_bucket_list_for_project(project_id):
    """Returns a list of GCS buckets for a given project ID."""
    buckets = []
    try:
        client = storage.Client(project=project_id)
        buckets = client.list_buckets()

        return [bucket.name for bucket in buckets]
    except Exception as e:
        print(e)
        return []

def check_bucket(project_id):

    print(f"checking bucket on project {project_id}")

    data_full = []
    buckets = []
    try:
        # buckets = subprocess.check_output(f"gcloud storage ls --project {project_id} --quiet", shell=True, text=True)
        buckets = get_bucket_list_for_project(project_id)
    except Exception as e:
        print(e)

    print(buckets)

    for bucket in buckets:
        print("%s,%s" % (project_id, bucket))
        data_full = [[ project_id, bucket ]]

        with open(output_bucket, 'a') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data_full)

    
    if not buckets:
        print("  No buckets found.\n")
    else:
        print("  Buckets:\n")
        for bucket in buckets:
            print(f"    - {bucket}\n")
    print("\n")


def main():
    with open("project_list.txt", "r") as file:
        projects = [line.strip() for line in file.readlines()]

    for project_id in projects:
        check_enabled_services(project_id=project_id)
        check_paas_is_exists(project_id=project_id)
        check_bucket(project_id=project_id)

if __name__ == '__main__':
    main()