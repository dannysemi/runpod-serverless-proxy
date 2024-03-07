# Guide for Creating a Serverless LLM Endpoint for Goliath-longLORA-120b-rope8-32k-fp16-AWQ

[Updated 03/07/2024]

Configuration for this model [TheBloke/Goliath-longLORA-120b-rope8-32k-fp16-AWQ](https://huggingface.co/TheBloke/Goliath-longLORA-120b-rope8-32k-fp16-AWQ) is nearly identical to the one I use in the [MiquMaid](./miqumaid_guide.md). So I will only highlight the differences here.

**Note**: There's probably enough available vram with this setup to use a larger `MAX_MODEL_LENGTH` and context size within ST, but I haven't tested anything higher than `8192`.

## Pre-download Model

Follow the instructions provided in [hf-pre-downloader](./hf_pre_downloader.md) guide to load the model in the network volume before creating the endpoint. This will save on execution time.

I use a network volume with a size of `65 gb`. Make sure the region you choose has 48gb hardware configurations available.

## Endpoint Configuration

![endpoint configuration](image-10.png)

Note: This image has an Idle Timeout setting of 5 seconds, but for the purposes of this guide a 1-second timeout is more appropriate. 

![template configuration](image-11.png)

~~**Important:** Be sure to use the new `registry.gitlab.com/dannysemi/worker-vllm:eager_mode` worker or this configuration will not work.~~

Newest worker-vllm supports openai-compatible API. Use `runpod/worker-vllm:0.3.1` for the container image.

Here are the template configuration values:

| Parameter | Value |
|-----------|-------|
| `MODEL_NAME` | `TheBloke/Goliath-longLORA-120b-rope8-32k-fp16-AWQ` |
| `QUANTIZATION` | `awq` |
| `CUSTOM_CHAT_TEMPLATE` | See code block below |
| `MAX_MODEL_LENGTH` | `8192` |
| `ENFORCE_EAGER` | `1` |
| `TRUST_REMOTE_CODE` | `1` |
| `DISABLE_LOG_REQUESTS` | `1` |
| `GPU_MEMORY_UTILIZATION` | `0.98` |
| `TENSOR_PARALLEL_SIZE` | `2` |

Chat template:
```markdown
{% for message in messages %}{{message['role']|upper + ':' + '\n' + message['content'] + '\n'}}{% endfor %}\nASSISTANT:\n
```

## Runpod Serverless OpenAI-compatible API settings for Sillytavern

Use Chat Completion -> Custom (OpenAI-compatible) options in the API and Chat Completion Source dropdowns.

For Custom Endpoint (Base URL) you will use the Runpod api endpoint url with your endpoint id in place of `endpoint_id`:
`https://api.runpod.ai/v2/endpoint_id/openai/v1`

You will need to paste your Runpod API key in the Custom API key field.

Click Connect and the Models dropdown should populate with the name of the model. Select it and everything should be ready.

Note: If you did not run a test request on the endpoint dashboard, or pre-load the model files, it could take several minutes for the endpoint to become active. Check that the endpoint is functioning properly before attempting to connect.
