#!/bin/sh
set -e

echo "Installing OpenSSL..."
apk add --no-cache openssl

echo "Creating certificate directories..."
mkdir -p /backend-certs /frontend-certs

# Generate Root CA
if [ ! -f /backend-certs/rootCA-key.pem ]; then
  echo "Generating Root CA..."
  openssl genrsa -out /backend-certs/rootCA-key.pem 4096
  openssl req -new -x509 -days 365 -key /backend-certs/rootCA-key.pem -out /backend-certs/rootCA.pem -subj "/C=US/ST=CA/L=SF/O=ZARA/CN=ZARA Root CA"
  cp /backend-certs/rootCA.pem /frontend-certs/rootCA.pem
  cp /backend-certs/rootCA-key.pem /frontend-certs/rootCA-key.pem
fi

# Generate backend SSL certificates
if [ ! -f /backend-certs/api.zara.com.pem ]; then
  echo "Generating backend SSL certificates..."
  openssl genrsa -out /backend-certs/api.zara.com-key.pem 2048
  openssl req -new -key /backend-certs/api.zara.com-key.pem -out /backend-certs/api.zara.com.csr -subj "/C=US/ST=CA/L=SF/O=ZARA/CN=api.zara.com"
  
  cat > /backend-certs/api.zara.com.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = api.zara.com
DNS.2 = localhost
DNS.3 = backend
IP.1 = 127.0.0.1
EOF
  
  openssl x509 -req -in /backend-certs/api.zara.com.csr -CA /backend-certs/rootCA.pem -CAkey /backend-certs/rootCA-key.pem -CAcreateserial -out /backend-certs/api.zara.com.pem -days 365 -extfile /backend-certs/api.zara.com.ext
  openssl pkcs12 -export -out /backend-certs/keystore.p12 -inkey /backend-certs/api.zara.com-key.pem -in /backend-certs/api.zara.com.pem -certfile /backend-certs/rootCA.pem -password pass:changeit
  rm /backend-certs/api.zara.com.csr /backend-certs/api.zara.com.ext
fi

# Generate frontend SSL certificates
if [ ! -f /frontend-certs/cert.pem ]; then
  echo "Generating frontend SSL certificates..."
  openssl genrsa -out /frontend-certs/dev-key.pem 2048
  openssl req -new -key /frontend-certs/dev-key.pem -out /frontend-certs/dev.csr -subj "/C=US/ST=CA/L=SF/O=ZARA/CN=zara.com"
  
  cat > /frontend-certs/dev.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = zara.com
DNS.2 = localhost
DNS.3 = frontend
IP.1 = 127.0.0.1
EOF
  
  openssl x509 -req -in /frontend-certs/dev.csr -CA /backend-certs/rootCA.pem -CAkey /backend-certs/rootCA-key.pem -CAcreateserial -out /frontend-certs/dev.pem -days 365 -extfile /frontend-certs/dev.ext
  cp /frontend-certs/dev.pem /frontend-certs/cert.pem
  cp /frontend-certs/dev-key.pem /frontend-certs/key.pem
  rm /frontend-certs/dev.csr /frontend-certs/dev.ext
fi

echo "Certificate generation completed!"
echo "Backend certificates: /backend-certs/"
echo "Frontend certificates: /frontend-certs/"
echo "Root CA: /backend-certs/rootCA.pem"
