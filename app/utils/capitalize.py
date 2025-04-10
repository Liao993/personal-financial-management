import streamlit as st

def capitalize_first_letter_of_each_word(text):

  words = text.split()
  capitalized_words = [word[0].upper() + word[1:] for word in words]
  return " ".join(capitalized_words)

