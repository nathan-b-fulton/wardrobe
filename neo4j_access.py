from neo4j import GraphDatabase, Driver, Result
import streamlit as st
import pandas as pd


def openGraph() -> Driver:
    ""
    s = st.secrets
    driver = GraphDatabase.driver(s["NEO4J_URI"], auth=(s["NEO4J_USER"], s["NEO4J_PASSWORD"]))
    return driver


def neo4jTest():
    ""
    graph = openGraph()
    res = graph.execute_query(
        "MATCH (n) RETURN n.Name AS text LIMIT 1"
    )
    graph.close()
    print(res)

@st.cache_data
def getOptions(_graph:Driver, label:str):
    ""
    options = None
    q = "MATCH (n:" + label + ") RETURN n"
    records = _graph.execute_query(
        q,
        database_="neo4j"
    ).records
    if records:
        o = []
        for record in records:
            rDict = record.data()
            o.append(rDict["n"])
        options = pd.DataFrame.from_dict(o)
        nList = options.columns.tolist()
        nList.remove("Name")
        cols = ["Name"] + nList
        options = options[cols]
    return options


@st.cache_data
def getChoices(_graph:Driver, id:str):
    ""
    q = "MATCH ({ UUID:$id })-[:PROVIDES_CHOICE]->(c:CHOICE)-[:HAS_OPTION]->(o) RETURN o.Name AS Name, o.UUID AS id, labels(o)[0] AS type, c.UUID AS choice"
    df = _graph.execute_query(
        q,
        id=id,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df


@st.cache_data
def getIncreases(_graph:Driver, id:str):
    ""
    q = "MATCH ({ UUID:$id })-[:INCREASES]->(a:ABILITY) RETURN a.Name AS Name, a.UUID AS id"
    df = _graph.execute_query(
        q,
        id=id,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df


@st.cache_data
def getDecreases(_graph:Driver, id:str):
    ""
    q = "MATCH ({ UUID:$id })-[:DECREASES]->(a:ABILITY) RETURN a.Name AS Name, a.UUID AS id"
    df = _graph.execute_query(
        q,
        id=id,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df


@st.cache_data
def getCompetencies(_graph:Driver, id:str):
    ""
    q = "MATCH ({ UUID:$id })-[:PROVIDES_COMPETENCE]->(c:COMPETENCE) RETURN c.UUID AS id"
    df = _graph.execute_query(
        q,
        id=id,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df


@st.cache_data
def parseComp(_graph:Driver, id:str):
    ""
    q = "MATCH (t)<-[:TOPIC]-(:COMPETENCE { UUID:$id })-[:LEVEL]->(l:PROFICIENCY) RETURN l.Name + ' in ' + t.Name AS parsed"
    comp = _graph.execute_query(
        q,
        id=id,
        database_="neo4j"
    ).records
    final = "OH NO: {} does not seem to be a valid competence specification.".format(id)
    if len(comp) > 0:
        d = comp[0].data()
        final = d["parsed"]
    return final


def initializeChar(_graph:Driver, name:str, id:str):
    ""
    q = """
    CREATE (c:CHARACTER { UUID:$id })
    SET c.Name = $name
    """
    summary = _graph.execute_query(
        q,
        id=id,
        name=name,
        database_="neo4j"
    ).summary
    return summary.counters.nodes_created


def retrieveChar(graph:Driver, char:str):
    ""
    q = """
    MATCH (:CHARACTER { Name:$char })-[:HAS]->(c:COMPONENT)-[r]->(s)
    RETURN c.UUID AS component, TYPE(r) AS facet, s.UUID AS focus
    """
    df = graph.execute_query(
        q,
        char=char,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df


def retrieveInt(graph:Driver, char:str):
    ""
    q = """
    MATCH (:CHARACTER { Name:$char })-[:HAS]->(c:COMPONENT)-[*1..2]->(:ABILITY {UUID: 'e74196a1-f693-474c-a5db-4e36ae71274e'}) 
    WHERE NOT (c)-[:DETAILS]->(:DETAILS)
    RETURN COUNT(c) AS boosts
    """
    boosts = graph.execute_query(
        q,
        char=char,
        database_="neo4j"
    ).records
    final = "OH NO: {} does not seem to be a valid competence specification.".format(id)
    if len(boosts) > 0:
        d = boosts[0].data()
        final = d["boosts"]
    else: final = 0
    return final


def setBGForChar(graph:Driver, char:str, bg:str, comp:str):
    ""
    q = """
    MERGE (co:COMPONENT { UUID:$comp })
    WITH co
    MATCH (ch:CHARACTER { Name:$char })
    MATCH (b:BACKGROUND { UUID:$bg })
    CREATE (ch)-[:HAS]->(co)-[:BACKGROUND]->(b)
    RETURN co.UUID AS component
    """
    co = graph.execute_query(
        q,
        char=char,
        bg=bg,
        comp=comp,
        database_="neo4j"
    ).records
    d = co[0].data()
    final = d["component"]
    return final


def setTropeForChar(graph:Driver, char:str, tr:str, comp:str):
    ""
    q = """
    MERGE (co:COMPONENT { UUID:$comp })
    WITH co
    MATCH (ch:CHARACTER { Name:$char })
    MATCH (t:TROPE { UUID:$tr })
    CREATE (ch)-[:HAS]->(co)-[:TROPE]->(t)
    RETURN co.UUID AS component
    """
    co = graph.execute_query(
        q,
        char=char,
        tr=tr,
        comp=comp,
        database_="neo4j"
    ).records
    d = co[0].data()
    final = d["component"]
    return final


def attachSelection(graph:Driver, sel:str, comp:str):
    ""
    q = """
    MATCH (c:COMPONENT { UUID:$comp })
    MATCH (s { UUID:$sel })
    CREATE (c)-[:SELECTED]->(s)
    """
    s = graph.execute_query(
        q,
        sel=sel,
        comp=comp,
        database_="neo4j"
    ).summary
    return s.counters.relationships_created


# neo4jTest()
