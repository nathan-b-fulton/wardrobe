from neo4j_access import openGraph, getOptions, initializeChar
from stock_names import stockNames
import streamlit as st
import uuid
import random


graph = openGraph()


def setName(name=random.choice(stockNames), id=None):
    ""
    if id is None:
        id = str(uuid.uuid4())
    name = st.text_input("Please accept this name for your character, or replace it with a preferred name and hit *enter*.", name, on_change=setName, args=(name, id))
    st.button("Create " + name, on_click=initializeChar, args=(graph,name,id))
    return id


with st.sidebar:
    initialize = st.button("Create new character")

if initialize:
    st.session_state['current'] = setName()
elif 'current' not in st.session_state:
    st.markdown(" ## Please select or create a character.")
else:
    options = getOptions(graph, "TROPE")
    trope = st.selectbox("Please select a trope for your character:", options)
    details = options.loc[options['Name'] == trope]
    cols = options.columns.tolist()
    cols.remove('UUID')
    for col in cols:
        st.write("*"+col+"*: ", str(details[col].iloc[0]))


graph.close()