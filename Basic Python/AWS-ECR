import boto3
from operator import itemgetter

ecr_client = boto3.client('ecr')

# Get all ECR repos and print names
repos = ecr_client.describe_repositories()['repositories']
for repo in repos:
    print(repo['repositoryName'])

print("-----------------------")

# For one specific repo, get all the images and print them out sorted by date

repo_name = "{your repo name}"
images = ecr_client.describe_images(
    repositoryName=repo_name
)

image_tags = []

for image in images['imageDetails']:
    image_tags.append({
        'tag': image['imageTags'],
        'pushed_at': image['imagePushedAt']
    })

images_sorted = sorted(image_tags, key=itemgetter("pushed_at"), reverse=True)
for image in images_sorted:
    print(image)
