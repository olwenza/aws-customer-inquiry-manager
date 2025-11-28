# 🚀 Project Title

AWS - Customer Inquiry Manager

## Description
Project handles customers inquiries via a business website


# 📝 Outline 
1. Build a simple web app on EC2
2. AWS Bedrock reads and interprets message content
3. Store on inquiry data to RDS/Mysql
4. Depending on message data categorization, notification send via SES
5. Create Cloudwatch events to trigger daily checks for auto follow-up

# 🛠 Tech Stack
| Technology         | Purpose               |
| -------------------|-----------------------|
| Terraform          | Create environment.   |
| AWS EC2            | Web server            |
| AWS Bedrock        | Build gen AI apps     |
| AWS RDS            | Data Management       |
| AWS SES            | Email notification    |
| AWS Cloudwatch     | Trigger notifications |
| React              | UI library            |
| Redux Toolkit      | State management      |
| React Router       | Routing               |
| Axios              | HTTP requests         |
| Vite               | Build tool            |
| Tailwindcss        | CSS library           |
| AWS Incognito      | User management       |
| AWS Lambda         | Handle chatbot code   |
| AWS API GW         | Route Lambda calls    |



## Getting Started

### Dependencies
 
* Install Homebrew if not already installed
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
 
 * Update Homebrew
 ```
 brew update
 ```

* Install AWS CLI
```
brew install awscli
```

* Verify installation.
```
awscli --version
```
 
* Configure awscli with account credentials
```
awscli configure
```

* Install AWS Serverless Application Model  (SAM) - need for running Lambda locally
```
brew install aws-sam-cli
```

### Installing

* TBD/NA

### Executing program
#### - Create website in s3 bucket with auto deploy via github actions
1. Create s3 bucket for react app
```
aws s3 mb s3://landing-page-dev-ivan \
    --region us-east-1
``` 

2. Enable static website hosting for created bucket
```
aws s3 website landing-page-dev-ivan \
    --index-document index.html \
    --error-document error.html
```

3. Create origin acccess control - Save the returned Id → OAC_ID (E2DCGHQQAAYKAH)
```
aws cloudfront create-origin-access-control \
  --origin-access-control-config '{
    "Name": "react-oac",
    "OriginAccessControlOriginType": "s3",
    "SigningBehavior": "always",
    "SigningProtocol": "sigv4"
  }'
```

4. Create distribution - Save the returned distribution ARN → DIST_ARN 
```
aws cloudfront create-distribution \
  --distribution-config  file://distribution-config.json
```
 
5. Attach bucket policy that allows CloudFront to read objects from the S3 bucket (update BUCKET_NAME and DIST_ARN)
```
aws s3api put-bucket-policy \
  --bucket landing-page-dev-ivan \
  --policy file://cf-bucket-policy.json
```

6. Create IAM user with programmatic access
```
aws iam create-user --user-name github-actions-deployer
```

7. Create access and secret keys - save output values for github use
```
aws iam create-access-key --user-name github-actions-deployer
```

8. Create policy to allow user to deploy to s3 - save output ARN
```
aws iam create-policy \
    --policy-name GitHubActionsDeployPolicy \
    --policy-document file://github-actions-policy.json
```

9. Attach the policy to the IAM user - get $ARN from previous step
```
aws iam attach-user-policy \
  --user-name github-actions-deployer \
  --policy-arn {$ARN}
```

10. Make some changes and push to project dev branch (landinghttps://github.com/olwenza/landing-page/) to trigger github auction to deploy to s3

11. Get CloudFront URL
```
aws cloudfront list-distributions \
  --query "DistributionList.Items[].{Id:Id,DomainName:DomainName}" \
  --output table
```

12. View the website - copy and paste domain name from previous step on your browser and hard reset page.

#### - Create lambda function for chatbot
1. Create/Update a new managed IAM policy for the lamda role
```
aws iam create-policy \
  --policy-name BedrockInlinePolicy \
  --policy-document file://bedrock-inline-policy.json
```

2. Attach the newly created policy to the Lambda role.(get policy-arn from previous step)
```
aws iam attach-role-policy \
  --role-name lambda-website-uptime-monitor-role \
  --policy-arn arn:aws:iam::697227439720:policy/BedrockInlinePolicy
```

3. Create file for lambda function and add code
```
touch chat-bot.py
```

4. Compile code to spot any errors
```
python chat-bot.py
```

5. Zip chat-bot.py file for deployment to AWS lambda
```
zip function.zip chat-bot.py
```

5.  Create lambda function in aws for bedrock chat bot
```
aws lambda create-function \
  --function-name chatBot \
  --runtime python3.12 \
  --role arn:aws:iam::697227439720:role/lambda-website-uptime-monitor-role \
  --handler chat-bot.lambda_handler \
  --zip-file fileb://function.zip
```

6. Create template.yaml file for your local config/env
```
touch template.yaml
```

7. Test lamda function locally
```
echo '{"message": "How do I book?"}' | sam local invoke ChatBotFunction --event -
```

8. Test live functioning chatbot 
```
https://d11atov17l37i4.cloudfront.net/
```

## Authors

Contributors names and contact info

Ivan Augustino
[@ivanaugustino](https://www.linkedin.com/in/ivanaugustino/)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [General Public License (GPL) - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)