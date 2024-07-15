import io
import json

import chainlit as cl
import requests
import yaml
from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.agent_toolkits.openapi import planner
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
from langchain_openai import AzureChatOpenAI

from prompts import assistant_prompt

load_dotenv()

customer_api_docs = None


@cl.on_chat_start
def setup_multiple_chains():
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

    with open('openapi.json', 'r') as f:
        spec = json.load(f)
    reduced_spec = reduce_openapi_spec(spec)

    llm = AzureChatOpenAI(
        azure_deployment="<YOUR AZURE DEPLOYEMENT NAME>",  # Replace with your custom LLM URL
        api_version="<YOUR API VERSION>"
    )

    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                   max_len=200,
                                                   return_messages=True,
                                                   )
    llm_chain = LLMChain(llm=llm, prompt=assistant_prompt, memory=conversation_memory)
    cl.user_session.set("llm_chain", llm_chain)

    requests_wrapper = RequestsWrapper(headers=None)
    agent = planner.create_openapi_agent(
        reduced_spec,
        requests_wrapper,
        llm,
        allow_dangerous_requests=True,
    )

    cl.user_session.set("agent", agent)


@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content.lower()
    llm_chain = cl.user_session.get("llm_chain")
    agent = cl.user_session.get("agent")

    if any(keyword in user_message for keyword in ["customer", "customers"]):
        # If any of the keywords are in the user_message, use api_chain
        response = await agent.ainvoke(user_message,
                                         callbacks=[cl.AsyncLangchainCallbackHandler()])
    else:
        # Default to llm_chain for handling general queries
        response = await llm_chain.acall(user_message,
                                         callbacks=[cl.AsyncLangchainCallbackHandler()])

    response_key = "output" if "output" in response else "text"
    await cl.Message(response.get(response_key, "")).send()
