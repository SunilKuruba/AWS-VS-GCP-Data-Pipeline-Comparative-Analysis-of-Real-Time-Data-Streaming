provider "aws" {
  region = "us-east-1"
}

# IAM Role for EC2 to access Kinesis
resource "aws_iam_policy" "ec2_kinesis_write_policy" {
  name = "EC2KinesisWritePolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "kinesis:PutRecord",
          "kinesis:PutRecords",
          "kinesis:DescribeStream"
        ],
        Resource = aws_kinesis_stream.data_ingestion_stream.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_kinesis_policy_attach" {
  role       = aws_iam_role.ec2_kinesis_role.name
  policy_arn = aws_iam_policy.ec2_kinesis_write_policy.arn
}

# EC2 Instance
resource "aws_instance" "iot_data_source" {
  ami                    = "ami-060a84cbcb5c14844" # Amazon Linux
  instance_type          = "t2.micro"
  iam_instance_profile   = aws_iam_instance_profile.ec2_instance_profile.name
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              sudo yum install python3-pip -y
              sudo pip3 install boto3
              cd /home/ec2-user/
              python3 data_source.py
              EOF

  tags = {
    Name = "iot-data-source-ec2"
  }

  vpc_security_group_ids = [aws_security_group.allow_all.id]
}

resource "aws_security_group" "allow_https_only" {
  name = "allow_https_only"

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-kinesis-instance-profile"
  role = aws_iam_role.ec2_kinesis_role.name
}

# Kinesis Stream
resource "aws_kinesis_stream" "data_ingestion_stream" {
  name             = "data-ingestion-kinesis"
  shard_count      = 1
  retention_period = 24
}

# DynamoDB Table
resource "aws_dynamodb_table" "data_storage" {
  name         = "data-storage-dynamodb"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "entry_id"
    type = "N" # Number
  }

  hash_key = "entry_id"
}

# IAM Role for Lambda (Kinesis + DynamoDB)
resource "aws_iam_role" "lambda_role" {
  name = "LambdaKinesisDynamoDBAccess"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "LambdaKinesisDynamoDBPolicy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListStreams"
        ],
        Resource = aws_kinesis_stream.data_ingestion_stream.arn
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem"
        ],
        Resource = aws_dynamodb_table.data_storage.arn
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "data_processing_lambda" {
  function_name = "data-processing-lambda"

  filename         = "lambda_function_payload.zip" # <-- You need to create a deployment package (.zip)
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  reserved_concurrent_executions = 1
  role             = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.data_storage.name
    }
  }
}

# Lambda Trigger (Kinesis)
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.data_ingestion_stream.arn
  function_name     = aws_lambda_function.data_processing_lambda.arn
  starting_position = "LATEST"
  batch_size        = 100
  maximum_batching_window_in_seconds = 1
}
