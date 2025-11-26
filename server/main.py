import io
import os

from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.params import Depends
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from server.service.dependencies import get_llm, get_tavily, get_predictor, get_workflow, get_vector_store

app = FastAPI()


@app.post("/api/predict")
async def predict(image: UploadFile, llm=Depends(get_llm), tavily=Depends(get_tavily),
                  predictor=Depends(get_predictor), workflow=Depends(get_workflow),
                  vector_store=Depends(get_vector_store)):
    contents = await image.read()

    img = Image.open(io.BytesIO(contents)).convert("RGB")
    inputs = {"image_buffer": img}
    result = await workflow.ainvoke(
        inputs,
        config={
            "configurable": {
                "llm": llm,
                "tavily": tavily,
                "predictor": predictor,
                "vector_store": vector_store,
            }
        }
    )

    return {"article": result["article"]}


current_dir = os.path.dirname(os.path.realpath(__file__))
build_dir = os.path.join(current_dir, "../frontend/dist")

if os.path.exists(build_dir):

    app.mount("/assets", StaticFiles(directory=os.path.join(build_dir, "assets")), name="assets")


    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(build_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        return FileResponse(os.path.join(build_dir, "index.html"))

else:
    print("React build directory not found. Run 'npm run build' in frontend.")
