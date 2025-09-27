import mysql.connector
import pandas as pd
import streamlit as st

def conexao(query):
    try:
        con = mysql.connector.connect(
            host="projetointegrador-grupo2.mysql.database.azure.com",
            port="3306",
            user="projeto2",
            password="senai%40134",
            database="db_sensor",
            ssl_ca="DigiCertGlobalRootG2.crt.pem"  # Caminho para o certificado
        )
        df = pd.read_sql(query, con)
        con.close()
        return df
    except Exception as e:
        st.error(f"Erro na conexão com o banco: {e}")
        return pd.DataFrame()
