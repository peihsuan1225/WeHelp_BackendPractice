from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class postRequest(BaseModel):
    text: str
    image: str

posts = []

@app.post("/api/post")
async def save_post_info(postContent: postRequest):
    if not postContent.image or not postContent.text:
        result = {"error": True, "message": "獲取 Post 內容失敗"}
        return JSONResponse(content=result, status_code=400)
    try:
        posts.insert(0, postContent.dict())
        result = {"success": True, "message": "Post 內容已保存"}
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        result = {"error": True, "message": f"保存Post內容失敗: {str(e)}"}
        return JSONResponse(content=result, status_code=500)

@app.get("/api/post")
async def get_post_info():
    result = {"success": True, "data": posts}
    return JSONResponse(content=result, status_code=200)

@app.get("/", response_class=FileResponse)
async def get_html():
    return FileResponse("static/index.html", media_type="text/html")