resource "aws_iam_role" "ec2_kinesis_role" {
  name = "ec2-kinesis-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ec2_kinesis_write_policy" {
  name = "EC2KinesisWritePolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "kinesis:PutRecord",
        "kinesis:PutRecords",
        "kinesis:DescribeStream"
      ],
      Resource = aws_kinesis_stream.data_ingestion_stream.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_kinesis_policy_attach" {
  role       = aws_iam_role.ec2_kinesis_role.name
  policy_arn = aws_iam_policy.ec2_kinesis_write_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-kinesis-instance-profile"
  role = aws_iam_role.ec2_kinesis_role.name
}

# ---------------------------
# IAM Role and Policy for Lambda to read from Kinesis and write to DynamoDB
# ---------------------------

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
