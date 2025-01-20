from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import os

from Endpoints.Endpoints import router

InfoGrepFileManagementService = FastAPI();

os.environ["no_proxy"]="*"
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
origins = [
    "*",
]

@InfoGrepFileManagementService.middleware("http")
async def add_open_telemetry_headers(request: Request, call_next):
    response = await call_next(request)
    for k, v in request.headers.items():
        if k.startswith("x-") or k.startswith("trace"):
            response.headers[k] = v
    return response

InfoGrepFileManagementService.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

InfoGrepFileManagementService.include_router(router)

if __name__ == "__main__":
    uvicorn.run(InfoGrepFileManagementService, host="0.0.0.0", port=8002)
