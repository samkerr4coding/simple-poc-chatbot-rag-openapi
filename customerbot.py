import json
import os
from collections.abc import Sequence

import chainlit as cl
import requests
from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.agent_toolkits.openapi import planner
from langchain_community.agent_toolkits.openapi.planner import Operation
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.utilities import RequestsWrapper
from langchain_openai import AzureChatOpenAI

from prompts import assistant_prompt

load_dotenv()

customer_api_docs = None


@cl.on_chat_start
def setup_llm_chain_and_agent():
    # Load and parse the OpenAPI Spec
    openapi_url = 'http://localhost:5000/openapi.json'
    response = requests.get(openapi_url)
    # Ensure the request was successful
    if response.status_code == 200:
        # Parse JSON content
        openapi_data = response.json()

        # Convert Python object to JSON string (for pretty printing)
        openapi_json = json.dumps(openapi_data, indent=2)

        # Optionally, you can save the JSON content to a file
        with open('openapi.json', 'w') as f:
            f.write(openapi_json)

        print("OpenAPI JSON content saved to openapi.json file")
    else:
        print(f"Failed to fetch OpenAPI JSON content. Status code: {response.status_code}")

    llm = AzureChatOpenAI(
        azure_deployment=os.environ.get('AZURE_OPENAI_DEPLOYEMENT_NAME'),  # Replace with your custom LLM URL
        api_version=os.environ.get('AZURE_OPENAI_API_VERSION')
    )

    # llm = ChatOpenAI(
    #     openai_api_key="no token",
    #     model_name="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    #     openai_api_base="http://localhost:1234/v1"  # Replace with your custom LLM URL
    # )

    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                   max_len=200,
                                                   return_messages=True,
                                                   )
    llm_chain = LLMChain(llm=llm, prompt=assistant_prompt, memory=conversation_memory)
    cl.user_session.set("llm_chain", llm_chain)

    with open('openapi.json', 'r') as f:
        spec = json.load(f)
    reduced_spec = reduce_openapi_spec(spec)

    requests_wrapper = RequestsWrapper(headers=None)

    # Create a sequence of allowed operations
    allowed_operations: Sequence[Operation] = ("GET", "POST", "DELETE", "PUT")

    agent = planner.create_openapi_agent(
        api_spec=reduced_spec,
        requests_wrapper=requests_wrapper,
        llm=llm,
        allow_dangerous_requests=True,
        allowed_operations=allowed_operations
    )

    cl.user_session.set("agent", agent)


@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content.lower()
    llm_chain = cl.user_session.get("llm_chain")
    agent = cl.user_session.get("agent")

    if any(keyword in user_message for keyword in ["customer", "customers"]):
        # If any of the keywords are in the user_message, use api_chain
        if any(keyword in user_message for keyword in ["create", "add", "insert",
                                                       "modify", "change", "update",
                                                       "delete", "remove",
                                                       "list"]):
            response = await agent.ainvoke(user_message,
                                           callbacks=[cl.AsyncLangchainCallbackHandler()])
        else:
            # Default to llm_chain for handling general queries
            response = await llm_chain.acall(user_message,
                                             callbacks=[cl.AsyncLangchainCallbackHandler()])
    else:
        # Default to llm_chain for handling general queries
        response = await llm_chain.acall(user_message,
                                         callbacks=[cl.AsyncLangchainCallbackHandler()])

    response_key = "output" if "output" in response else "text"
    await cl.Message(response.get(response_key, "")).send()
