import runpod
import requests
import os
import time
import base64

BFL_API_KEY = os.environ.get("BFL_API_KEY")

def handler(event):
    try:
        # Get prompt from user request
        prompt = event["input"]["prompt"]
        width = event["input"].get("width", 1024)
        height = event["input"].get("height", 1024)

        # Submit generation request
        response = requests.post(
            "https://api.bfl.ai/v1/flux-2-pro",
            headers={
                "accept": "application/json",
                "x-key": BFL_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "width": width,
                "height": height
            },
        ).json()

        polling_url = response["polling_url"]

        # Poll until ready
        while True:
            poll = requests.get(
                polling_url,
                headers={"x-key": BFL_API_KEY}
            ).json()

            if poll["status"] == "Ready":
                image_url = poll["result"]["sample"]
                break

            if poll["status"] == "Error":
                return {"error": "Generation failed"}

            time.sleep(2)

        # Download image and convert to base64
        image_bytes = requests.get(image_url).content
        image_base64 = base64.b64encode(image_bytes).decode()

        return {"image_base64": image_base64}

    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
