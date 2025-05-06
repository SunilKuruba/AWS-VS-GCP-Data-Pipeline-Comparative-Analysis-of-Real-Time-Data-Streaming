resource "aws_instance" "iot_data_source" {
  ami                    = "ami-0e449927258d45bc4"
  instance_type          = "t2.micro"
  iam_instance_profile   = aws_iam_instance_profile.ec2_instance_profile.name
  associate_public_ip_address = true
  user_data = <<EOF
#!/bin/bash
# Install dependencies
sudo yum update -y
sudo yum install git -y
sudo yum install -y python3-pip -y
sudo pip3 install boto3 requests

# Run data source script
git clone https://github.com/SunilKuruba/aws-vs-gcp-data-pipeline.git
cd  aws-vs-gcp-data-pipeline/aws-data-pipeline
python3 data_source.py

EOF
  vpc_security_group_ids = [aws_security_group.allow_ssh_and_https.id]

  tags = {
    Name = "iot-data-source-ec2"
  }
}
