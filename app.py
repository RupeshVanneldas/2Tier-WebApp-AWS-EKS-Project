from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Environment variables from ConfigMap and Secrets
DBHOST = os.environ.get("DBHOST")
DBPORT = int(os.environ.get("DBPORT", "3306"))
DBUSER = os.environ.get("DBUSER")  # From Secret
DBPWD = os.environ.get("DBPWD")    # From Secret
DATABASE = os.environ.get("DATABASE", "employees")
BG_IMAGE_URL = os.environ.get("BG_IMAGE_URL")  # From ConfigMap (e.g., s3://my-bucket/Cats.png)
GROUP_NAME = os.environ.get("GROUP_NAME", "MyGroup")  # From ConfigMap
GROUP_SLOGAN = os.environ.get("GROUP_SLOGAN", "Innovate and Excel")  # From ConfigMap

# AWS credentials from Secrets
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN")  # Optional, if using temporary credentials

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,  # Optional
    region_name='us-east-1'  # Change to your region
)

# Local directory to store downloaded images
LOCAL_IMAGE_DIR = "/app/static/images"
if not os.path.exists(LOCAL_IMAGE_DIR):
    os.makedirs(LOCAL_IMAGE_DIR)
else:
    logger.info(f"Directory {LOCAL_IMAGE_DIR} already exists. No need to create it.")

# Download background image from S3
def download_s3_image():
    try:
        if not BG_IMAGE_URL.startswith("s3://rupesh-project-bucket/"):
            raise ValueError("BG_IMAGE_URL must be an S3 URL (e.g., s3://bucket-name/image.png)")
        
        # Parse S3 URL (e.g., s3://my-bucket/Cats.png)
        bucket_name = BG_IMAGE_URL.split('/')[2]
        key = '/'.join(BG_IMAGE_URL.split('/')[3:])
        local_image_path = os.path.join(LOCAL_IMAGE_DIR, os.path.basename(key))
        
        # Download image from S3
        logger.info(f"Downloading image from S3: {BG_IMAGE_URL}")
        s3_client.download_file(bucket_name, key, local_image_path)
        logger.info(f"Image downloaded to: {local_image_path}")
        
        return os.path.basename(key)  # Return filename (e.g., Cats.png)
    except Exception as e:
        logger.error(f"Failed to download S3 image: {e}")
        return "default.png"  # Fallback image

# Download image at startup
image_filename = download_s3_image()
logger.info(f"Image filename: {image_filename}")

@app.context_processor
def inject_template_vars():
    image_url = url_for('static', filename=f'images/{image_filename}')
    logger.info(f"Background image URL: {image_url}")  # Log the image URL
    return dict(
        image_url=image_url,
        group_name=GROUP_NAME,
        group_slogan=GROUP_SLOGAN
    )

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html')

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    logger.info("Employee added successfully")
    return render_template('addempoutput.html', name=emp_name)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html")

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            output = {"error": "Employee not found"}
    except Exception as e:
        logger.error(f"Error fetching employee: {e}")
    finally:
        cursor.close()

    return render_template("getempoutput.html", **output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-url', required=False)
    args = parser.parse_args()

    if args.image_url:
        logger.info(f"Image URL from command line: {args.image_url}")
        os.environ['BG_IMAGE_URL'] = args.image_url
        image_filename = download_s3_image()

    app.run(host='0.0.0.0', port=81, debug=True)