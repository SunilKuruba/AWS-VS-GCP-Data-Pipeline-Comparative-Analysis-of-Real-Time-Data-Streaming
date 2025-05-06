# Lambda Function
resource "aws_lambda_function" "data_processing_lambda" {
  function_name = "data-processing-lambda"

  filename         = "lambda_function_payload.zip"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.data_storage.name
    }
  }
}

# Lambda Trigger (Kinesis → Lambda)
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.data_ingestion_stream.arn
  function_name     = aws_lambda_function.data_processing_lambda.arn
  starting_position = "LATEST"
  batch_size        = 100
  maximum_batching_window_in_seconds = 1
}
