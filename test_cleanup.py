import boto3
import cleanup
from moto import mock_aws


def test_get_args(mocker):
    """
    Tests that user input is correctly parsed into arguments.
    """
    test_args = ["--bucket", "test-bucket", "--keep", "5"]
    mocker.patch("sys.argv", ["prog_name"] + test_args)
    args = cleanup.get_args()
    assert args.bucket == "test-bucket"
    assert args.keep == 5


@mock_aws
def test_cleanup():
    """
    Tests that the cleanup function deletes all but the most recent X folders in an S3 bucket.
    """

    # Create a bucket and add 50 folders to it
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3.create_bucket(Bucket=bucket_name)

    for i in range(50):
        s3.put_object(Bucket=bucket_name, Key=f"folder{i}/file.txt", Body=b"Test")

    # Run the cleanup function
    cleanup.cleanup(s3, bucket_name, 5)

    # Check that the correct number of folders were deleted
    remaining_objects = s3.list_objects(Bucket=bucket_name)["Contents"]
    assert len(remaining_objects) == 5

    # Delete all objects in the bucket, then delete the bucket
    s3_objects = s3.list_objects(Bucket=bucket_name).get("Contents", [])
    for obj in s3_objects:
        s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
    s3.delete_bucket(Bucket=bucket_name)
