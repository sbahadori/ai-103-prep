import subprocess
import os
from dotenv import load_dotenv

# import namespaces
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

        openai_client = OpenAI(  
        base_url = azure_openai_endpoint,  
        api_key=token_provider,
        )

        # Initial messages
        conversation_messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant that answers questions and provides information."
            }
        ]

        # Loop until the user wants to quit
        print("Assistant: Enter a prompt (or type 'quit' to exit)")
        while True:
            input_text = input('\nYou: ')
            if input_text.lower() == "quit":
                print("Assistant: Goodbye!")
                break

            # Add the user message
            conversation_messages.append(
                {"role": "user",
                "content": input_text}
            )

            # Get a completion
            completion = openai_client.chat.completions.create(
                model=model_deployment,
                messages=conversation_messages
            )
            assistant_message = completion.choices[0].message.content
            print("\nAssistant:", assistant_message)

            # Append the response to the conversation
            conversation_messages.append(
                {"role": "assistant", "content": assistant_message}
            )

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
