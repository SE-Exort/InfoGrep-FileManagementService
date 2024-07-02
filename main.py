from fastapi import FastAPI;
import uvicorn
from Endpoints.Endpoints import router
InfoGrepFileManagementService = FastAPI();

InfoGrepFileManagementService.include_router(router)
if __name__ == "__main__":
    uvicorn.run(InfoGrepFileManagementService, host="0.0.0.0", port=8002)