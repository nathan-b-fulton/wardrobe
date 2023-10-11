from neo4j_access import *
from stock_names import stockNames
import streamlit as st
import uuid
import random
import numpy as np


graph = openGraph()
charParts = {'TROPE':False, 'BACKGROUND':False, 'DETAILS':False, 'CLASS':False}


def setName(name=random.choice(stockNames), id=None):
    ""
    if id is None:
        id = str(uuid.uuid4())
    name = st.text_input("Please accept this name for your character, or replace it with a preferred name and hit *enter*.", name, on_change=setName, args=(name, id))
    st.button("Create " + name, on_click=initializeChar, args=(graph,name,id))
    return id


def setComponent(BACKGROUND=None, TROPE=None, COMPETENCE=None, SKILL_FEAT=None, ABILITY=None, DETAILS=None):
    ""
    component = str(uuid.uuid4())
    char = st.session_state['char']
    if BACKGROUND is not None:
        setBGForChar(graph, char, BACKGROUND, component)
        if SKILL_FEAT is not None:
            for s in SKILL_FEAT:
                attachSelection(graph, s, component)
    elif TROPE is not None:
        setTropeForChar(graph, char, TROPE, component)
    elif DETAILS is not None:
        setDetailsForChar(graph, char, component)
    for a in ABILITY:
        attachSelection(graph, a, component)
    if COMPETENCE is not None:
            for c in COMPETENCE:
                attachSelection(graph, c, component)


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
        id = 'f1904c15-e2f1-4be2-ab66-da8b518b21a4'
        if part != 'DETAILS':
            options = getOptions(graph, part)
            smallPart = part.lower()
            choice = st.selectbox("Please select a " + smallPart + " for your character:", options)
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
        selections = {}
        if 'selections' in st.session_state:
            selections = st.session_state['selections']
        selections[part] = id
        df = getChoices(graph, id)
        groups = df.groupby('choice')
        choices = groups.groups.keys()
        for c in choices:
            count = 1
            options = groups.get_group(c)
            choiceType = options.type.unique()[0]
            if selections.get(choiceType) is None:
                selections[choiceType] = {}
            choicesInType = df.loc[df['type'] == choiceType]['choice'].unique()
            if choiceType == 'COMPETENCE':
                for i in options.index:
                    parsed = parseComp(graph, options['id'][i])
                    options.loc[i]['Name'] = parsed
                if part == 'DETAILS':
                    count = 2 + retrieveInt(graph, st.session_state['char'])
                    if 'e74196a1-f693-474c-a5db-4e36ae71274e' in selections['ABILITY']:
                        count+=1
            for x in range(count):
                initial = None
                this_sel = None
                if choiceType in selections and len(selections[choiceType]) > 0:
                    current =  list(selections[choiceType].values())
                    y = len(current) - 1
                    z = y if x > y else x
                    this_sel = current[z]
                    ops = list(options['Name'])
                    if this_sel in ops:
                        initial = ops.index(this_sel)
                s = st.selectbox('Please select one.', options, index=initial, key = c + str(x),placeholder="Select {}".format(choiceType.lower()))
                if s is not None:
                    suuid = options.loc[options['Name'] == s, 'id'].iloc[0]
                    limit = count + len(choicesInType) - 1
                    selections[choiceType][suuid] = s
                    if len(selections[choiceType]) > limit:
                         selections[choiceType].pop(list(selections[choiceType].keys())[0])
                    df = df.drop(df[df['id'] == suuid].index)
                    groups = df.groupby('choice')
                    options = options.drop(options[options['id'] == suuid].index)
        st.session_state['selections'] = selections
        selections
        if part == 'DETAILS':
            st.button("Confirm these selections for {}".format(st.session_state['char']), on_click=setComponent, kwargs=selections)
        else:
            st.button("Confirm {} as the {} for {}".format(choice, smallPart, st.session_state['char']), on_click=setComponent, kwargs=selections)
else:
    st.markdown(" ## Please select or create a character.")

    


graph.close()