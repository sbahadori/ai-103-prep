import os
import subprocess
from dotenv import load_dotenv
import glob

from openai import OpenAI

# Import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def main(): 
    # Clear the console
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True, check=False)

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
        )

        client = OpenAI(  
        base_url = azure_openai_endpoint,  
        api_key=token_provider,
        )


        # Create vector store and upload files
        print("Creating vector store and uploading files...")
        vector_store = client.vector_stores.create(name="policy-docs")
        file_streams = [open(file_path, "rb") for file_path in glob.glob("brochures/*.pdf")]
        if not file_streams:
            print("No PDF files found.")
            return
        uploaded_count = 0
        for file_stream in file_streams:
            try:
                client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=file_stream
                )
                uploaded_count += 1
            finally:
                file_stream.close()
        print(f"Vector store created and {uploaded_count} files uploaded successfully.")



        # Track conversation state
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a question (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a question.")
                continue

            # Get a response
            response = client.responses.create(
                        model=model_deployment,
                        instructions=f"You are a travel assistant that provides information on travel services available from Margie's Travel. Answer questions about services offered by Margie's Travel using the provided travel brochures. Search the web for general information about destinations or current travel advice.",
                        input=input_text,
                        previous_response_id=last_response_id,
                        tools=[{
                            "type": "file_search",
                            "vector_store_ids": [vector_store.id]
                        },
                        {
                            "type": "web_search",
                        }
                        ]            
                        )
            assistant_text = response.output_text
            print("\nAssistant:", assistant_text)
            last_response_id = response.id
            



    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
