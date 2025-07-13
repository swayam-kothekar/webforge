import boto3
import os
import mimetypes
import uuid
import datetime
import sys
from botocore.exceptions import ClientError

def generate_bucket_name():
    date = datetime.datetime.utcnow().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:6]
    return f"static-site-{date}-{uid}"

def print_progress(current, total, message=""):
    """Print progress bar"""
    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r[{bar}] {percentage:.1f}% {message}", end='', flush=True)
    if current == total:
        print()

def deploy_static_site(directory, bucket_name, region, clean=False):
    s3 = boto3.client('s3', region_name=region)

    # Step 1: Create bucket if it doesn't exist
    exists, bucket_name = bucket_exists(s3, bucket_name)
    if not exists:
        create_bucket(s3, bucket_name, region)
        print(f"[OK] Bucket created: {bucket_name}")
    else:
        print(f"[INFO] Bucket already exists: {bucket_name}")

    # Step 2: Configure bucket for static website hosting
    enable_static_website_hosting(s3, bucket_name)
    print("[OK] Static website hosting enabled")

    # Step 3: Clean old files if requested
    if clean:
        delete_existing_objects(s3, bucket_name)
        print("[CLEAN] Removed existing files from bucket")

    # Step 4: Upload files
    uploaded_files = upload_directory(s3, directory, bucket_name)
    print(f"[OK] Uploaded {len(uploaded_files)} files from {directory}")

    # Step 5: Make all files public
    set_bucket_policy_public(s3, bucket_name)

    # Step 6: Print the website URL
    print()
    print(f"Your website is now live!")
    print(f"   URL: http://{bucket_name}.s3-website-{region}.amazonaws.com")
    print()


def create_bucket(s3, bucket_name, region):
    print(f"[INFO] Creating bucket in region: {region}")
    if region == "us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

def bucket_exists(s3, bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True, bucket_name  # Bucket exists and accessible
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return False, bucket_name  # Doesn't exist, safe to create
        elif error_code == '403':
            # Bucket exists but not owned → suggest new
            new_name = f"{bucket_name}-{uuid.uuid4().hex[:6]}"
            print(f"[WARN] Bucket '{bucket_name}' exists but you do not own it or it's in a different region.")
            print(f"[SWITCHING] Using a new bucket name: {new_name}")
            return False, new_name
        else:
            print(f"[ERROR] Unexpected error checking bucket: {e}")
            sys.exit(1)

def enable_static_website_hosting(s3, bucket_name):
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'error.html'}
        }
    )

def delete_existing_objects(s3, bucket_name):
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        keys = [{'Key': obj['Key']} for obj in response['Contents']]
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': keys})

def upload_directory(s3, directory, bucket_name):
    uploaded = []
    files_to_upload = []
    
    # First, collect all files to upload
    for root, _, files in os.walk(directory):
        for file in files:
            local_path = os.path.join(root, file)
            files_to_upload.append(local_path)
    
    total_files = len(files_to_upload)
    
    for i, local_path in enumerate(files_to_upload):
        s3_key = os.path.relpath(local_path, start=directory).replace("\\", "/")
        content_type, _ = mimetypes.guess_type(local_path)
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        s3.upload_file(local_path, bucket_name, s3_key, ExtraArgs=extra_args)
        uploaded.append(s3_key)
        
        # Show progress
        print_progress(i + 1, total_files, f"({i + 1}/{total_files}) {s3_key}")
        
    return uploaded


def set_bucket_policy_public(s3, bucket_name):
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }]
    }

    # Ensure public access is allowed
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )
    
    s3.put_bucket_policy(Bucket=bucket_name, Policy=str(policy).replace("'", '"'))