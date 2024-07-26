from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import boto3
import uuid
import aiomysql
import pytz

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIA5FTY65H7FN2FPL4G',
    aws_secret_access_key='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',
    region_name='us-west-1'
)
bucket_name = 'wehelp-backendpractice'

class postRequest(BaseModel):
    text: str
    image_url: str

posts = []

DATABASE = {
    'host': 'database-1.czmssmmqmyi7.us-west-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'OAfqTdZqCCeD3AluhyJz',
    'db': 'posts_db',
}

async def get_db_connection():
    return await aiomysql.connect(
        host=DATABASE['host'],
        port=DATABASE['port'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        db=DATABASE['db'],
        charset='utf8',
        autocommit=True
    )

@app.post("/api/post")
async def save_post_info(text: str = Form(...), image: UploadFile = File(...)):
    taiwan_tz = pytz.timezone('Asia/Taipei')
    taiwan_time = datetime.now(taiwan_tz).strftime('%Y-%m-%d %H:%M:%S')
    # print(f"Received text: {text}")
    # print(f"Received image: {image.filename}")

    if not text or not image:
        result = {"error": True, "message": "獲取 Post 內容失敗"}
        return JSONResponse(content=result, status_code=400)

    try:
        file_key = str(uuid.uuid4()) + '-' + image.filename
        
        s3_client.upload_fileobj(image.file, bucket_name, file_key)
        
        image_url = f"https://d194xlmnh8jllb.cloudfront.net/{file_key}"

        conn = await get_db_connection()
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO posts (text, image_url, created_at) VALUES (%s, %s, %s)",
                (text, image_url, taiwan_time)
            )
        await conn.ensure_closed()
        
        result = {"success": True, "message": "Post 內容已保存"}
        return JSONResponse(content=result, status_code=200)
    except NoCredentialsError:
        result = {"error": True, "message": "S3 凭证错误"}
        return JSONResponse(content=result, status_code=500)
    except Exception as e:
        result = {"error": True, "message": f"保存Post內容失敗: {str(e)}"}
        return JSONResponse(content=result, status_code=500)

@app.get("/api/post")
async def get_post_info():
    try:
            conn = await get_db_connection()
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM posts ORDER BY id DESC")
                posts = await cursor.fetchall()
            await conn.ensure_closed()

            for post in posts:
             post['created_at'] = post['created_at'].isoformat()

            # print(posts)
            
            result = {"success": True, "data": posts}
            # print(result)
            return JSONResponse(content=result, status_code=200)
    except Exception as e:
        # print(f"Error: {e}")
        result = {"error": True, "message": f"獲取 Post 內容失敗: {str(e)}"}
        return JSONResponse(content=result, status_code=500)


@app.get("/", response_class=FileResponse)
async def get_html():
    return FileResponse("static/index.html", media_type="text/html")