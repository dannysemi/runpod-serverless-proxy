# Runpod Serverless Proxy

This is a FastAPI application providing an OpenAI-compatible API for sporadic text generation using models hosted on [Runpod](https://runpod.io) serverless infrastructure. It is not recommended for batch jobs or tasks with large run times.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- FastAPI
- A Runpod serverless endpoint running `runpod/worker-vllm:0.2.3`. See the [Setup Guide](./docs/runpod_endpoint.md) for instructions on setting this up.
- **New**: Optionally use `registry.gitlab.com/dannysemi/worker-vllm:eager_mode` worker for access to `enforce_eager` flag. This flag frees up vram occupied by CUDA graphs at the expense of execution speed. Overall quality remains the same.

### New guides for SillyTavern and hf-pre-downloader

- [hf-pre-downloader](./docs/hf_pre_downloader.md) - Reduce initial execution time on your endpoint by downloading the model files to the network volume using a pod in advance.
- [LoneStriker/MiquMaid-v2-70B-DPO-GPTQ guide](./docs/miqumaid_guide.md) - Complete guide to setting up this endpoint and accessing it through SillyTavern UI.
- [TheBloke/Goliath-longLORA-120b-rope8-32k-fp16-AWQ](./docs/goliath_guide.md) - Very similar to the MiquMaid guide, but uses 2x A40s in the configuration.

### Installing

1. Clone the repository
2. Navigate to the project directory
3. Install the package using pip:

```bash
pip install .
```

### Usage

The application provides the following API endpoints which mirror the OpenAI api:

- `POST /chat/completions`: Generate a chat completion
- `POST /completions`: Generate a completion
- `GET /models`: List all models (Note: streaming does not work for this endpoint.)
- `GET /models/{model_id}`: Get a specific model

To start the application, you can use the following command:

`python main.py --config "/path/to/config/file"`

You can also specify different parameters using command line arguments:

- `-c` or `--config`: Path to the config file. If this is provided, the application will load configurations from the specified file.
- `-e` or `--endpoint`: API endpoint ID. This is mandatory if not loading from a config file. An alphanumeric string that should be found on the endpoint details for your Runpod serverless endpoint.
- `-k` or `--api_key`: API key. This is mandatory if not loading from a config file. This is your Runpod API key.
- `-m` or `--model`: Model name. This is mandatory if not loading from a config file. Used for routing requests to a specific worker. You can choose to name your models whatever you want. This is how you will reference them in the api or in menus with connected apps. Note: you can have multiple models/runpod endpoints if using a config file.
- `-t` or `--timeout`: Timeout. *Default: 150*. Time in seconds before this app sends a request to cancel the job through runpod's api.
- `-o` or `--use_openai_format`: Use OpenAI format. *Default: 1*. Tells the api to attempt to send the job as an OpenAI chat completion. Will fail if the model is not configured to handle messages (should have a chat template in its config)
- `-b` or `--batch_size`: Batch size. *Default: 30*.
- `--host`: Host. *Default: 127.0.0.1*
- `--port`: Port. *Default: 3000*

If not loading from a config file, the `--endpoint`, `--api_key`, and `--model` arguments are mandatory. If any of these arguments are missing, the application will not start.

An example config file can be copied from `config.example.json` found in the root directory of this repo.

For example:

```bash
python main.py --endpoint "my_endpoint" --api_key "my_api_key" --model "my_model" --timeout 30 --use_openai_format 1 --batch_size 10 --host "0.0.0.0" --port 8000
```

## Built With

- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

# Disclaimer

Please be aware that this application uses cloud resources which may incur costs. These costs are dependent on the usage and the pricing model of the cloud service provider. 

By using this application, you acknowledge that you are fully responsible for any costs that may arise from its operation. As the developer of this application, I am not responsible for any charges you may incur while running this application.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details

## Acknowledgments

- Credit to [Pooya Haratian](https://github.com/pooyahrtn). An early version of their [OllamaRunpod](https://github.com/pooyahrtn/RunpodOllama) repository served as a basis for this project.