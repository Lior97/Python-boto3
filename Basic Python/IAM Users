import boto3

iam = boto3.client('iam')
iam_users = iam.list_users()

last_active_user = iam_users["Users"][0]

for iam_user in iam_users["Users"]:
    print(iam_user["UserName"])
    print(iam_user["PasswordLastUsed"])
    print("---------------------------")
    
    if last_active_user["PasswordLastUsed"] < iam_user["PasswordLastUsed"]:
        last_active_user = iam_user

print("Last active user:")
print(last_active_user["UserId"])
print(last_active_user["UserName"])
print(last_active_user["PasswordLastUsed"])
