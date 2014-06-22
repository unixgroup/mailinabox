#!/bin/bash
#
# SSL Certificate
#
# Create a self-signed SSL certificate if one has not yet been created.
#
# The certificate is for PUBLIC_HOSTNAME specifically and is used for:
#
#  * IMAP
#  * SMTP submission (port 587) and opportunistic TLS (when on the receiving end)
#  * the DNSSEC DANE TLSA record for SMTP
#  * HTTPS (for PUBLIC_HOSTNAME only)
#  * Mozilla Persona identity provisioning (the raw key but not the certificate)
#
# When other domains besides PUBLIC_HOSTNAME are served over HTTPS,
# we generate a domain-specific self-signed certificate in the management
# daemon (web_update.py) as needed.

source setup/functions.sh # load our functions
source /etc/mailinabox.conf # load global vars

apt_install openssl

mkdir -p $STORAGE_ROOT/ssl

# Generate a new private key if one doesn't already exist.
if [ ! -f $STORAGE_ROOT/ssl/ssl_certificate.pem ]; then
	# Set the umask so the key file is not world-readable.
	(umask 077; openssl genrsa -out $STORAGE_ROOT/ssl/ssl_private_key.pem 2048)
fi

# Export the public key. Ensure that the keys correspond by always
# running this step even if the file already exists. Make it readable.
openssl rsa -in $STORAGE_ROOT/ssl/ssl_private_key.pem -noout -modulus | sed "s/Modulus=//" \
	> $STORAGE_ROOT/ssl/public_key_modulus.txt
chown $STORAGE_USER $STORAGE_ROOT/ssl/public_key_modulus.txt

# Generate a certificate signing request if one doesn't already exist.
if [ ! -f $STORAGE_ROOT/ssl/ssl_cert_sign_req.csr ]; then
	openssl req -new -key $STORAGE_ROOT/ssl/ssl_private_key.pem -out $STORAGE_ROOT/ssl/ssl_cert_sign_req.csr \
	  -subj "/C=$CSR_COUNTRY/ST=/L=/O=/CN=$PUBLIC_HOSTNAME"
fi

# Generate a SSL certificate by self-signing if a SSL certificate doesn't yet exist.
if [ ! -f $STORAGE_ROOT/ssl/ssl_certificate.pem ]; then
	openssl x509 -req -days 365 \
	  -in $STORAGE_ROOT/ssl/ssl_cert_sign_req.csr -signkey $STORAGE_ROOT/ssl/ssl_private_key.pem -out $STORAGE_ROOT/ssl/ssl_certificate.pem
fi

echo
echo "Your SSL certificate's fingerpint is:"
openssl x509 -in /home/user-data/ssl/ssl_certificate.pem -noout -fingerprint
echo
