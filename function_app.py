import logging
import azure.functions as func
import requests
from azure.storage.blob import BlobServiceClient
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get data_link from query parameters or request body
    data_link = req.params.get('data_link')
    if not data_link:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            data_link = req_body.get('data_link')

    if data_link:
        try:
            # Fetch data from the provided link
            response = requests.get(data_link)
            response.raise_for_status()  # Raise an error if the request failed
            data = response.content

            # Upload data to Azure Blob Storage
            storage_account_name = "amldatacnak"  # Replace with your storage account name
            container_name = "amldata"  # Replace with your container name
            blob_service_client = BlobServiceClient.from_connection_string(
                "DefaultEndpointsProtocol=https;AccountName=amldatacnak;AccountKey=OD7x5wWUM2IoaFIUIVW1Sq8hI6HzKhnA7Rr4nI+9/OH0jElAD+eksiEoIsIyhjmSlgoynvE5cUwa+AStSBrKkQ==;EndpointSuffix=core.windows.net"
            )  # Replace with your connection string
            blob_client = blob_service_client.get_blob_client(container=container_name, blob="raw_data/data.csv")
            blob_client.upload_blob(data, overwrite=True)

            # Trigger the Databricks job to process the uploaded data
            databricks_instance = "https://adb-2432582280951251.11.azuredatabricks.net"  # Replace with your Databricks instance URL
            job_id = "340019621491816"  # Replace with your Databricks job ID
            token = "dapi95de85c674acac5783b7818d157be299"  # Replace with your Databricks token

            # Trigger the Databricks job
            databricks_response = requests.post(
                f"{databricks_instance}/api/2.0/jobs/run-now",
                headers={"Authorization": f"Bearer {token}"},
                json={"job_id": job_id, "notebook_params": {"data_path": f"https://{storage_account_name}.blob.core.windows.net/{container_name}/raw_data/data.csv"}}
            )

            if databricks_response.status_code == 200:
                logging.info("Successfully triggered Databricks job.")
                
                # Path where predictions will be stored in Blob Storage
                predictions_blob_path = "predictions/predictions_with_results.csv"
                
                return func.HttpResponse(
                    json.dumps({
                        "message": "Data uploaded and Databricks job triggered successfully", 
                        "predictions_blob_path": predictions_blob_path
                    }),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                logging.error(f"Failed to trigger Databricks job: {databricks_response.text}")
                return func.HttpResponse(
                    json.dumps({"error": f"Failed to trigger Databricks job: {databricks_response.text}"}),
                    mimetype="application/json",
                    status_code=500
                )

        except requests.exceptions.RequestException as e:
            return func.HttpResponse(
                json.dumps({"error": f"Failed to fetch data: {str(e)}"}),
                mimetype="application/json",
                status_code=500
            )
    else:
        return func.HttpResponse(
            json.dumps({"error": "Please pass a data_link on the query string or in the request body"}),
            mimetype="application/json",
            status_code=400
        )
