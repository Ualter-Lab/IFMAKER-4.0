## 📋 Funcionalidades

*   [x] Agendamento de equipamentos com intervalo de datas.
*   [x] Interface responsiva para dispositivos móveis.
*   [x] Validação de formulários via JavaScript (Toast notifications).
*   [ ] Painel de administração para monitores (Em desenvolvimento).

---

### Dicas para o seu perfil:
*   **Humanize o texto:** Como você mesmo solicitou anteriormente, evite termos excessivamente robóticos. O README deve explicar o "porquê" do projeto (resolver a organização do laboratório) e não apenas listar funções.
*   **GitHub Bio:** Lembre-se de que sua bio deve focar nas suas habilidades gerais (Python, Flask, Jiu-Jitsu, Robótica), mantendo os detalhes específicos para o README de cada repositório.

O que achou dessa estrutura? SeCom certeza, Walter! Ter um **README.md** bem estruturado é essencial para o seu portfólio "WN Web", pois mostra que você se preocupa com a documentação e organização do código. Como você está usando **Python**, **Flask** e planeja usar **Docker**, o README deve refletir essa maturidade técnica.

Aqui está um modelo direto e humano para o seu projeto do **IFMAKER**, focado em habilidades e clareza:

---

# 🛠️ IFMAKER - Portal de Agendamento

Sistema de gerenciamento e reserva de equipamentos para o laboratório IFMAKER do **IFAL - Campus Marechal Deodoro**. O projeto permite que alunos e monitores solicitem o uso de ferramentas e espaços de forma organizada.

## 🚀 Tecnologias Utilizadas

*   **Backend:** Python 3.14 com Flask.
*   **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção).
*   **ORM:** SQLAlchemy para manipulação de dados.
*   **Frontend:** HTML5, CSS3 (Tailwind CSS) e JavaScript (Fetch API).
*   **Containerização:** Docker & Docker Compose.

## 📦 Como rodar o projeto

### Pré-requisitos
*   Python 3.14+
*   Docker (opcional, mas recomendado)

### Instalação Manual
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/ifmaker-portal.git](https://github.com/seu-usuario/ifmaker-portal.git)
    cd ifmaker-portal
    ```
2.  **Crie e ative sua venv:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Mac/Linux
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Inicialize o banco de dados:**
    ```bash
    python
    >>> from backend import create_app, db
    >>> from backend.models import Agendamento
    >>> app = create_app()
    >>> with app.app_context():
    >>>     db.create_all()
    >>> exit()
    ```
5.  **Execute o servidor:**
    ```bash
    python run.py
    ```

### Via Docker
```bash
docker-compose up --build
📋
