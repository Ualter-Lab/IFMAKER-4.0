## 📋 Funcionalidades

*   [x] Agendamento de equipamentos com intervalo de datas.
*   [x] Interface responsiva para dispositivos móveis.
*   [x] Validação de formulários via JavaScript (Toast notifications).
*   [ ] Painel de administração para monitores (Em desenvolvimento).

---

# 🛠️ IFMAKER - Portal de Agendamento

Sistema de gerenciamento e reserva de equipamentos para o laboratório IFMAKER do **IFAL - Campus Marechal Deodoro**. O projeto permite que alunos e monitores solicitem o uso de ferramentas e espaços de forma organizada.

## 🚀 Tecnologias Utilizadas

*   **Backend:** Python 3.14 com Flask.
*   **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção).
*   **ORM:** SQLAlchemy para manipulação de dados.
*   **Frontend:** HTML5, CSS3 e JavaScript (Fetch API).
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
