from neo4j_access import openGraph, getOptions, initializeChar, retrieveChar
from stock_names import stockNames
import streamlit as st
import uuid
import random


graph = openGraph()
charParts = {'TROPE':False, 'BACKGROUND':False, 'DETAILS':False, 'CLASS':False}


def setName(name=random.choice(stockNames), id=None):
    ""
    if id is None:
        id = str(uuid.uuid4())
    name = st.text_input("Please accept this name for your character, or replace it with a preferred name and hit *enter*.", name, on_change=setName, args=(name, id))
    st.button("Create " + name, on_click=initializeChar, args=(graph,name,id))
    return id


with st.sidebar:
    chars = getOptions(graph, "CHARACTER")
    if chars is not None:
        st.session_state['current'] = st.selectbox("Please select a character:", chars)
        "or"
    initialize = st.button("Create new character")
    if 'current' in st.session_state:
        char = retrieveChar(graph, st.session_state['current'])
        char
        for part in charParts:
            emoji = ':x:'
            action = 'Set '
            bType = 'primary'
            if part in char['facet'].values:
                emoji = ':heavy_check_mark:'
                action = 'Edit '
                bType = 'secondary'
            cased = part.title()
            st.markdown(' ### ' + emoji + ' ' + cased)
            charParts[part] = st.button(action + cased, type=bType)
            


if initialize:
    st.session_state['current'] = setName()
elif 'current' in st.session_state:
    for part in charParts:
        if charParts[part] is True:
            options = getOptions(graph, part)
            choice = st.selectbox("Please select a " + part.lower() + " for your character:", options)
            details = options.loc[options['Name'] == choice]
            cols = options.columns.tolist()
            cols.remove('UUID')
            for col in cols:
                st.write("*"+col+"*: ", str(details[col].iloc[0]))
            break
else:
    st.markdown(" ## Please select or create a character.")

    


graph.close()