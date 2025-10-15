from fastapi import FastAPI

app = FastAPI(title="Smart Resume Screener API")

@app.get("/")
async def read_root():
    return {"message": "Smart Resume Screener API is running"}

# Mount parsing API
from api.parsing import app as parsing_app
app.mount("/api", parsing_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
