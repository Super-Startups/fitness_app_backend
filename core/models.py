from zipfile import ZipFile

import PyPDF2
from django.core.files.base import ContentFile
from django.db import models

import os

import pickle
import re
import faiss
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.embeddings import OpenAIEmbeddings
import ai_utility.constants as constants

EMBEDDINGS_MODEL = "text-embedding-3-small"

INDEXES_PATH = 'uploads/indexes'
METADATA_PATH = 'uploads/metadata'
MATERIALS_PATH = 'uploads/materials'


class Trainer(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    uploaded_materials = models.FileField(upload_to=MATERIALS_PATH)
    faiss_index_3_small = models.FileField(upload_to=INDEXES_PATH, null=True, blank=True)
    faiss_meta_3_small = models.FileField(upload_to=METADATA_PATH, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Trainer, self).save(*args, **kwargs)

        index_file_name, metadata_file_name = create_index_files(self)

        with open(f'{INDEXES_PATH}/{index_file_name}', 'rb') as f:
            self.faiss_index_3_small.save(index_file_name, ContentFile(f.read()), save=False)

        with open(f'{METADATA_PATH}/{metadata_file_name}', 'rb') as f:
            self.faiss_meta_3_small.save(metadata_file_name, ContentFile(f.read()), save=False)

        super(Trainer, self).save(*args, **kwargs)
        print('Index created')


def create_index_files(trainer):
    with ZipFile(trainer.uploaded_materials.path) as zip_file:
        texts = accumulate_texts(zip_file)

    index = create_index(texts, EMBEDDINGS_MODEL)

    index_file_name = f'{trainer.id}_{EMBEDDINGS_MODEL}_index.faiss'
    metadata_file_name = f'{trainer.id}_{EMBEDDINGS_MODEL}_metadata.pkl'

    index_path = f'{INDEXES_PATH}/{index_file_name}'
    metadata_path = f'{METADATA_PATH}/{metadata_file_name}'

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    save_index(index, index_path, metadata_path)

    return index_file_name, metadata_file_name


def save_index(index, index_path, metadata_path):
    faiss.write_index(index.index, index_path)
    with open(metadata_path, 'wb+') as f:
        pickle.dump((index.docstore, index.index_to_docstore_id), f)


def create_index(data, model):
    chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=2048, chunk_overlap=1)

    for chunk in splitter.split_text(data):
        chunks.append(Document(page_content=chunk, metadata={}))

    embedding = OpenAIEmbeddings(model=model, api_key=constants.OPEN_AI_API_KEY)

    return FAISS.from_documents(chunks, embedding)


def accumulate_texts(zip_file):
    texts = "\n\n"
    for name in zip_file.namelist():
        with zip_file.open(name) as file:
            if file.name.endswith('.pdf'):
                text = convert_pdf_to_text(file)
                texts = texts + "\n" + text
            else:
                texts = texts + "\n" + file.read().decode('utf-8')
    return texts


def convert_pdf_to_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text
