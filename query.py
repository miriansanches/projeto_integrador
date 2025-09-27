# pip install mysql-connector-python
# pip install pandas

import mysql.connector
import pandas as pd

def conexao(query):

    con = mysql.connector.connect(
        host="projetointegrador-grupo2.mysql.database.azure.com",
        port="3306",
        user="projeto2",
        password="senai%40134",
        db="db_sensor"

    )

    df = pd.read_sql(query, con)
    # Executar o SQL e armazenar o resultado no dataframe

    con.close()
    return df
