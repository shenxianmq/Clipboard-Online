from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import base64
import uuid
import yaml
import shutil
import time


working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

if not os.path.exists("./download"):
    os.mkdir("./download")

if not os.path.exists("./config"):
    os.mkdir("./config")

clipboard_path = os.path.abspath(os.path.join("./config", "clipboard.yaml"))


def read_clipboard():
    if not os.path.exists(clipboard_path):
        with open(clipboard_path, "w", encoding="utf-8") as file:
            yaml.dump(
                [], file, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
    with open(clipboard_path, "r", encoding="utf-8") as file:
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

    with open(clipboard_path, "w", encoding="utf-8") as file:
        yaml.dump(
            data, file, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


def append_item(item):
    clipboard_list.append(item)
    yaml_dump(clipboard_list)


def remove_item(item):
    clipboard_list.remove(item)
    yaml_dump(clipboard_list)


def empty_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)


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
    filename = request.filename
    file = os.path.abspath(os.path.join("./download", filename))
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
    append_item({"type": "file", "filename": filename, "uuid": str(uuid.uuid4())})
    return {"message": "Content added successfully"}


@app.post("/content")
async def add_content(item: ContentItem):
    content = item.content
    append_item({"type": "string", "content": content, "uuid": str(uuid.uuid4())})
    return {"message": "Content added successfully"}


@app.get("/")
async def get_clipboard(request: Request):
    reversed_list = clipboard_list[::-1]
    context = {
        "request": request,
        "clipboard_list": reversed_list,
        "title": "Clipboard Content",
        "template_file": "clipboard.html",
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/add_content")
async def main_page(request: Request):
    context = {
        "request": request,
        "title": "Add Content",
        "template_file": "add_content.html",
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/upload_file")
async def upload_file(request: Request):
    context = {
        "request": request,
        "title": "Upload File",
        "template_file": "upload_file.html",
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join("./download", file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    append_item({"type": "file", "filename": file.filename, "uuid": str(uuid.uuid4())})
    return {"filename": file.filename}


@app.post("/delete")
async def delete(request: Request):
    data = await request.json()
    uuid = data["uuid"]
    temp_list = clipboard_list[:]
    for item in temp_list:
        if uuid == item["uuid"]:
            if item["type"] == "file":
                file_path = os.path.join("./download", item["filename"])
                if os.path.exists(file_path):
                    os.remove(file_path)
            remove_item(item)
            break
    return {"message": "success"}


@app.get("/paste")
async def paste(request: Request):
    content = clipboard_list[-1]["content"]
    return JSONResponse({"content": content})


@app.post("/clear_text")
async def clear_clipboard(request: Request):
    global clipboard_list
    new_licpboard_list = [item for item in clipboard_list if item["type"] != "string"]
    clipboard_list = new_licpboard_list[:]
    yaml_dump(clipboard_list)
    return {"message": "success"}


@app.post("/clear_files")
async def clear_clipboard(request: Request):
    global clipboard_list
    new_licpboard_list = [item for item in clipboard_list if item["type"] != "file"]
    clipboard_list = new_licpboard_list[:]
    download_path = os.path.abspath("./download")
    try:
        if os.path.exists(download_path):
            empty_directory(download_path)
    except:
        pass
    yaml_dump(clipboard_list)
    return {"message": "success"}


@app.post("/clear_clipboard")
async def clear_clipboard(request: Request):
    global clipboard_list
    clipboard_list = []
    download_path = os.path.abspath("./download")
    try:
        if os.path.exists(download_path):
            empty_directory(download_path)
    except:
        pass
    yaml_dump(clipboard_list)
    return {"message": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web:app", host="0.0.0.0", port=18095, reload=True)
