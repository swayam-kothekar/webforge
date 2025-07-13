# 🌐 WebForge

**WebForge** is a blazing-fast command-line tool to deploy static websites directly to AWS S3.  
Ideal for launching portfolios, mini-projects, landing pages, or demos with a single command.

---

## ✨ Features

- 🪣 Automatically creates and configures S3 buckets for static hosting
- 📂 Recursively uploads your static files (HTML/CSS/JS/images/etc.)
- 🌐 Instantly generates a public-accessible URL
- 🧼 Optionally cleans the bucket before uploading new files
- 🧪 Validates `index.html` presence before deployment
- 🛡 Sets necessary bucket policies for public access

---

## ⚙️ Installation

> 🐍 Requires **Python 3.7+** and an AWS account with proper credentials configured.

```bash
git clone https://github.com/your-username/webforge.git
cd webforge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
python deploy.py --dir ./my-site
```

### Available Flags

| Flag        | Description                                            |
|-------------|--------------------------------------------------------|
| `--dir`     | Directory containing static site files (default: `.`)  |
| `--bucket`  | Custom S3 bucket name (optional)                       |
| `--region`  | AWS region (default: `us-east-1`)                      |
| `--clean`   | Clean existing files before uploading                  |

---

### Example

```bash
python deploy.py --dir ./portfolio --region us-west-2 --clean
```

If `--bucket` is omitted, WebForge generates a unique name like:

```text
webforge-site-20250713-abc123
```

---


## 🔐 AWS IAM Permissions Required

Make sure your IAM user has:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:CreateBucket",
    "s3:PutBucketPolicy",
    "s3:PutBucketWebsite",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket",
    "s3:GetBucketLocation",
    "s3:PutPublicAccessBlock"
  ],
  "Resource": "*"
}
```

---

