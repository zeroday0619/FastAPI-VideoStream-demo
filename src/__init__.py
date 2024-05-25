from pathlib import Path
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import StreamingResponse, UJSONResponse
from fastapi.templating import Jinja2Templates

class System(object):
    CHUNK_SIZE = 1024*1024
    name = "걸즈 밴드 크라이"
    video_list = [
        '제1화 도쿄 으랏차.mp4',
        '제2화 야행성 생물 세 마리.mp4', 
        '제3화 엉뚱한 문답.mp4',  
        '제4화 감사 (놀람).mp4',  
        '제5화 노랫소리여 일어나라.mp4',  
        '제6화 아웃사이더 찬가.mp4',  
        '제7화 이름을 붙여 주겠어.mp4',  
        '제8화 만약 네가 운다면.mp4'
    ]
    def __init__(self, app: FastAPI):
        self.app = app
        self.templates = Jinja2Templates(directory="templates")
        
        self.init()
    
    def init(self):
        self.app.add_api_route("/", self.list_videos, methods=["GET"])
        self.app.add_api_route("/stream", self.index, methods=["GET"])
        self.app.add_api_route("/video", self.video, methods=["GET"])
        self.add_exception_handlers()

    def add_exception_handlers(self):
        @self.app.exception_handler(HTTPException)
        async def custom_http_exception_handler(request: Request, exc: HTTPException):
            if exc.status_code == 404:
                return self.templates.TemplateResponse("404.html", {"request": request}, status_code=404)
            return UJSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    async def list_videos(self, request: Request):
        videos = []
        for index, title in enumerate(self.video_list):
            videos.append({
                "part": index+1,
                "title": self.name + ": " + title.split(".")[0]
            })
        
        return self.templates.TemplateResponse("index.html", {"request": request, "videos": videos})



    async def index(self, request: Request):
        try:
            part = int(request.query_params.get("part", 1))
        except TypeError:
            raise HTTPException(status_code=404, detail="File not found")
        try:
            videos = [{
                "part": part,
                "title": self.name + ": " + self.video_list[part-1].split(".")[0],
            }]
        except IndexError:
            print(0)
            raise HTTPException(status_code=404, detail="File not found")
        return self.templates.TemplateResponse("stream.html", {"request": request, "videos": videos})
    
    async def video(self, request: Request, range: str = Header(None)):
        part = request.query_params.get("part")
        name = self.name
        match part:
            case "1":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[0]}"
            case "2":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[1]}"
            case "3": 
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[2]}"
            case "4":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[3]}"
            case "5":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[4]}"
            case "6":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[5]}"
            case "7":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[6]}"
            case "8":
                file = f"/home/zeroday0619/Videos/{name}/{self.video_list[7]}"
            case _:
                raise HTTPException(status_code=404, detail="File not found")
            
        video_path = Path(file)
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if not range:
            raise HTTPException(status_code=416, detail="Missing range header")

        try:
            start, end = range.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else start + self.CHUNK_SIZE
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid range format")

        file_size = video_path.stat().st_size
        end = min(end, file_size - 1)

        if start >= file_size or start < 0 or end < start:
            raise HTTPException(status_code=416, detail="Requested range not satisfiable")

        with open(file, "rb") as video:
            video.seek(start)
            data = video.read(end - start + 1)

        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1)
        }

        return StreamingResponse(iter([data]), status_code=206, headers=headers, media_type="video/mp4")