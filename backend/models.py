from . import db
from datetime import datetime

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    objeto_uso = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Agendamento {self.nome}>'