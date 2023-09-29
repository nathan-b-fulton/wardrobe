from neo4j_access import openGraph, getOptions, initializeChar, retrieveChar, getChoices, getIncreases, getDecreases, getCompetencies, parseComp
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
        st.session_state['char'] = st.selectbox("Please select a character:", chars)
        "or"
    initialize = st.button("Create new character")
    if 'char' in st.session_state:
        char = retrieveChar(graph, st.session_state['char'])
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
    st.session_state['char'] = setName()
elif 'char' in st.session_state:
    for part in charParts:
        if charParts[part] is True:
            st.session_state['part'] = part
    if 'part' in st.session_state:
        part = st.session_state['part']
        options = getOptions(graph, part)
        choice = st.selectbox("Please select a " + part.lower() + " for your character:", options)
        details = options.loc[options['Name'] == choice]
        cols = options.columns.tolist()
        cols.remove('UUID')
        for col in cols:
            st.write("*"+col+"*: ", str(details[col].iloc[0]))
        id = details['UUID'].iloc[0]
        inc = getIncreases(graph, id)
        if not inc.empty:
            incs = ""
            for i in inc.index:
                incs = incs + inc['Name'][i] + ', '
            incs = incs.rstrip(', ')
            st.write("Increases: ", incs)
        dec = getDecreases(graph, id)
        if not dec.empty:
            st.write("Decreases: ", dec['Name'][0])
        comp = getCompetencies(graph, id)
        if not comp.empty:
            comps = ""
            for i in comp.index:
                parsed = parseComp(graph, comp['id'][i])
                comps = comps + parsed + ', '
            comps = comps.rstrip(', ')
            st.write(comps)
        df = getChoices(graph, id)
        groups = df.groupby('choice')
        choices = df.choice.unique()
        selections = {}
        for c in choices:
            options = groups.get_group(c)
            type = options.type.unique()[0]
            if type == 'COMPETENCE':
                for i in options.index:
                    parsed = parseComp(graph, options['id'][i])
                    options['Name'][i] = parsed
            prev = selections.get(type)
            if prev is None:
                selections[type] = []
            else:
                options.drop(options[options['Name'] == prev[0]].index)
            s = st.selectbox('Please select one.', options)
            selections[type].append(s)
else:
    st.markdown(" ## Please select or create a character.")

    


graph.close()