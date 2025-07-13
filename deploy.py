import argparse
import os
import sys
from s3_utils import deploy_static_site, generate_bucket_name

def print_logo():
    """Print the Deployr ASCII logo"""
    logo = """
    ██╗    ██╗███████╗██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
    ██║    ██║██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
    ██║ █╗ ██║█████╗  ██████╔╝█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
    ██║███╗██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
    ╚███╔███╔╝███████╗██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
     ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    
      ┌─────────────────────────────────────────────────────────────┐
      │                 Static Site Deployment Tool                 │
      │                 Deploy to AWS S3 with ease                  │
      └─────────────────────────────────────────────────────────────┘
    """
    print(logo)

def main():
    print_logo()
    
    parser = argparse.ArgumentParser(
        description="Deploy a static website to AWS S3 with one command."
    )

    parser.add_argument(
        '--dir',
        type=str,
        default='.',
        help='Path to local directory to deploy (default: current directory)'
    )

    parser.add_argument(
        '--bucket',
        type=str,
        default=None,
        help='S3 bucket name (default: auto-generated if not provided)'
    )

    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS region to deploy in (default: us-east-1)'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean existing files in the bucket before uploading'
    )

    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.dir):
        print(f"[ERROR] Directory '{args.dir}' does not exist.")
        sys.exit(1)

    # Validate index.html presence
    index_path = os.path.join(args.dir, "index.html")
    if not os.path.isfile(index_path):
        print("[ERROR] 'index.html' not found in the specified directory. Required for S3 static website hosting.")
        sys.exit(1)

    # Generate bucket name if not provided
    bucket_name = args.bucket or generate_bucket_name()
    if not args.bucket:
        print(f"[INFO] No bucket name provided. Using generated name: {bucket_name}")

    print("[INFO] Starting deployment...")

    deploy_static_site(
        directory=args.dir,
        bucket_name=bucket_name,
        region=args.region,
        clean=args.clean
    )

if __name__ == "__main__":
    main()