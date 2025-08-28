FROM python:3.11-slim

# Instala pacotes básicos, Tailscale e driver ODBC SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https iproute2 iptables build-essential unixodbc-dev libgssapi-krb5-2 libssl1.1 libcurl4 && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /app

# Copia dependências Python e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código e entrypoint
COPY . .

# Define script de entrypoint
ENTRYPOINT ["./entrypoint.sh"]

