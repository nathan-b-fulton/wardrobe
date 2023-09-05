from neo4j import GraphDatabase, Driver
import streamlit as st


def openGraph() -> Driver:
    ""
    s = st.secrets
    driver = GraphDatabase.driver(s["NEO4J_URI"], auth=(s["NEO4J_USER"], s["NEO4J_PASSWORD"]))
    return driver

def neo4jTest():
    ""
    graph = openGraph()
    res = graph.execute_query(
        "MATCH (n) RETURN n.textField AS text LIMIT 1"
    )
    graph.close()
    print(res)

neo4jTest()