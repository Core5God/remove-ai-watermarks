"""Windows desktop launcher backend for 水印清除助手."""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file


APP_NAME = "水印清除助手"
# 发布前只需替换为你的真实小红书主页链接，无需修改界面代码。
XIAOHONGSHU_URL = "https://motion.beastle.cn/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif"}
MAX_BATCH = 10


def resource_dir() -> Path:
    """Return bundled resources both in source mode and in PyInstaller mode."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent))


def user_data_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return root / "ShuiYinQingChuZhuShou"


def get_upload_dir() -> Path:
    path = user_data_dir() / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_command(mode: str, source: Path, output: Path, options: dict) -> list[str]:
    """Call the packaged Python module, never a PATH-dependent CLI executable."""
    command = [sys.executable, "-m", "remove_ai_watermarks.cli", mode, str(source), "-o", str(output)]
    if mode in {"all", "visible"}:
        if options.get("inpaint") is False:
            command.append("--no-inpaint")
        if options.get("inpaint_method"):
            command.extend(["--inpaint-method", str(options["inpaint_method"])])
        if options.get("strip_metadata") is False:
            command.append("--keep-metadata")
    if mode in {"all", "invisible"}:
        for key, flag in (("strength", "--strength"), ("steps", "--steps"), ("device", "--device"), ("humanize", "--humanize"), ("max_resolution", "--max-resolution")):
            value = options.get(key)
            if value is not None and value != "auto":
                command.extend([flag, str(value)])
    if mode == "metadata":
        command = [sys.executable, "-m", "remove_ai_watermarks.cli", "metadata", "--remove", str(source), "-o", str(output)]
        if options.get("remove_all"):
            command.append("--remove-all")
    return command


def run_command(command: list[str], timeout: int = 600) -> tuple[int, str, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "处理超时，请尝试较小的图片或降低处理强度。"
    except FileNotFoundError:
        return -1, "", "程序组件不完整，请重新安装。"


app = Flask(__name__, static_folder=str(resource_dir() / "static"))


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/config")
def config():
    return jsonify(app_name=APP_NAME, xiaohongshu_url=XIAOHONGSHU_URL)


@app.post("/api/upload")
def upload():
    files = request.files.getlist("file")
    if not files:
        return jsonify(error="请选择图片"), 400
    if len(files) > MAX_BATCH:
        return jsonify(error=f"一次最多处理 {MAX_BATCH} 张图片"), 400
    records = []
    upload_dir = get_upload_dir()
    for file in files:
        if not file.filename or not allowed(file.filename):
            continue
        job_id = uuid.uuid4().hex[:12]
        ext = file.filename.rsplit(".", 1)[1].lower()
        name = f"{job_id}.{ext}"
        file.save(upload_dir / name)
        records.append({"job_id": job_id, "filename": name, "original": Path(file.filename).name, "size": (upload_dir / name).stat().st_size})
    return jsonify(files=records) if records else (jsonify(error="没有可处理的图片"), 400)


@app.post("/api/process/<job_id>")
def process(job_id: str):
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    source = get_upload_dir() / filename
    if not source.exists() or not source.name.startswith(job_id):
        return jsonify(error="找不到原始图片"), 404
    extension = source.suffix
    output_name = f"{job_id}_clean{extension}"
    output = get_upload_dir() / output_name
    code, stdout, stderr = run_command(build_command(data.get("mode", "all"), source, output, data.get("options", {})))
    if code == 0 and not output.exists():
        shutil.copy2(source, output)
    if code == 0:
        return jsonify(output=output_name, stdout=stdout, warning="未发现可处理水印时会保留原图" if not stdout else "")
    return jsonify(error=stderr or stdout or "处理失败"), 500


@app.get("/api/preview/<filename>")
def preview(filename: str):
    path = get_upload_dir() / Path(filename).name
    return send_file(path) if path.exists() else (jsonify(error="图片不存在"), 404)


@app.get("/api/download/<filename>")
def download(filename: str):
    path = get_upload_dir() / Path(filename).name
    return send_file(path, as_attachment=True, download_name=path.name) if path.exists() else (jsonify(error="图片不存在"), 404)


@app.post("/api/download-zip")
def download_zip():
    filenames = (request.get_json(silent=True) or {}).get("filenames", [])
    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in filenames:
            path = get_upload_dir() / Path(filename).name
            if path.exists():
                archive.write(path, f"clean_{path.name}")
    bundle.seek(0)
    return send_file(bundle, mimetype="application/zip", as_attachment=True, download_name="cleaned_images.zip")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False)
