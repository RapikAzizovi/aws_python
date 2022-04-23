import time
import boto3


AWS_REGION = "us-east-1"
s3 = boto3.client("s3")
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
ZIPNAME = "lambda_function.zip"


def create_bucket(my_bucket):
    try:
        s3.create_bucket(Bucket=my_bucket)
    except Exception as ex:
        print(ex)


def aws_file():
    with open(ZIPNAME, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content


def create_lambda(my_lambda1):
    response = lambda_client.create_function(
        Code={
            'ZipFile': aws_file()
        },
        Description='Recognize object from photos',
        FunctionName=my_lambda1,
        Handler='lambda_function.lambda_handler',
        Publish=True,
        Role='arn:aws:iam::114232093311:role/LabRole',
        Runtime='python3.8',
    )
    return response


def add_permission(my_bucket, my_lambda1):
    lambda_client.add_permission(
        FunctionName=my_lambda1,
        StatementId='1',
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn=f'arn:aws:s3:::{my_bucket}',
    )


def s3_trigger(my_bucket, my_lambda1):
    add_permission(my_bucket, my_lambda1)
    response = s3.put_bucket_notification_configuration(
        Bucket=my_bucket,
        NotificationConfiguration={'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': f'arn:aws:lambda:{AWS_REGION}:114232093311:function:{my_lambda1}',
                'Events': [
                    's3:ObjectCreated:*'
                ],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name':  'suffix',
                                'Value': '.jpg'
                            },
                        ]
                    }
                }
            },
        ],
          },
        SkipDestinationValidation=True
    )
    return response


def upload_file(dog, my_bucket, file):
    try:
        s3.upload_file(dog, my_bucket, file)
        time.sleep(150)
        data = s3.get_object(Bucket=my_bucket, Key=file.replace('.jpg', '.json'))
        # data_exists = data.get_waiter('json exists')
        # data_exists.wait(data)
        contents = data['Body'].read()
        print(contents)
    except Exception as ex:
        print(f"Something went wrong :( {ex}")


def main(my_bucket, my_lambda1, dog):
    file = dog
    create_bucket(my_bucket)
    create_lambda(my_lambda1)
    s3_trigger(my_bucket, my_lambda1)
    upload_file(dog, my_bucket, file)


if __name__ == '__main__':
    main("my_bucket", "davaleba5lambda", "dog.jpg")