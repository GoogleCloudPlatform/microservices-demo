#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from urllib.parse import unquote
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from flask import Flask, request
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore

engine = AlloyDBEngine.from_instance(
    project_id="cooking-with-duet-6",
    region="us-central1",
    cluster="onlineboutique-cluster",
    instance="onlineboutique-instance",
    database="products",
    user="postgres",
    password="admin"
)
vectorstore = AlloyDBVectorStore.create_sync(
    engine=engine,
    table_name="catalog_items",
    embedding_service=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
    id_column="id",
    content_column="description",
    embedding_column="product_embedding"
)


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToGemini():
        prompt = request.json['message']
        prompt = unquote(prompt)

        #Decsription prompt:
        #Send in the image, ask for a description of the room, search for relevant products
        llm_vision = ChatGoogleGenerativeAI(model="gemini-pro-vision")
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
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

        docs = vectorstore.similarity_search(description_response)
        print(f"Vector search:: {description_response}")
        print(f"Retrieved documents: {len(docs)}")
        relevant_docs = ""
        for doc in docs:
            doc_details = doc.to_json()
            print(f"Adding document to prompt context: {doc_details}")
            relevant_docs += doc.page_content + ", "

        design_response = llm.invoke(
            f"""
            You are an interior designer that works for Online Boutique. You are
             tasked with providing recommendations to a customer on what they
             should add to a given room from our catalog.

            This is the description of the room: {description_response}
            Here are a list of products that are relevant to it: {relevant_docs}

            Specifically, this is what the customer has asked for, see if you
            can accommodate it: {prompt}

            Start by repeating a brief description of the room's design to the
            customer, then provide your recommendations.
            Do your best to pick the most relevant item out of the list of
            products provided, but if none of them seem relevant, then say that
            instead of inventing a new product.

            If you are aware of any links to the product pages, please include
            those in the response.
            """
        )

        data = {}
        data['content'] = design_response.content
        return data

    return app


if __name__ == "__main__":
    # Create an instance of flask server when called directly
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
