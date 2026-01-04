
import os
from fastapi import APIRouter, Depends
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.auth import *

static_router = APIRouter()

templates = Jinja2Templates("backend/routers/templates")


@static_router.get("/dify")
def redirect_to_new():
    return RedirectResponse(url="http://localhost/datasets", status_code=301)

@static_router.get("/{page}")
async def page(page:str, request: Request):
    return templates.TemplateResponse(f"{page}.html",{
            "request": request
        })


@static_router.get("/content/{owner}/{repo_name}/{path:path}")
def get_article_page1(request: Request, owner, repo_name, branch, path:str="", token: str = Depends(oauth2_scheme)):
    return templates.TemplateResponse("repo.html", {
        "request": request,  # 注意：TemplateResponse 需要传 request
        "app_data": {
            "jwt": token,
            "owner": owner,
            "repo_name": repo_name,
            "branch":branch,
            "path": path
        }
    })
