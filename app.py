import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests

app = Flask(__name__)

load_dotenv()

# Configurações do App
app.config['SECRET_KEY'] = os.getenv('KEY')
database_url = os.getenv('URL_DATABASE')

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

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
    agendamentos = db.relationship(
    'Agendamento',
    backref='usuario',
    lazy=True,
    cascade='all, delete-orphan',
    )
    
    horarios = db.relationship(
    'HorarioMonitoria',
    backref='monitor',
    lazy=True,
    cascade='all, delete-orphan'
    )

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
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='Pendente') # 'Pendente', 'Aprovado', 'Recusado'
    
    
    usuario_id = db.Column(
    db.Integer,
    db.ForeignKey('usuarios.id', ondelete='CASCADE'),
    nullable=False
    )

def criar_card_trello(agendamento):
    print("TRELLO_KEY:", os.getenv("TRELLO_KEY"))
    print("TRELLO_TOKEN:", os.getenv("TRELLO_TOKEN"))
    print("TRELLO_LIST_ID:", os.getenv("TRELLO_LIST_ID"))

    url = "https://api.trello.com/1/cards"

    params = {
        "key": os.getenv("TRELLO_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
        "idList": os.getenv("TRELLO_LIST_ID"),
        "name": f"{agendamento.equipamento} - {agendamento.usuario.nome}",
        "desc": f"""
Aluno: {agendamento.usuario.nome}
Equipamento: {agendamento.equipamento}
Data: {agendamento.data_reserva}
Horário: {agendamento.horario_slot}
Projeto: {agendamento.projeto_vinculo}
Descrição: {agendamento.descricao or 'Sem descrição'}
"""
    }

    r = requests.post(url, params=params, timeout=10)

    print("TRELLO STATUS:", r.status_code)
    print("TRELLO RESPOSTA:", r.text)

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
    lista_monitores = Usuario.query.filter(
        Usuario.role.in_([
            'monitor',
            'coordenador',
            'admin'
        ])
    ).all()
    horarios_escala = HorarioMonitoria.query.all()

    allagendamentos =  db.session.query(Agendamento.id).count()
    allequipamentos = db.session.query(ItemInventario.id).count()
    
    # Agendamentos para exibição no Dashboard do Monitor/Admin
    todos_agendamentos = (
    Agendamento.query.order_by(Agendamento.data_reserva.desc()).all()
    if not current_user.is_anonymous and current_user.role in ['monitor', 'coordenador', 'admin']
    else []
)
    
    return render_template(
        'index.html', 
        inventario=items_inventario, 
        monitores=lista_monitores,
        horarios=horarios_escala,
        agendamentos=todos_agendamentos,
        allagendamentos = allagendamentos,
        allequipamentos = allequipamentos
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
        user = Usuario.query.filter_by(username=username).filter(Usuario.role.in_(['monitor', 'coordenador', 'admin'])).first()

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
    descricao = data.get('descricao', '').strip()

    if equipamento == 'outros' and not descricao:
        return jsonify({
            'success': False,
            'message': 'Descreva qual equipamento ou necessidade você possui.'
        }), 400

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
        descricao = descricao,
        usuario_id=current_user.id
    )
    
    db.session.add(novo_agendamento)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Solicitação enviada com sucesso!'
    })


# Gerenciamento de Agendamento pelos Monitores (Aprovar/Recusar)
@app.route('/api/agendamento/<int:id>/status', methods=['POST'])
@login_required
def atualizar_status_agendamento(id):
    if current_user.role not in ['monitor', 'coordenador', 'admin']:
        return jsonify({
            'success': False,
            'message': 'Acesso negado.'
        }), 403

    data = request.get_json()
    status_recebido = data.get('status')

    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = status_recebido
    db.session.commit()

    if status_recebido == 'Aprovado':
        print("STATUS APROVADO, TENTANDO CRIAR CARD...")
        try:
            criar_card_trello(agendamento)
            print("FUNÇÃO TRELLO EXECUTADA")
        except Exception as e:
            print("ERRO TRELLO:", e)

    return jsonify({
        'success': True,
        'message': f'Status atualizado para {status_recebido}.'
    })
    
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

    matricula = None
    you_have_matricula = input("Você tem número de matrícula? (s/n): ").strip().lower()
    if you_have_matricula == "s" :
        matricula = input("Número de matrícula: ")
    senha = input("Palavra-passe (Senha): ").strip()
    
    is_vol_input = input("É monitor Voluntário? (s/n): ").strip().lower()
    is_voluntario = True if is_vol_input == 's' else False

    usuario_existente = Usuario.query.filter(
        (Usuario.email == email) | (Usuario.username == username)
    ).first()

    matricula_existente = False
    if matricula:
        matricula_existente = Usuario.query.filter(Usuario.matricula == matricula).first()

    if usuario_existente or matricula_existente:
        print("\n❌ Erro: Já existe um monitor com este E-mail, Username ou matrícula!")
        return

    try:
        # Cria o objeto do novo monitor
        novo_monitor = Usuario(
            nome=nome, 
            email=email, 
            username=username,
            matricula=matricula,
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

@app.cli.command("setup-inventario")
def setup_inventario():
    """Configura o preset do inventário com os dados exatos do invData."""
    db.create_all()
    
    # Dados extraídos exatamente do teu invData
    inv_data = [
        {'name': 'Impressora 3D Creality Ender 3', 'cat': 'fabricacao', 'desc': 'Volume de impressão 220×220×250mm, filamento PLA/ABS/PETG. Resolução mín. 0.1mm.', 'status': 'ok', 'qty': 2},
        {'name': 'Cortadora Laser 40W', 'cat': 'fabricacao', 'desc': 'Área de trabalho 300×200mm. Corte e gravação em acrílico, madeira, MDF, couro.', 'status': 'ok', 'qty': 1},
        {'name': 'Fresadora CNC 3018', 'cat': 'fabricacao', 'desc': 'Eixos XYZ, ideal para PCB e madeira. Software GRBL. Área 300×180mm.', 'status': 'ok', 'qty': 1},
        {'name': 'Bancada de Eletrônica', 'cat': 'eletronica', 'desc': 'Estação de solda, multímetro, osciloscópio USB, fonte de bancada regulável.', 'status': 'ok', 'qty': 4},
        {'name': 'Kit Arduino Mega + Shields', 'cat': 'eletronica', 'desc': 'Arduino Mega 2560, protoboard, sensores variados, módulos Bluetooth e Wi-Fi.', 'status': 'ok', 'qty': 10},
        {'name': 'Kit ESP32 IoT', 'cat': 'eletronica', 'desc': 'Módulos ESP32 DevKit, sensores de temperatura, umidade, presença e luz.', 'status': 'ok', 'qty': 8},
        {'name': 'Kit Robótica Educacional', 'cat': 'eletronica', 'desc': 'Chassi robô 2WD/4WD, motores DC, drivers L298N, sensores ultrassônico.', 'status': 'unavail', 'qty': 3},
        {'name': 'Osciloscópio Digital 50MHz', 'cat': 'eletronica', 'desc': '2 canais, amostragem 1GSa/s, 7" colorido. Ideal para análise de sinais.', 'status': 'ok', 'qty': 2},
        {'name': 'Filamento PLA 1.75mm', 'cat': 'insumo', 'desc': 'Bobinas de 1kg em diversas cores. Compatível com todas as impressoras do lab.', 'status': 'ok', 'qty': 15},
        {'name': 'Folha MDF 3mm', 'cat': 'insumo', 'desc': 'Chapas 30×20cm para uso na cortadora laser. Estoque reabastecido semanalmente.', 'status': 'ok', 'qty': 30},
        {'name': 'Componentes SMD Sortidos', 'cat': 'insumo', 'desc': 'Resistores, capacitores, LEDs, transistores e CIs em embalagens organizadas.', 'status': 'busy', 'qty': 5},
        {'name': 'Estação de Solda Hakko', 'cat': 'eletronica', 'desc': 'Temperatura ajustável 200–480°C, ponteiras variadas, suporte e esponja inclusos.', 'status': 'ok', 'qty': 6},
    ]

    print("\n📦 Sincronizando inventário com o banco de dados...")
    
    novos_itens = 0
    for item in inv_data:
        # Verifica se o item já existe para evitar duplicados ao rodar o comando várias vezes
        if not ItemInventario.query.filter_by(nome=item['name']).first():
            novo = ItemInventario(
                nome=item['name'],
                categoria=item['cat'],
                descricao=item['desc'],
                quantidade=item['qty'],
                status=item['status']
            )
            db.session.add(novo)
            novos_itens += 1
    
    db.session.commit()
    print(f"✅ Concluído! {novos_itens} itens adicionados com sucesso.")

@app.route('/inventario/editar/<int:item_id>', methods=['POST'])
@login_required
def editar_inventario(item_id):
    # Verifica se o usuário tem permissão (apenas monitor ou admin)
    if current_user.role not in ['monitor', 'admin']:
        flash("Acesso negado. Apenas monitores podem editar o inventário.", "danger")
        return redirect(url_for('index'))

    item = ItemInventario.query.get_or_404(item_id)
    
    # Atualiza os campos com os dados do formulário
    item.nome = request.form.get('nome')
    item.categoria = request.form.get('categoria')
    item.quantidade = int(request.form.get('quantidade', 0))
    item.status = request.form.get('status')
    item.descricao = request.form.get('descricao')

    try:
        db.session.commit()
        flash(f"Item '{item.nome}' atualizado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao atualizar o item. Tente novamente.", "danger")
    
    return redirect(url_for('index'))

@app.route('/inventario/adicionar', methods=['POST'])
def adicionar_inventario():
    nome = request.form.get('nome')
    quantidade = request.form.get('quantidade')
    descricao = request.form.get('descricao')
    status = request.form.get('status')
    categoria = request.form.get('categoria', 'Geral')

    novo_item = ItemInventario(
        nome=nome,
        quantidade=int(quantidade),
        descricao=descricao,
        status=status,
        categoria=categoria
    )
    
    db.session.add(novo_item)
    db.session.commit()
    
    # Redireciona de volta para a página do painel/gerenciamento
    return redirect(url_for('index'))

@app.route('/monitor/adicionar', methods=['POST'])
@login_required
def adicionar_monitor():
    if current_user.role not in ['monitor', 'coordenador', 'admin']:
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    nome = request.form.get('nome')
    email = request.form.get('email')
    username = request.form.get('username')
    senha = request.form.get('senha')
    role_recebida = request.form.get('role', 'monitor')
    is_voluntario = role_recebida == 'monitor_voluntario'
    role_final = 'monitor' if is_voluntario else role_recebida

    if Usuario.query.filter((Usuario.email == email) | (Usuario.username == username)).first():
        flash("Já existe um monitor com esse email ou username.", "danger")
        return redirect(url_for('index'))

    novo_monitor = Usuario(
        nome=nome,
        email=email,
        username=username,
        role=role_final,
        is_voluntario=is_voluntario
    )

    novo_monitor.set_password(senha)

    db.session.add(novo_monitor)
    db.session.commit()

    flash("Monitor cadastrado com sucesso!", "success")
    return redirect(url_for('index'))


@app.route('/monitor/remover/<int:monitor_id>', methods=['POST'])
@login_required
def remover_monitor(monitor_id):

    # Apenas coordenadores e admins podem remover
    if current_user.role not in ['coordenador', 'admin']:
        flash("Apenas coordenadores e administradores podem remover membros.", "danger")
        return redirect(url_for('index'))

    monitor = Usuario.query.get_or_404(monitor_id)

    # Impede remover a si mesmo
    if monitor.id == current_user.id:
        flash("Você não pode remover a si mesmo.", "danger")
        return redirect(url_for('index'))

    Agendamento.query.filter_by(usuario_id=monitor.id).delete()
    db.session.delete(monitor)
    db.session.commit()
    
    flash("Membro removido com sucesso!", "success")
    return redirect(url_for('index'))

@app.route('/agendamentos/apagar-todos', methods=['POST'])
@login_required
def apagar_todos_agendamentos():

    if current_user.role not in ['coordenador', 'admin']:
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    try:
        quantidade = Agendamento.query.count()

        Agendamento.query.delete()

        db.session.commit()

        flash(
            f"{quantidade} agendamento(s) removido(s) com sucesso!",
            "success"
        )

    except Exception as e:
        db.session.rollback()
        print("Erro ao apagar agendamentos:", e)

        flash(
            "Erro ao apagar os agendamentos.",
            "danger"
        )

    return redirect(url_for('index'))
    
@app.route('/ping')
def ping():
    return "ok", 200

@app.route('/restore', methods=['POST'])
def restore():
    data = request.get_json()

    try:
        for u in data.get("usuarios", []):
            if not Usuario.query.filter_by(email=u["email"]).first():
                usuario = Usuario(
                    nome=u["nome"],
                    email=u["email"],
                    username=u.get("username"),
                    matricula=u.get("matricula"),
                    password_hash=u["password_hash"],
                    role=u["role"],
                    is_voluntario=u.get("is_voluntario", False)
                )
                db.session.add(usuario)

        db.session.commit()

        for a in data.get("agendamentos", []):
            agendamento = Agendamento(
                equipamento=a["equipamento"],
                data_reserva=a["data_reserva"],
                horario_slot=a["horario_slot"],
                projeto_vinculo=a.get("projeto_vinculo"),
                descricao=a.get("descricao"),
                status=a["status"],
                usuario_id=a["usuario_id"]
            )
            db.session.add(agendamento)

        db.session.commit()

        return "Backup restaurado com sucesso!"

    except Exception as e:
        db.session.rollback()
        return f"Erro ao restaurar: {e}", 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Cria as tabelas caso não existam ao rodar diretamente
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
