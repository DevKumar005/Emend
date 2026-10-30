import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import analysis, jobs, demo, health

app = FastAPI(
    title="Emend API",
    description="Fix it. Prove it. - Autonomous code-repair agent that verifies its work and honestly reports residual risks.",
    version="1.0.0"
)

# Enable CORS for local Vite dev server and web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(analysis.router)
app.include_router(jobs.router)
app.include_router(demo.router)
app.include_router(health.router)

# Serve built frontend if static directory exists (single-container deployment mode)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "Emend API is running. Fix it. Prove it.",
            "docs": "/docs",
            "health": "/api/health",
            "demo_repos": "/api/demo-repos"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("emend.api.main:app", host="0.0.0.0", port=port, reload=True)
