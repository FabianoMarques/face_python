# Use a imagem base do Python (versão 3.10)
FROM python:3.10

# Instalar dependências do sistema para compilar dlib e outras bibliotecas
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gfortran \
    libjpeg-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    python3-dev

# Criar e ativar o ambiente virtual
RUN python -m venv /opt/venv

# Configurar o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Definir o diretório de trabalho
WORKDIR /

# Copiar o arquivo requirements.txt para o contêiner
# Se você estiver usando um requirements.txt local, copie-o para dentro do contêiner
COPY requirements.txt /app/

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o restante do projeto para o contêiner
COPY . /app/

# Comando para iniciar o aplicativo (mude 'main.py' para o seu arquivo principal)
CMD ["python", "detectar_faces.py"]
