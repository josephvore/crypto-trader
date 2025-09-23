from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
