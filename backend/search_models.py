import urllib.request
import json

url = "https://huggingface.co/api/models?search=deepfake&pipeline_tag=image-classification&sort=downloads"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())
    for i, model in enumerate(data[:10]):
        print(f"{i+1}. {model['id']} (Downloads: {model.get('downloads', 0)})")
