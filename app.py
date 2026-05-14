import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurações do App
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_super_segura_aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ifmaker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuração do Controle de Sessão (Login)
login_manager = LoginManager(app)
login_manager.login_view = 'acesso' # Redireciona para a aba de acesso se não logado
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"


# ==========================================
# MODELS (BANCO DE DADOS)
# ==========================================

# Tabela associativa de Monitores e seus Horários/Dias na escala de Monitoria
class HorarioMonitoria(db.Model):
    __tablename__ = 'horarios_monitoria'
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(20), nullable=False) # Ex: 'Segunda', 'Terça'
    turno = db.Column(db.String(10), nullable=False)      # Ex: 'Manhã', 'Tarde'
    monitor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Identificadores específicos do IFAL
    matricula = db.Column(db.String(20), unique=True, nullable=True) # Para Alunos
    username = db.Column(db.String(50), unique=True, nullable=True)  # Para Monitores/Admins
    
    role = db.Column(db.String(20), nullable=False, default='aluno')  # 'aluno', 'monitor', 'admin'
    is_voluntario = db.Column(db.Boolean, default=False)              # Para chips estilizados de monitores
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='usuario', lazy=True)
    horarios = db.relationship('HorarioMonitoria', backref='monitor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ItemInventario(db.Model):
    __tablename__ = 'inventario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(30), nullable=False) # 'fabricacao', 'eletronica', 'insumo'
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='ok') # 'ok', 'busy', 'unavail'


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    equipamento = db.Column(db.String(50), nullable=False) # '3d', 'laser', 'arduino'
    data_reserva = db.Column(db.String(10), nullable=False) # Formato YYYY-MM-DD
    horario_slot = db.Column(db.String(10), nullable=False) # Ex: '08:00'
    projeto_vinculo = db.Column(db.String(100), nullable=True) # Nome do projeto ou disciplina
    status = db.Column(db.String(20), nullable=False, default='Pendente') # 'Pendente', 'Aprovado', 'Recusado'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ==========================================
# ROTAS / VIEWS
# ==========================================

@app.route('/')
def index():
    # Coleta de dados dinâmica para renderizar no painel principal
    items_inventario = ItemInventario.query.all()
    lista_monitores = Usuario.query.filter_by(role='monitor').all()
    horarios_escala = HorarioMonitoria.query.all()
    
    # Agendamentos para exibição no Dashboard do Monitor/Admin
    todos_agendamentos = Agendamento.query.order_by(Agendamento.data_reserva.desc()).all() if not current_user.is_anonymous and current_user.role in ['monitor', 'admin'] else []
    
    return render_template(
        'index.html', 
        inventario=items_inventario, 
        monitores=lista_monitores,
        horarios=horarios_escala,
        agendamentos=todos_agendamentos
    )


# Rota de Login Unificado / Mapeamento do Painel de Acesso
@app.route('/login', methods=['POST'])
def login():
    tipo_usuario = request.form.get('tipo_usuario') # 'aluno' ou 'monitor'
    
    if tipo_usuario == 'aluno':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(matricula=matricula, role='aluno').first()
    else:
        username = request.form.get('username')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(username=username).filter(Usuario.role.in_(['monitor', 'admin'])).first()

    if user and user.check_password(senha):
        login_user(user)
        flash(f"Bem-vindo de volta, {user.nome}!", "success")
        return redirect(url_for('index'))
    
    flash("Credenciais inválidas. Verifique os campos e tente novamente.", "danger")
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for('index'))


# Rota de Cadastro de Novo Aluno/Usuário
@app.route('/registrar_aluno', methods=['POST'])
def registrar_aluno():
    nome = request.form.get('nome')
    email = request.form.get('email')
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')
    
    if Usuario.query.filter((Usuario.email == email) | (Usuario.matricula == matricula)).first():
        flash("Email ou Matrícula já cadastrados.", "danger")
        return redirect(url_for('index'))
        
    novo_aluno = Usuario(nome=nome, email=email, matricula=matricula, role='aluno')
    novo_aluno.set_password(senha)
    
    db.session.add(novo_aluno)
    db.session.commit()
    
    flash("Cadastro realizado! Faça login utilizando sua matrícula.", "success")
    return redirect(url_for('index'))


# Processamento assíncrono de Agendamento (JSON/Fetch)
@app.route('/api/agendar', methods=['POST'])
@login_required
def api_agendar():
    data = request.get_json()
    
    equipamento = data.get('equipamento')
    data_reserva = data.get('data')
    horario_slot = data.get('horario')
    projeto = data.get('projeto', '')

    # Verificação simples de colisão de horário para o mesmo equipamento
    colisao = Agendamento.query.filter_by(
        equipamento=equipamento, 
        data_reserva=data_reserva, 
        horario_slot=horario_slot, 
        status='Aprovado'
    ).first()
    
    if colisao:
        return jsonify({'success': False, 'message': 'Este equipamento já está reservado neste horário!'}), 400

    novo_agendamento = Agendamento(
        equipamento=equipamento,
        data_reserva=data_reserva,
        horario_slot=horario_slot,
        projeto_vinculo=projeto,
        usuario_id=current_user.id
    )
    
    db.session.add(novo_agendamento)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Solicitação de agendamento enviada com sucesso!'})


# Gerenciamento de Agendamento pelos Monitores (Aprovar/Recusar)
@app.route('/api/agendamento/<int:id>/status', methods=['POST'])
@login_required
def atualizar_status_agendamento(id):
    if current_user.role != 'monitor':
        return jsonify({'success': False, 'message': 'Acesso negado. Apenas monitores podem moderar.'}), 403
        
    data = request.get_json()
    status_recebido = data.get('status')
    
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = status_recebido
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Status atualizado para {status_recebido}.'})


# CLI Command para alimentar o banco de dados com dados iniciais de teste
@app.cli.command("add-monitor")
def add_monitor():
    """Cadastra um novo monitor interativamente pelo terminal."""
    db.create_all()
    
    print("\n" + "="*40)
    print("  CADASTRO DE NOVO MONITOR (IFMAKER)  ")
    print("="*40)
    
    nome = input("Nome Completo: ").strip()
    email = input("E-mail Institucional: ").strip()
    username = input("Nome de Utilizador (Username para Login): ").strip()
    senha = input("Palavra-passe (Senha): ").strip()
    
    is_vol_input = input("É monitor Voluntário? (s/n): ").strip().lower()
    is_voluntario = True if is_vol_input == 's' else False

    # Validação básica para não duplicar utilizadores
    if Usuario.query.filter((Usuario.email == email) | (Usuario.username == username)).first():
        print("\n❌ Erro: Já existe um monitor com este E-mail ou Username!")
        return

    try:
        # Cria o objeto do novo monitor
        novo_monitor = Usuario(
            nome=nome, 
            email=email, 
            username=username, 
            role='monitor', 
            is_voluntario=is_voluntario
        )
        novo_monitor.set_password(senha)
        db.session.add(novo_monitor)
        db.session.commit()
        
        print(f"\n✅ Monitor {nome} cadastrado com sucesso!")
        print(f"👉 Login via painel com o username: {username}\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Erro ao salvar no banco de dados: {e}")


if __name__ == '__main__':
    # Cria as tabelas caso não existam ao rodar diretamente
    with app.app_context():
        db.create_all()
    app.run(debug=True)