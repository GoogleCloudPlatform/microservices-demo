#!/usr/bin/python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.cloud import secretmanager_v1
from urllib.parse import unquote
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from flask import Flask, request

from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore

PROJECT_ID = os.environ["PROJECT_ID"]
REGION = os.environ["REGION"]
ALLOYDB_DATABASE_NAME = os.environ["ALLOYDB_DATABASE_NAME"]
ALLOYDB_TABLE_NAME = os.environ["ALLOYDB_TABLE_NAME"]
ALLOYDB_CLUSTER_NAME = os.environ["ALLOYDB_CLUSTER_NAME"]
ALLOYDB_INSTANCE_NAME = os.environ["ALLOYDB_INSTANCE_NAME"]
ALLOYDB_SECRET_NAME = os.environ["ALLOYDB_SECRET_NAME"]

secret_manager_client = secretmanager_v1.SecretManagerServiceClient()
secret_name = secret_manager_client.secret_version_path(project=PROJECT_ID, secret=ALLOYDB_SECRET_NAME, secret_version="latest")
secret_request = secretmanager_v1.AccessSecretVersionRequest(name=secret_name)
secret_response = secret_manager_client.access_secret_version(request=secret_request)
PGPASSWORD = secret_response.payload.data.decode("UTF-8").strip()

engine = AlloyDBEngine.from_instance(
    project_id=PROJECT_ID,
    region=REGION,
    cluster=ALLOYDB_CLUSTER_NAME,
    instance=ALLOYDB_INSTANCE_NAME,
    database=ALLOYDB_DATABASE_NAME,
    user="postgres",
    password=PGPASSWORD
)

# Create a synchronous connection to our vectorstore
vectorstore = AlloyDBVectorStore.create_sync(
    engine=engine,
    table_name=ALLOYDB_TABLE_NAME,
    embedding_service=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
    id_column="id",
    content_column="description",
    embedding_column="product_embedding",
    metadata_columns=["id", "name", "categories"]
)

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToGemini():
        print("Beginning RAG call")
        prompt = request.json['message']
        prompt = unquote(prompt)

        # Step 1 – Get a room description from Gemini-vision-pro
        llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "You are a professional interior designer, give me a detailed decsription of the style of the room in this image",
                },
                {"type": "image_url", "image_url": request.json['image']},
            ]
        )
        response = llm_vision.invoke([message])
        print("Description step:")
        print(response)
        description_response = response.content

        # Step 2 – Similarity search with the description & user prompt
        vector_search_prompt = f""" This is the user's request: {prompt} Find the most relevant items for that prompt, while matching style of the room described here: {description_response} """
        print(vector_search_prompt)

        docs = vectorstore.similarity_search(vector_search_prompt)
        print(f"Vector search: {description_response}")
        print(f"Retrieved documents: {len(docs)}")
        #Prepare relevant documents for inclusion in final prompt
        relevant_docs = ""
        for doc in docs:
            doc_details = doc.to_json()
            print(f"Adding relevant document to prompt context: {doc_details}")
            relevant_docs += str(doc_details) + ", "

        # Step 3 – Tie it all together by augmenting our call to Gemini-pro
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        design_prompt = (
            f" You are an interior designer that works for Online Boutique. You are tasked with providing recommendations to a customer on what they should add to a given room from our catalog. This is the description of the room: \n"
            f"{description_response} Here are a list of products that are relevant to it: {relevant_docs} Specifically, this is what the customer has asked for, see if you can accommodate it: {prompt} Start by repeating a brief description of the room's design to the customer, then provide your recommendations. Do your best to pick the most relevant item out of the list of products provided, but if none of them seem relevant, then say that instead of inventing a new product. At the end of the response, add a list of the IDs of the relevant products in the following format for the top 3 results: [<first product ID>], [<second product ID>], [<third product ID>] ")
        print("Final design prompt: ")
        print(design_prompt)
        design_response = llm.invoke(
            design_prompt
        )

        data = {'content': design_response.content}
        return data

    return app

if __name__ == "__main__":
    # Create an instance of flask server when called directly
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
