# Usa uma imagem leve do Python
FROM python:3.14-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o cache)
COPY requirements.txt .

# Instala as dependências (flask-sqlalchemy, flask-migrate, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Expõe a porta que o Flask usa
EXPOSE 5001

# Comando para rodar a aplicação
CMD ["python", "run.py"]