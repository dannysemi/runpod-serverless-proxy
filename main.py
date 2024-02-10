# Importing necessary libraries
from fastapi import FastAPI, APIRouter, Request, HTTPException
from runpod_serverless import ApiConfig, RunpodServerless, Params
from fastapi.responses import StreamingResponse, JSONResponse
import json, time
from uvicorn import Config, Server
from pathlib import Path

# Initializing variables
model_data = {
    "object": "list",
    "data": []
}

configs = []

def run(config_path: str, host: str = "127.0.0.1", port: str = "3000"):
    if config_path:
        config_dict = load_config(config_path)  # function to load your config file

        for config in config_dict["models"]:
            config_model = {
                "url": f"https://api.runpod.ai/v2/{config['endpoint']}",
                "api_key": config_dict["api_key"],
                "model": config["model"],
                **({"timeout": config["timeout"]} if config.get("timeout") is not None else {}),
                **({"use_openai_format": config["use_openai_format"]} if config.get("use_openai_format") is not None else {}),
                **({"batch_size": config["batch_size"]} if config.get("batch_size") is not None else {}),
            }
            configs.append(ApiConfig(**config_model))
        for api in configs: print(api)

        model_data["data"] = [{"id": config["model"], 
            "object": "model", 
            "created": int(time.time()), 
            "owned_by": "organization-owner"} for config in config_dict["models"]]
        config = Config(
            app=app,
            host=config_dict.get("host", host),
            port=config_dict.get("port", port),
            log_level=config_dict.get("log_level", "info"),
        )
    else:
        config = Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
        )
    server = Server(config=config)
    server.run()

def load_config(config_path):
    config_path = Path(args.config)
    with open(config_path) as f:
        return json.load(f)

# Function to get configuration by model name
def get_config_by_model(model_name):
    for config in configs:
        if config.model == model_name:
            return config
        
# Function to format the response data
def format_response(data):
    openai_like_response = {
        'id': data['id'],
        'object': 'text_completion',
        'created': int(time.time()),
        'model': 'gpt-3.5-turbo-instruct',
        'system_fingerprint': "fp_44709d6fcb",
        'choices': [
            {
                'index': 0,
                'text': data['output'][0]['choices'][0]['tokens'][0],
                'logprobs': None,
                'finish_reason': 'stop' if data['status'] == 'COMPLETED' else 'length'
            }
        ],
        'usage': {
            'prompt_tokens': data['output'][0]['usage']['input'],
            'completion_tokens': data['output'][0]['usage']['output'],
            'total_tokens': data['output'][0]['usage']['input'] + data['output'][0]['usage']['output']
        }
    }

    return openai_like_response

# Creating API router
router = APIRouter()

params = Params()

# API endpoint for chat completions
@router.post('/chat/completions')
async def request_chat(request: Request):
    try:
        data = await request.json()
        model = data.get("model")
        if not model:
            return JSONResponse(status_code=400, content={"detail": "Missing model in request."})
        
        api = get_config_by_model(model)
        payload = data.get("messages")
        params_dict = params.dict()
        params_dict.update(data)
        new_params = Params(**params_dict)
        runpod: RunpodServerless = RunpodServerless(api=api, params=new_params)
        
        if(data["stream"]==False):
            response = get_chat_synchronous(runpod, payload)
            return response
        else:
            stream_data = get_chat_asynchronous(runpod, payload)
            response = StreamingResponse(content=stream_data, media_type="text/event-stream")
            response.body_iterator = stream_data.__aiter__()
            return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# API endpoint for completions
@router.post('/completions')
async def request_prompt(request: Request):
    try:
        data = await request.json()
        model = data.get("model")
        if not model:
            return JSONResponse(status_code=400, content={"detail ": "Missing model in request."})
        payload = data.get("prompt")[0]
        api = get_config_by_model(model)
        
        params_dict = params.dict()
        params_dict.update(data)
        new_params = Params(**params_dict)
        runpod: RunpodServerless = RunpodServerless(api=api, params=new_params)
        return get_synchronous(runpod, payload)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
# Function to get chat synchronously
def get_chat_synchronous(runpod, chat):
    # Generate a response from the runpod
    response = runpod.generate(chat)
    # Check if the response is not cancelled
    if(response ['status'] != "CANCELLED"):
            # Extract data from the response
            data = response["output"][0]
    else:
        # If the request is cancelled, raise an exception
        raise HTTPException(status_code=408, detail="Request timed out.")
    return data

# Function to get chat asynchronously
async def get_chat_asynchronous(runpod, chat):
    # Generate a response from the runpod in an asynchronous manner
    async for chunk in runpod.stream_generate(chat):
        # Check if the chunk is not cancelled
        if(chunk['status'] != "CANCELLED"):
            # Prepare the chat message for SSE
            prepared_message = prepare_chat_message_for_sse(chunk["stream"][0]["output"])
            # Encode the prepared message
            data = f'data: {prepared_message}\n\n'.encode('utf-8')
            yield data
        else:
            # If the request is cancelled, raise an exception
            raise HTTPException(status_code=408, detail="Request timed out.")

# Function to get synchronous response
def get_synchronous(runpod, prompt):
    # Generate a response from the runpod
    response = runpod.generate(prompt)
    # Check if the response is not cancelled
    if(response['status'] != "CANCELLED"):
            # Format the response
            data = format_response(response)
    else:
        # If the request is cancelled, raise an exception
        raise HTTPException(status_code=408, detail="Request timed out.")
    return data

# Function to prepare chat message for SSE
def prepare_chat_message_for_sse(message: dict) -> str:
    # Check if 'choices' in message and if it's not empty
    if 'choices' in message and message['choices']:
            # Loop through all choices
            for choice in message['choices']:
                # Check if 'delta' and 'content' in choice
                if 'delta' in choice and 'content' in choice['delta']:
                    # Join the content list into a string
                    joined_content = ''.join(choice['delta']['content'])
                    # Update the 'content' in 'delta' with the joined string
                    choice['delta']['content'] = joined_content
    # Return the message as a JSON string
    return json.dumps(message)

# Create a FastAPI application
app = FastAPI()

# Include the router in the application
app.include_router(router)

# Endpoint to list all models
@app.get("/models")
async def list_models():
    return model_data

# Endpoint to get a specific model
@app.get("/models/{model_id}")
async def get_model(model_id):
    # Function to find a model by id
    def find_model(models, id):
        return next((model for model in models['data'] if model['id'] == id), None)
    # Return the found model
    return find_model(model_data, model_id)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the config file", type=str, default=None)
    parser.add_argument("-e", "--endpoint", help="API endpoint", type=str, default=None)
    parser.add_argument("-k", "--api_key", help="API key", type=str, default=None)
    parser.add_argument("-m", "--model", help="Model", type=str, default=None)
    parser.add_argument("-t", "--timeout", help="Timeout", type=int, default=None)
    parser.add_argument("-o", "--use_openai_format", help="Use OpenAI format", type=bool, default=None)
    parser.add_argument("-b", "--batch_size", help="Batch size", type=int, default=None)
    parser.add_argument("--host", help="Host", type=str, default="127.0.0.1")
    parser.add_argument("--port", help="Port", type=int, default=3000)
    args = parser.parse_args()

    if args.config:
        run(args.config)
    else:
        config_model = {
            "url": f"https://api.runpod.ai/v2/{args.endpoint}",
            "api_key": args.api_key,
            "model": args.model,
            **({"timeout": args.timeout} if args.timeout is not None else {}),
            **({"use_openai_format": args.use_openai_format} if args.use_openai_format is not None else {}),
            **({"batch_size": args.batch_size} if args.batch_size is not None else {}),
        }
        configs.append(ApiConfig(**config_model))
        run(None, host=args.host, port=args.port)

