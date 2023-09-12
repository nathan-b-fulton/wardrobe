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
    records, summary, keys = _graph.execute_query(
        q,
        database_="neo4j"
    )
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


def initializeChar(graph:Driver, name:str, id:str):
    ""
    q = """
    CREATE (c:CHARACTER { UUID:$id })
    SET c.Name = $name
    """
    summary = graph.execute_query(
        q,
        id=id,
        name=name,
        database_="neo4j"
    ).summary
    return summary.counters.nodes_created


def retrieveChar(graph:Driver, id:str):
    ""
    q = """
    MATCH (:CHARACTER { UUID:$id })-[r]->(s)
    RETURN TYPE(r) AS facet, s.UUID AS focus
    """
    df = graph.execute_query(
        q,
        id=id,
        database_="neo4j",
        result_transformer_=Result.to_df
    )
    return df

# neo4jTest()
