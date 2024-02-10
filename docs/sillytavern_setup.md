# Guide to Integrating Runpod Serverless Proxy with the SillyTavern AI Server

1. Navigate to the API connections menu. Select `Chat Completion` and `Custom (OpenAI-compatible)`.
2. Enter the host:port specified in your config in the custom endpoint field. For example, `http://localhost:3000`.
3. Leave the API key field blank and click `Connect`.
4. If the server is configured correctly, the models dropdown will be populated with the list of models you have configured for your API. Select your model.
5. Use the "AI response configuration" (far left) menu to customize your completion settings.
6. Add settings not directly available in the AI response configuration menu but are available to vllm to the `Additional Parameters` option in the API connections menu. For example, `- min_p: 0.1`. Refer to the vllm documentation for a complete list of available settings.
7. Customize your prompts on the "AI response configuration" menu and as long as the chat template for your model is configured properly you won't need to add any special tokens or anything to any of the prompts.

Note: The AI response formatting menu (marked by an 'A' icon) does not significantly affect chat completions, with the possible exception of the `Context Formatting` options. Adjust these settings according to your specific needs.
