# 🛠️ IFMAKER & LAB 4.0 — IFAL Campus Marechal Deodoro

O **IFMAKER 4.0** é um sistema web completo desenvolvido para automatizar e gerir as atividades diárias do laboratóriomaker do IFAL - Campus Marechal Deodoro. A aplicação centraliza o controlo de inventário de componentes de robótica/eletrónica, a escala de horários da equipa de monitoria e o fluxo de agendamentos e reservas de máquinas (como impressoras 3D).

O foco principal do projeto é a **segurança de dados, modularização e experiência do utilizador**, substituindo controlos manuais por uma plataforma digital intuitiva e robusta.

---

## 🚀 Funcionalidades Principais

* **👥 Autenticação de Utilizadores Dinâmica:** * **Área do Aluno:** Login via Matrícula institucional e senha para efetuar pedidos de agendamento de equipamentos.
    * **Área do Monitor / Admin:** Login via Username técnico para gerir o laboratório, aprovar/recusar reservas e monitorizar o inventário.
* **🔒 Segurança Avançada (Proteção de Credenciais):** As palavras-passe **nunca** são guardadas em texto limpo no banco de dados. O sistema utiliza algoritmos de *Hashing* de via única (**scrypt/PBKDF2** através do pacote Werkzeug), tornando matematicamente impossível reverter ou descriptografar os dados salvos.
* **📅 Sistema Dinâmico de Agendamentos:** Os alunos solicitam horários e equipamentos. Os monitores recebem os pedidos em tempo real no painel de moderação e podem **Aprovar** ou **Recusar** com cliques rápidos, atualizando a interface instantaneamente via requisições assíncronas (`Fetch API`).
* **📦 Gestão de Inventário e Escala:** Exibição dinâmica de componentes de fabricação digital, eletrónica e insumos, além da escala ativa de turnos de monitoria organizada por Jinja2.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando uma arquitetura moderna dividida em camadas:

* **Backend:** Python 3 com o micro-framework **Flask**.
* **Banco de Dados:** **SQLite** com **Flask-SQLAlchemy** (mapeamento objeto-relacional / ORM).
* **Gestão de Sessões:** **Flask-Login** para proteção de rotas e cookies seguros.
* **Segurança:** Criptografia de senhas com **Werkzeug.security**.
* **Frontend:** HTML5, CSS3 (com paleta temática Maker moderna e responsiva) e **Jinja2** como motor de renderização de templates do lado do servidor.
* **Interações Dinâmicas:** JavaScript assíncrono (`Fetch API` / AJAX) para processamento de formulários e estados sem recarregamento de página.

---

## 📁 Estrutura do Projeto

O projeto segue estritamente o padrão de organização do Flask:

```text
meu_projeto/
│
├── app.py                  # Código-fonte Python (Rotas, Modelos SQL, CLI)
├── instance/              # Pasta exclusiva para o banco de dados em sqlite
│   └── ifmaker.db               # Banco de dados SQLite (Gerado automaticamente)
├── requirements.txt        # Arquivo de dependências do Python
│
└── templates/              # Pasta exclusiva para os arquivos HTML
    └── index.html          # Template central renderizado com Jinja2
