from fastapi import FastAPI

app = FastAPI(title="ObRail API")


@app.get("/health")
def health_check():
    return {"status": "ok"}