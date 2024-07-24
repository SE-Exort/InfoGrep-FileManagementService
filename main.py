from fastapi import FastAPI;
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Endpoints.Endpoints import router
InfoGrepFileManagementService = FastAPI();

InfoGrepFileManagementService.include_router(router)
InfoGrepChatroomService.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
if __name__ == "__main__":
    uvicorn.run(InfoGrepFileManagementService, host="0.0.0.0", port=8002)
