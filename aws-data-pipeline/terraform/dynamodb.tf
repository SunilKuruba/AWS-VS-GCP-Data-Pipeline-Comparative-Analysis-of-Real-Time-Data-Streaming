resource "aws_dynamodb_table" "data_storage" {
  name         = "data-storage-dynamodb"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "entry_id"
    type = "N"
  }

  hash_key = "entry_id"
}
