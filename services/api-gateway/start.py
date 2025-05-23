import uvicorn

from configs import configs

if __name__ == "__main__":
    uvicorn.run(
        "app:gateway",
        host="0.0.0.0",
        port=8061,
        reload=configs.DEBUG_MODE,
        use_colors=True,
        date_header=True,
    )
