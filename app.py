import streamlit as st
import requests
import pandas as pd
from azure.storage.blob import BlobServiceClient
import io

# Set custom page configuration
st.set_page_config(
    page_title="Anti-Money Laundering System",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a dark-themed UI
st.markdown("""
    <style>
        /* Dark background and font styles */
        .stApp {
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: 'Helvetica Neue', sans-serif;
        }
        /* Main container */
        .css-1n4v1x0 {
            background-color: #34495e;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            margin: auto;
        }
        /* Title styles */
        h1 {
            color: #ecf0f1;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: bold;
        }
        /* Subtitle styles */
        h3 {
            color: #bdc3c7;
            font-size: 1.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        /* Input box */
        .stTextInput>div>div>input {
            border: 2px solid #1abc9c;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1.2rem;
            color: #ecf0f1;
            background-color: #2c3e50;
        }
        /* Button styles */
        .stButton button {
            background-color: #1abc9c;
            color: white;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 1.2rem;
            font-weight: bold;
            border: none;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            margin-top: 2rem;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .stButton button:hover {
            background-color: #16a085;
            transform: translateY(-3px);
        }
        /* Adjust text input and button alignment */
        .css-1lcbmhc {
            justify-content: center;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app title with emoji
st.title("💸 Anti-Money Laundering System")

# Input for data link with subtitle
st.markdown("### Upload Your Data for Prediction")
data_link = st.text_input("Enter the link to your data:")

if data_link:
    # Predict button with added styling
    if st.button("Predict"):
        with st.spinner("Processing your request..."):
            # Define the URL of the Azure Function
            function_url = "https://app-aml-pro.azurewebsites.net/api/http_trigger?code=ZvVg90BwsJ3kcs0urNl27ZwcXqRGyjZQs33WdosKemrPAzFu5aF8vA%3D%3D"

            # Send POST request to Azure Function
            response = requests.post(function_url, json={"data_link": data_link})

            # Check the response
            if response.status_code == 200:
                result = response.json()
                #st.success("Data uploaded and job triggered successfully!")

                # Extract predictions file path from response
                predictions_blob_path = result.get("predictions_blob_path")

                if predictions_blob_path:
                    # Fetch the predictions file
                    container_name = "amldata"
                    connection_string = "DefaultEndpointsProtocol=https;AccountName=amldatacnak;AccountKey=OD7x5wWUM2IoaFIUIVW1Sq8hI6HzKhnA7Rr4nI+9/OH0jElAD+eksiEoIsIyhjmSlgoynvE5cUwa+AStSBrKkQ==;EndpointSuffix=core.windows.net"

                    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=predictions_blob_path)

                    # Download the predictions file
                    download_stream = blob_client.download_blob()
                    predictions_file = io.BytesIO(download_stream.readall())

                    # Load the predictions file into a DataFrame
                    predictions_df = pd.read_csv(predictions_file)

                    # Show download link
                    st.download_button(
                        label="Download Predictions File",
                        data=predictions_file.getvalue(),
                        file_name="predictions_with_results.csv",
                        mime="text/csv"
                    )

                    # Display prediction statistics
                    st.markdown("### Prediction Statistics")
                    if 'predictions' in predictions_df.columns:
                        num_laundering = predictions_df['predictions'].sum()
                        num_not_laundering = len(predictions_df) - num_laundering
                        st.write(f"Laundering (1): {num_laundering}")
                        st.write(f"Not Laundering (0): {num_not_laundering}")
                    else:
                        st.write("No prediction column found.")
                else:
                    st.write("Failed to retrieve the predictions file path.")
            else:
                st.write("Failed to upload data:")
                st.write(response.text)




##### final code of streamlit