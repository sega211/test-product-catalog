from fastapi import FastAPI
app = FastAPI(title="Test Catalog API")

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "good"}