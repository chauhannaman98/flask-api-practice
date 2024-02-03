# CONTRIBUTING

## How to run the Docker file locally

```
docker run -dp 5000:5000 -w /app -v "<WORKING_DIR>:/app" <IMAGE-NAME> sh -c "flask run --host 0.0.0.0"
```