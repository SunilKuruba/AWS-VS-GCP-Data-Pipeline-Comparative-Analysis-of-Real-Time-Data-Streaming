resource "aws_kinesis_stream" "data_ingestion_stream" {
  name             = "data-ingestion-kinesis"
  shard_count      = 1
  retention_period = 24
}
