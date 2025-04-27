resource "aws_security_group" "allow_https_only" {
  name = "allow-https-only"

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
