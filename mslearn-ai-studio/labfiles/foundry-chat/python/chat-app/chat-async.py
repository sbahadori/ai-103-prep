import os
import subprocess
from dotenv import load_dotenv

# import namespaces for async
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
import asyncio
from openai import AsyncOpenAI



async def main(): 

    # Clear the console
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True, check=False)

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
        credential, "https://ai.azure.com/.default"
        )

        async_client = AsyncOpenAI(  
        base_url = azure_openai_endpoint,  
        api_key=token_provider,
        )

       

        # Track responses
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Await an asynchronous response
            response = await async_client.responses.create(
                instructions="You are a helpful AI assistant that explains technology concepts clearly.",
                model=model_deployment,
                input=input_text,
                previous_response_id=last_response_id
            )
            print(response.output_text)

          

    except Exception as ex:
        print(ex)

    finally:
        # Close the async client session
        await async_client.close()
        await credential.close()

if __name__ == '__main__': 
    asyncio.run(main())
