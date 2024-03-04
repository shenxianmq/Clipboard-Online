from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import base64
import uuid
import yaml


working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

if not os.path.exists("./download"):
    os.mkdir("./download")


def read_clipboard():
    with open("clipboard.yaml", "r", encoding="utf-8") as file:
        clipboard_list = yaml.safe_load(file)
    if clipboard_list:
        return clipboard_list
    else:
        return []


def yaml_dump(data):
    if len(clipboard_list) > history_num:
        item = clipboard_list[0]
        if item["type"] == "file":
            file_path = os.path.join("./download", item["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
        clipboard_list.remove(item)

    with open("clipboard.yaml", "w", encoding="utf-8") as file:
        yaml.dump(
            data, file, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
clipboard_list = read_clipboard()
history_num = 300


class FileItem(BaseModel):
    content: str
    filename: str


class ContentItem(BaseModel):
    content: str


class DownloadRequest(BaseModel):
    filename: str


@app.post("/download")
def download_file(request: DownloadRequest):
    print(request.filename)
    filename = request.filename
    file = os.path.abspath(os.path.join("./download", filename))
    print(file)
    try:
        # 返回文件给客户端进行下载
        return FileResponse(file, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
def download_file(filename: str):
    file = os.path.abspath(os.path.join("./download", filename))
    try:
        # 返回文件给客户端进行下载
        return FileResponse(file, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(item: FileItem):
    content = item.content
    filename = item.filename
    file = base64.b64decode(content)
    with open(f"./download/{filename}", "wb") as f:
        f.write(file)
    clipboard_list.append(
        {"type": "file", "filename": filename, "uuid": str(uuid.uuid4())}
    )
    yaml_dump(clipboard_list)
    return {"message": "Content added successfully"}


@app.post("/content")
async def add_content(item: ContentItem):
    content = item.content
    clipboard_list.append(
        {"type": "string", "content": content, "uuid": str(uuid.uuid4())}
    )
    yaml_dump(clipboard_list)
    return {"message": "Content added successfully"}


@app.get("/clipboard")
async def get_clipboard(request: Request):
    reversed_list = clipboard_list[::-1]
    return templates.TemplateResponse(
        "clipboard.html", {"request": request, "clipboard_list": reversed_list}
    )


@app.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/add")
async def main_page(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.get("/paste")
async def paste(request: Request):
    content = clipboard_list[-1]["content"]
    return JSONResponse({"content": content})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web:app", host="0.0.0.0", port=18095, reload=False)
