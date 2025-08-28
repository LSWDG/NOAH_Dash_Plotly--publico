#!/bin/bash
set -e

# Inicia o daemon do Tailscale em background
echo "Iniciando tailscaled..."
tailscaled &

# Aguarda 5 segundos para o daemon inicializar
sleep 5

# Conecta à rede Tailscale usando a auth key
echo "Conectando à rede Tailscale..."
tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=render-dash --accept-routes=true --accept-dns=false --ssh=false

# Inicia a aplicação Dash
echo "Iniciando aplicação Dash..."
exec gunicorn app:server -b 0.0.0.0:$PORT --workers=2
