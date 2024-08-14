cd lambda_function
zip -r ../lambda_function.zip .
cd ..
aws s3 cp lambda_function.zip s3://gbfs-raw-data/lambda/lambda_function.zip
aws lambda update-function-code --function-name processData --s3-bucket gbfs-raw-data --s3-key lambda/lambda_function.zip 