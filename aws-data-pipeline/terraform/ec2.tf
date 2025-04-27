resource "aws_instance" "iot_data_source" {
  ami                    = "ami-0e449927258d45bc4"
  instance_type          = "t2.micro"
  iam_instance_profile   = aws_iam_instance_profile.ec2_instance_profile.name
  associate_public_ip_address = true
  user_data = <<EOF
#!/bin/bash
# Install dependencies
sudo yum update -y
sudo yum install -y python3-pip -y
sudo pip3 install boto3 requests

# Write data_source.py into EC2
cat <<EOPY > /home/ec2-user/data_source.py
${file("${path.module}/data_source.py")}
EOPY

# Set permissions and run
chmod +x /home/ec2-user/data_source.py
python3 /home/ec2-user/data_source.py
EOF
  vpc_security_group_ids = [aws_security_group.allow_https_only.id]

  tags = {
    Name = "iot-data-source-ec2"
  }
}
