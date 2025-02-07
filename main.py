from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import os

from Endpoints.Endpoints import router
from InfoGrep_BackendSDK.middleware import TracingMiddleware, LoggingMiddleware
from InfoGrep_BackendSDK.infogrep_logger.logger import Logger

InfoGrepFileManagementService = FastAPI();

os.environ["no_proxy"]="*"
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
origins = [
    "*",
]

InfoGrepFileManagementService.add_middleware(LoggingMiddleware, logger=Logger("FileManagementServiceLogger"))
InfoGrepFileManagementService.add_middleware(TracingMiddleware)
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
