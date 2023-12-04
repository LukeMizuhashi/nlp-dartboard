from google.cloud import bigquery

# Initialize a BigQuery client with your own project
client = bigquery.Client(project='cpc-labeling')

# Define the public project containing the dataset you wish to query
public_project = 'patents-public-data'
public_dataset_id = 'patents'

# Get the dataset reference from the public project
dataset_ref = client.dataset(public_dataset_id, project=public_project)

# Get the dataset IAM policy
policy = client.get_iam_policy(dataset_ref)

# List all members and roles in the dataset IAM policy
for binding in policy.bindings:
    role = binding['role']
    members = binding['members']
    print(f"Role: {role}, Members: {members}")
