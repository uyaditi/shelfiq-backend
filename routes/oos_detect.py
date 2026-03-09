from fastapi import APIRouter
from pydantic import BaseModel
from ultralytics import YOLO
import base64
import numpy as np
import cv2

router = APIRouter()
model = YOLO("shelf_model_best.pt")

class OOSRequest(BaseModel):
    image: str  # Base64-encoded image string

class OOSResponse(BaseModel):
    image: str
    confidence: float
    urgency: float


def decode_base64_image(base64_str: str):
    image_bytes = base64.b64decode(base64_str)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


@router.post("/oos_detect", response_model=OOSResponse)
async def detect_oos(request: OOSRequest):

    # Decode incoming image
    image = decode_base64_image(request.image)

    # Run YOLO inference
    results = model(image)

    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:

        # still return annotated image
        annotated = results[0].plot()

        _, buffer = cv2.imencode(".jpg", annotated)
        encoded_image = base64.b64encode(buffer).decode("utf-8")

        return OOSResponse(
            image=encoded_image,
            confidence=0.0,
            urgency=1.0
        )

    # Extract confidence
    confidences = boxes.conf.cpu().numpy()
    confidence = float(np.max(confidences))

    # Urgency logic
    urgency = max(0.0, 1 - (len(boxes) / 10))

    # Draw bounding boxes
    annotated = results[0].plot()

    # Convert to base64
    _, buffer = cv2.imencode(".jpg", annotated)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    return OOSResponse(
        image=encoded_image,
        confidence=confidence,
        urgency=float(urgency)
    )

