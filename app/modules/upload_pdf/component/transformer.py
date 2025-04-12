import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Load the Sentence Transformer model (you might want to do this once at the start)
@st.cache_resource
def load_transformer():
    return SentenceTransformer("all-MiniLM-L6-v2")

def categorize_description(description, model, category_options):
    description_embedding = model.encode(description)
    category_embeddings = model.encode(category_options)

    similarity_scores = cosine_similarity([description_embedding], category_embeddings)[0]
    best_category_index = np.argmax(similarity_scores)
    return category_options[best_category_index]
