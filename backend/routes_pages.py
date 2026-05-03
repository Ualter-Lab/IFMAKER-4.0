from flask import Blueprint, request, jsonify, render_template
from .models import Agendamento
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/agendamento', methods=['POST'])
def realizar_agendamento():
    dados = request.get_json()
    
    try:
        # Convertendo as strings de data para objetos date do Python
        inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
        fim = datetime.strptime(dados['data_fim'], '%Y-%m-%d').date()

        novo_agendamento = Agendamento(
            nome=dados['nome'],
            data_inicio=inicio,
            data_fim=fim,
            objeto_uso=dados['objeto_uso']
        )

        db.session.add(novo_agendamento)
        db.session.commit()
        
        return jsonify({"message": "Agendamento realizado!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400