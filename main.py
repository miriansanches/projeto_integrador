# pip install flask_sqlalchemy

from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

app = Flask('sensor')

# Configuração do banco
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SQLALCHEMY_ECHO'] = True


server_name = 'projetointegrador-grupo2.mysql.database.azure.com'
port='3306'
username='projeto2'
password='senai%40134'
database='db_sensor'
certificado='DigiCertGlobalRootG2.crt.pem'

uri = f"mysql://{username}:{password}@{server_name}:{port}/{database}"
ssl_certificado = f"?ssl_ca={certificado}"

app.config['SQLALCHEMY_DATABASE_URI'] = uri + ssl_certificado

mydb = SQLAlchemy(app)


mqtt_data = {}


def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(rc))
    client.subscribe("projeto_integrado/SENAI134/Cienciadedados/grupo1")

def on_message(client, userdata, msg):
    global mqtt_data
    payload = msg.payload.decode('utf-8')
    mqtt_data = json.loads(payload)
   
    print(f"Received message: {mqtt_data}")


# Adiciona o contexto da aplicação para a manipulação do banco de dados
    with app.app_context():
        try:
            temperatura = mqtt_data.get('temperature')
            pressao = mqtt_data.get('pressure')
            altitude = mqtt_data.get('altitude')
            umidade = mqtt_data.get('humidity')
            co2 = mqtt_data.get('CO2')
            poeira1 = mqtt_data.get('particula1')
            poeira2 = mqtt_data.get('particula2')
            timestamp_unix = mqtt_data.get('timestamp')
            id_cidade = 1

            if timestamp_unix is None:
                print("Timestamp não encontrado no payload")
                return

            # Converte timestamp Unix para datetime
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_unix), tz=timezone.utc)
            except (ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return

            # Cria o objeto Registro com os dados
            new_data = CondicaoAmbiental(
                temperatura=temperatura,
                pressao=pressao,
                altitude=altitude,
                umidade=umidade,
                poeira1=poeira1,
                poeira2=poeira2,
                co2=co2,
                data_hora=timestamp,
                id_cidade=id_cidade
            )

            # Adiciona o novo registro ao banco de dados
            mydb.session.add(new_data)
            mydb.session.commit()
            print("Dados inseridos no banco de dados com sucesso")

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mydb.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()

# ***********************************************************************************************************************************************
# Cadastrar
@app.route('/data', methods=['POST'])
def post_data():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido"}), 400

        # Adiciona logs para depuração
        print(f"Dados recebidos: {data}")

        temperatura = data.get('temperatura')
        pressao = data.get('pressao')
        altitude = data.get('altitude')
        umidade = data.get('umidade')
        co2 = data.get('CO2')
        timestamp_unix = data.get('data_hora')
        id_cidade = data.get('id_cidade')

        # Converte timestamp Unix para datetime
        try:
            timestamp = datetime.fromtimestamp(int(timestamp_unix), tz=timezone.utc)
        except ValueError as e:
            print(f"Erro no timestamp: {str(e)}")
            return jsonify({"error": "Timestamp inválido"}), 400

        # Cria o objeto Registro com os dados
        new_data = CondicaoAmbiental(
            temperatura=temperatura,
            pressao=pressao,
            altitude=altitude,
            umidade=umidade,
            co2=co2,
            poeira1 = mqtt_data.get('particula1'),
            poeira2 = mqtt_data.get('particula2'),
            data_hora=timestamp,
            id_cidade=id_cidade
        )

        # Adiciona o novo registro ao banco de dados
        mydb.session.add(new_data)
        print("Adicionando o novo registro")

        # Tenta confirmar a transação
        mydb.session.commit()
        print("Dados inseridos no banco de dados com sucesso")

        return jsonify({"message": "Data received successfully"}), 201

    except Exception as e:
        print(f"Erro ao processar a solicitação: {str(e)}")
        mydb.session.rollback()  # Reverte qualquer alteração em caso de erro
        return jsonify({"error": "Falha ao processar os dados"}), 500

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(mqtt_data)

# ------------------------------
# MODELOS
# ------------------------------

class Cidade(mydb.Model):
    __tablename__ = 'tb_cidade'
    id_cidade = mydb.Column(mydb.Integer, primary_key=True)
    nome = mydb.Column(mydb.String(100))
    estado = mydb.Column(mydb.String(2))
    bairro = mydb.Column(mydb.String(100))
    latitude = mydb.Column(mydb.DECIMAL)
    longitude = mydb.Column(mydb.DECIMAL)

    def to_json(self):
        return {
            "id_cidade": self.id_cidade,
            "nome": self.nome,
            "estado": self.estado,
            "bairro": self.bairro,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude)
        }

class Demografia(mydb.Model):
    __tablename__ = 'tb_demografia'
    id_demografia = mydb.Column(mydb.Integer, primary_key=True)
    id_cidade = mydb.Column(mydb.Integer, mydb.ForeignKey('tb_cidade.id_cidade'))
    ano_medicao = mydb.Column(mydb.Integer)
    populacao_total = mydb.Column(mydb.DECIMAL)
    area_km2 = mydb.Column(mydb.DECIMAL)
    densidade_populacional = mydb.Column(mydb.DECIMAL)
    urbanizacao_pct = mydb.Column(mydb.DECIMAL)

    def to_json(self):
        return {
            "id_demografia": self.id_demografia,
            "id_cidade": self.id_cidade,
            "ano_medicao": self.ano_medicao,
            "populacao_total": float(self.populacao_total),
            "area_km2": float(self.area_km2),
            "densidade_populacional": float(self.densidade_populacional),
            "urbanizacao_pct": float(self.urbanizacao_pct)
        }

class CondicaoAmbiental(mydb.Model):
    __tablename__ = 'tb_condicao_ambiental'
    id_condicao = mydb.Column(mydb.Integer, primary_key=True)
    id_cidade = mydb.Column(mydb.Integer, mydb.ForeignKey('tb_cidade.id_cidade'))
    data_hora = mydb.Column(mydb.DateTime)
    temperatura = mydb.Column(mydb.DECIMAL)
    umidade = mydb.Column(mydb.DECIMAL)
    pressao = mydb.Column(mydb.DECIMAL)
    co2 = mydb.Column(mydb.DECIMAL)
    poeira1 = mydb.Column(mydb.DECIMAL)
    poeira2 = mydb.Column(mydb.DECIMAL)
    altitude = mydb.Column(mydb.DECIMAL)

    def to_json(self):
        return {
            "id_condicao": self.id_condicao,
            "id_cidade": self.id_cidade,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
            "temperatura": float(self.temperatura),
            "umidade": float(self.umidade),
            "pressao": float(self.pressao),
            "co2": float(self.co2),
            "poeira1": float(self.poeira1),
            "poeira2": float(self.poeira2),
            "altitude": float(self.altitude)
        }

class Densidade(mydb.Model):
    __tablename__ = 'tb_densidade'
    id_densidade = mydb.Column(mydb.Integer, primary_key=True)
    id_condicao = mydb.Column(mydb.Integer, mydb.ForeignKey('tb_condicao_ambiental.id_condicao'))
    densidade = mydb.Column(mydb.DECIMAL)

    def to_json(self):
        return {
            "id_densidade": self.id_densidade,
            "id_condicao": self.id_condicao,
            "densidade": float(self.densidade)
        }



# ------------------------------
# ROTAS PARA CIDADE
# ------------------------------
# GET ALL
@app.route('/cidades', methods=['GET'])
def ver_cidades():
    cidades = Cidade.query.all()
    cidades_json = [c.to_json() for c in cidades]
    return gera_resposta(200, 'Cidades', cidades_json)

# GET POR ID
@app.route('/cidades/<int:id_selecionado>', methods=['GET'])
def seleciona_cidade_id(id_selecionado):
    cidade = Cidade.query.filter_by(id_cidade=id_selecionado).first()
    return gera_resposta(200, 'Cidade selecionada', cidade.to_json(), 'Cidade encontrada!')

# POST
@app.route('/cidades', methods=['POST'])
def criar_cidade():
    req = request.get_json()
    try:
        cidade = Cidade(
            id_cidade=req.get('id_cidade'),
            nome=req.get('nome'),
            estado=req.get('estado'),
            bairro=req.get('bairro'),
            latitude=req.get('latitude'),
            longitude=req.get('longitude')
        )
        mydb.session.add(cidade)
        mydb.session.commit()
        return gera_resposta(201, 'Nova cidade', cidade.to_json(), 'Cidade criada com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao criar cidade.')

# DELETE
@app.route('/cidades/<int:id_selecionado>', methods=['DELETE'])
def excluir_cidade(id_selecionado):
    cidade = Cidade.query.filter_by(id_cidade=id_selecionado).first()
    try:
        mydb.session.delete(cidade)
        mydb.session.commit()
        return gera_resposta(200, 'Cidade Excluída', cidade.to_json(), 'Cidade excluída com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao excluir cidade.')

# PUT
@app.route('/cidades/<int:id_selecionado>', methods=['PUT'])
def atualizar_cidade(id_selecionado):
    cidade = Cidade.query.filter_by(id_cidade=id_selecionado).first()
    req = request.get_json()
    try:
        if 'nome' in req: cidade.nome = req['nome']
        if 'estado' in req: cidade.estado = req['estado']
        if 'bairro' in req: cidade.bairro = req['bairro']
        if 'latitude' in req: cidade.latitude = req['latitude']
        if 'longitude' in req: cidade.longitude = req['longitude']

        mydb.session.add(cidade)
        mydb.session.commit()
        return gera_resposta(200, 'Cidade Atualizada', cidade.to_json(), 'Cidade atualizada!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao atualizar cidade.')

# ------------------------------
# ROTAS PARA DEMOGRAFIA
# ------------------------------
# GET ALL
@app.route('/demografias', methods=['GET'])
def ver_demografias():
    demografias = Demografia.query.all()
    demografias_json = [d.to_json() for d in demografias]
    return gera_resposta(200, 'Demografias', demografias_json)

# GET POR ID
@app.route('/demografias/<int:id_selecionado>', methods=['GET'])
def seleciona_demografia_id(id_selecionado):
    demografia = Demografia.query.filter_by(id_demografia=id_selecionado).first()
    return gera_resposta(200, 'Demografia selecionada', demografia.to_json(), 'Demografia encontrada!')

# POST
@app.route('/demografias', methods=['POST'])
def criar_demografia():
    req = request.get_json()
    try:
        demografia = Demografia(
            id_demografia=req.get('id_demografia'),
            id_cidade=req.get('id_cidade'),
            ano_medicao=req.get('ano_medicao'),
            populacao_total=req.get('populacao_total'),
            area_km2=req.get('area_km2'),
            densidade_populacional=req.get('densidade_populacional'),
            urbanizacao_pct=req.get('urbanizacao_pct')
        )
        mydb.session.add(demografia)
        mydb.session.commit()
        return gera_resposta(201, 'Nova demografia', demografia.to_json(), 'Demografia criada com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao criar demografia.')

# DELETE
@app.route('/demografias/<int:id_selecionado>', methods=['DELETE'])
def excluir_demografia(id_selecionado):
    demografia = Demografia.query.filter_by(id_demografia=id_selecionado).first()
    try:
        mydb.session.delete(demografia)
        mydb.session.commit()
        return gera_resposta(200, 'Demografia Excluída', demografia.to_json(), 'Demografia excluída com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao excluir demografia.')

# PUT
@app.route('/demografias/<int:id_selecionado>', methods=['PUT'])
def atualizar_demografia(id_selecionado):
    demografia = Demografia.query.filter_by(id_demografia=id_selecionado).first()
    req = request.get_json()
    try:
        if 'id_cidade' in req: demografia.id_cidade = req['id_cidade']
        if 'ano_medicao' in req: demografia.ano_medicao = req['ano_medicao']
        if 'populacao_total' in req: demografia.populacao_total = req['populacao_total']
        if 'area_km2' in req: demografia.area_km2 = req['area_km2']
        if 'densidade_populacional' in req: demografia.densidade_populacional = req['densidade_populacional']
        if 'urbanizacao_pct' in req: demografia.urbanizacao_pct = req['urbanizacao_pct']

        mydb.session.add(demografia)
        mydb.session.commit()
        return gera_resposta(200, 'Demografia Atualizada', demografia.to_json(), 'Demografia atualizada!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao atualizar demografia.')

# ------------------------------
# ROTAS PARA CONDICAO AMBIENTAL
# ------------------------------
# GET ALL
@app.route('/condicoes', methods=['GET'])
def ver_condicoes():
    condicoes = CondicaoAmbiental.query.all()
    condicoes_json = [c.to_json() for c in condicoes]
    return gera_resposta(200, 'Condicoes', condicoes_json)

# GET POR ID
@app.route('/condicoes/<int:id_selecionado>', methods=['GET'])
def seleciona_condicao_id(id_selecionado):
    condicao = CondicaoAmbiental.query.filter_by(id_condicao=id_selecionado).first()
    return gera_resposta(200, 'Condicao selecionada', condicao.to_json(), 'Condicao encontrada!')

# POST
@app.route('/condicoes', methods=['POST'])
def criar_condicao():
    req = request.get_json()
    try:
        condicao = CondicaoAmbiental(
            id_condicao=req.get('id_condicao'),
            id_cidade=req.get('id_cidade'),
            data_hora=req.get('data_hora'),
            temperatura=req.get('temperatura'),
            umidade=req.get('umidade'),
            pressao=req.get('pressao'),
            co2=req.get('co2'),
            poeira1=req.get('poeira1'),
            poeira2=req.get('poeira2'),
            altitude=req.get('altitude')
        )
        mydb.session.add(condicao)
        mydb.session.commit()
        return gera_resposta(201, 'Nova condicao', condicao.to_json(), 'Condicao criada com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao criar condicao.')

# DELETE
@app.route('/condicoes/<int:id_selecionado>', methods=['DELETE'])
def excluir_condicao(id_selecionado):
    condicao = CondicaoAmbiental.query.filter_by(id_condicao=id_selecionado).first()
    try:
        mydb.session.delete(condicao)
        mydb.session.commit()
        return gera_resposta(200, 'Condicao Excluída', condicao.to_json(), 'Condicao excluída com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao excluir condicao.')

# PUT
@app.route('/condicoes/<int:id_selecionado>', methods=['PUT'])
def atualizar_condicao(id_selecionado):
    condicao = CondicaoAmbiental.query.filter_by(id_condicao=id_selecionado).first()
    req = request.get_json()
    try:
        if 'id_cidade' in req: condicao.id_cidade = req['id_cidade']
        if 'data_hora' in req: condicao.data_hora = req['data_hora']
        if 'temperatura' in req: condicao.temperatura = req['temperatura']
        if 'umidade' in req: condicao.umidade = req['umidade']
        if 'pressao' in req: condicao.pressao = req['pressao']
        if 'co2' in req: condicao.co2 = req['co2']
        if 'poeira1' in req: condicao.poeira1 = req['poeira1']
        if 'poeira2' in req: condicao.poeira2 = req['poeira2']
        if 'altitude' in req: condicao.altitude = req['altitude']

        mydb.session.add(condicao)
        mydb.session.commit()
        return gera_resposta(200, 'Condicao Atualizada', condicao.to_json(), 'Condicao atualizada!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao atualizar condicao.')

# ------------------------------
# ROTAS PARA DENSIDADE
# ------------------------------
# GET ALL
@app.route('/densidades', methods=['GET'])
def ver_densidades():
    densidades = Densidade.query.all()
    densidades_json = [d.to_json() for d in densidades]
    return gera_resposta(200, 'Densidades', densidades_json)

# GET POR ID
@app.route('/densidades/<int:id_selecionado>', methods=['GET'])
def seleciona_densidade_id(id_selecionado):
    densidade = Densidade.query.filter_by(id_densidade=id_selecionado).first()
    return gera_resposta(200, 'Densidade selecionada', densidade.to_json(), 'Densidade encontrada!')

# POST
@app.route('/densidades', methods=['POST'])
def criar_densidade():
    req = request.get_json()
    try:
        densidade = Densidade(
            id_densidade=req.get('id_densidade'),
            id_condicao=req.get('id_condicao'),
            densidade=req.get('densidade')
        )
        mydb.session.add(densidade)
        mydb.session.commit()
        return gera_resposta(201, 'Nova densidade', densidade.to_json(), 'Densidade criada com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao criar densidade.')

# DELETE
@app.route('/densidades/<int:id_selecionado>', methods=['DELETE'])
def excluir_densidade(id_selecionado):
    densidade = Densidade.query.filter_by(id_densidade=id_selecionado).first()
    try:
        mydb.session.delete(densidade)
        mydb.session.commit()
        return gera_resposta(200, 'Densidade Excluída', densidade.to_json(), 'Densidade excluída com sucesso!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao excluir densidade.')

# PUT
@app.route('/densidades/<int:id_selecionado>', methods=['PUT'])
def atualizar_densidade(id_selecionado):
    densidade = Densidade.query.filter_by(id_densidade=id_selecionado).first()
    req = request.get_json()
    try:
        if 'id_condicao' in req: densidade.id_condicao = req['id_condicao']
        if 'densidade' in req: densidade.densidade = req['densidade']

        mydb.session.add(densidade)
        mydb.session.commit()
        return gera_resposta(200, 'Densidade Atualizada', densidade.to_json(), 'Densidade atualizada!')
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, 'Erro', {}, 'Erro ao atualizar densidade.')

# ------------------------------
# FUNÇÃO DE RESPOSTA PADRÃO
# ------------------------------
def gera_resposta(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo
    if mensagem:
        body['mensagem'] = mensagem
    return Response(json.dumps(body), status=status, mimetype='application/json')

if __name__ == '__main__':
    with app.app_context():
        mydb.create_all()  # Cria as tabelas no banco de dados
    
    start_mqtt()
    app.run(port=5000, host='localhost', debug=True)




