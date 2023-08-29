resource "aws_s3_bucket" "mybuketaf12eq" {
    bucket="mndsdnfsdfsndfksdf"
    acl="private"
    tags ={
        Name = "testingbucket",
        Enviornment = "testing"}
}

output "s3BucketOutput" {
    value = aws_s3_bucket.mybuketaf12eq.id

    }