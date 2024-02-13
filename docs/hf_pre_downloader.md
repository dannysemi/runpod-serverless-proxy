# Guide for Using hf-pre-downloader Runpod Template

This is a recommended step before creating a serverless LLM endpoint. Follow the steps below to use the Runpod template:

1. **Create a Runpod Network Volume:** The size of the volume should be appropriate for the model being downloaded. The region should provide the necessary hardware to run the model. You can create a network volume from the [Storage section of the dashboard](https://www.runpod.io/console/user/storage).


2. **Create a GPU Pod:** Use the provided template to create a GPU pod. If available, a CPU pod can also be used. Any hardware should suffice, the pod is just being used to download the files. Use the following link to create the pod: [Create Pod](https://runpod.io/gsc?template=8ep9tsqvom&ref=rql9o4ou)

3. **Attach Network Volume to Pod:** Attach the network volume created in Step 1 to the pod. Overwrite the `MODEL_NAME` environment variable in the template with the name of the model you want to download. **Note**: Currently there is a UI bug on the deployment details screen when creating a pod that warns about a network volume not being attached even when one is present. This warning can be ignored as long as you have already attached the network volume.

4. **Run the Pod and Monitor Logs:** Run the pod and monitor the logs. When the full download path of the model and snapshot ID is printed, the download is complete.

5. **Terminate the Pod:** Once the download is complete, terminate the pod. The network volume is now ready to be used by your serverless endpoint.

The benefit of this method is that it is more cost-effective to use a pod for downloading the files than using serverless execution time.

# Disclaimer

Please be aware that this application uses cloud resources which may incur costs. These costs are dependent on the usage and the pricing model of the cloud service provider. 

By using this application, you acknowledge that you are fully responsible for any costs that may arise from its operation. As the developer of this application, I am not responsible for any charges you may incur while running this application.
