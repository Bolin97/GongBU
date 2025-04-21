
import os
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware


static_router = APIRouter()

templates = Jinja2Templates("backend/routers/templates")

@static_router.get("/{page}")
async def page(page:str, request: Request):
    return templates.TemplateResponse(f"{page}.html",{
            "request": request
        })