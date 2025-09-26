# pip install mysql-connector-python
# pip install pandas

import mysql.connector
import pandas as pd

def conexao(query):

    con = mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="Senai@134",
        db="db_sensor"
    )

    df = pd.read_sql(query, con)
    # Executar o SQL e armazenar o resultado no dataframe

    con.close()
    return df