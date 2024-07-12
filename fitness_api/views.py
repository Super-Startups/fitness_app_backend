from django.http import JsonResponse
import jsonpickle
from langchain.vectorstores import faiss
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
from ai_utility import constants
import core.models as models

import pickle
import re

import faiss

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.embeddings import OpenAIEmbeddings


def get_material(request):
    request = jsonpickle.decode(request.body)

    question = request['question']

    coach = models.Trainer.objects.get(pk=request['coach_id'])
    index = load_faiss_index(coach.faiss_index_3_small.path, coach.faiss_meta_3_small.path, models.EMBEDDINGS_MODEL)
    content = get_message_content(question, index, 1)

    answer = content
    response = GetMaterialResponse(answer)
    json_response = response.__dict__

    return JsonResponse(json_response)


def ask_question(request):
    request = jsonpickle.decode(request.body)

    messages = request['messages']

    answer = ask_gpt_with_context(messages, constants.OPEN_AI_API_KEY)
    response = AskQuestionResponse(answer)
    json_response = response.__dict__

    return JsonResponse(json_response)


class GetMaterialResponse:

    def __init__(self, material):
        self.material = material


class AskQuestionResponse:

    def __init__(self, message):
        self.message = message


def ask_gpt_with_context(messages, api_key):
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    answer = completion.choices[0].message.content

    return answer


def load_faiss_index(index_path, metadata_path, embedding_model):
    embedding_function = OpenAIEmbeddings(model=embedding_model, api_key=constants.OPEN_AI_API_KEY)
    index = faiss.read_index(index_path)
    with open(metadata_path, 'rb') as f:
        docstore, index_to_docstore_id = pickle.load(f)
    return FAISS(embedding_function, index, docstore, index_to_docstore_id)


def get_message_content(topic, index, k_num):
    docs = index.similarity_search(topic, k=k_num)
    message_content = re.sub(r'\n{2}', ' ', '\n '.join(
        [f'\n#### Document excerpt №{i + 1}####\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    return message_content
