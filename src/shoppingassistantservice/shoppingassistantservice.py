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
from langchain_google_genai import ChatGoogleGenerativeAI
from flask import Flask, jsonify, request
from langchain_community.retrievers import (
    GoogleVertexAIMultiTurnSearchRetriever,
    GoogleVertexAISearchRetriever,
)
from langchain.vectorstores.pgvector import PGVector
from langchain.prompts import PromptTemplate


#Establish connection
CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get("PGVECTOR_HOST", "localhost"),
    port=int(os.environ.get("PGVECTOR_PORT", "5432")),
    database=os.environ.get("PGVECTOR_DATABASE", "onlineboutique-instance"),
    user=os.environ.get("PGVECTOR_USER", "postgres"),
    password=os.environ.get("PGVECTOR_PASSWORD", "admin"),
)
db = PGVector(
    collection_name="catalog_items",
    connection_string=CONNECTION_STRING,
)

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToGemini():
        prompt = request.json['message']
        prompt = unquote(prompt)

        if request.json.get('image') is None:
            #Prepare the prompt template:
            prompt_template = """ You are a customer assistant for an online store called Online Boutique. You are here to help our customers find the most relevant products to their questions. Try to provide links to the products when you are sure. If you do not know what to say, please say that clearly to t he customer instead of making something up.

                    {context}

                    Question: {question}
                    Answer:"""
            augmented_prompt = PromptTemplate(
                template=prompt_template, input_variables=["context", "question"]
            )

            chain_type_kwargs = {"prompt": augmented_prompt}

            #llm = ChatGoogleGenerativeAI(model="gemini-pro")
            retriever = db.as_retriever()

            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs=chain_type_kwargs,
                verbose=True
            )

            response = qa.run(prompt)
        else:
            llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {"type": "image_url", "image_url": request.json['image']},
                ]
            )
            response = llm.invoke([message])

        data = {}
        data['content'] = response.content
        return data

    return app


if __name__ == "__main__":
    # Create an instance of flask server when called directly
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
