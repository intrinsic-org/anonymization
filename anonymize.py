import argparse
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from getpass import getpass
import pandas as pd
import base64
import secrets
from simhash import Simhash

# Key generation
def generate_key(password_provided=None, salt=None):
    if password_provided is None:
        password_provided = getpass("Enter password to generate secret key: ")

    if salt is None:
        salt = secrets.token_bytes(16)

    password = password_provided.encode()  # Convert to type bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )

    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    return key, salt

# PII data anonymization
def anonymize(input_csv, output_csv, schema_yaml, key, enrich_simhash=True):
    # Load YAML schema file
    with open(schema_yaml, 'r') as f:
        schema = yaml.safe_load(f)

    df = pd.read_csv(input_csv)

    # Initialize the fernet class
    f = Fernet(key)

    for column in df.columns:
        # If the column is PII, encrypt it
        if schema[column]['pii']:
            if enrich_simhash:
                # Add a simhash column for each column to enrich it
                df[f'{column}_simhash'] = df[column].apply(lambda x: str(Simhash(x).value))
            # Encrypt the column
            df[column] = df[column].apply(lambda x: f.encrypt(x.encode()).decode())

    df.to_csv(output_csv, index=False)

# PII data de-anonymization
def reveal(input_csv, output_csv, schema_yaml, key):
    # Load YAML schema file
    with open(schema_yaml, 'r') as f:
        schema = yaml.safe_load(f)

    df = pd.read_csv(input_csv)

    # Initialize the fernet class
    f = Fernet(key)

    for column in df.columns:
        # If the column is PII, decrypt it
        # If it ends in "_simhash", remove it
        if not (column.endswith("_simhash")) and schema[column]['pii']:
            df[column] = df[column].apply(lambda x: f.decrypt(x.encode()).decode())

    df.to_csv(output_csv, index=False)

def main():
    parser = argparse.ArgumentParser(description='Anonymize/reveal a CSV file based on a provided YAML schema.')
    parser.add_argument('action', choices=['anonymize', 'reveal'], help='Action to perform: "anonymize" or "reveal".')
    parser.add_argument('input_csv', help='Input CSV file.')
    parser.add_argument('output_csv', help='Output CSV file.')
    parser.add_argument('-schema', required=True, help='YAML file containing data schema.')
    parser.add_argument('-key', help='Secret key file for encryption/decryption.')
    parser.add_argument('-disable-simhash', action='store_true', help='Disable Simhash enrichment.')

    args = parser.parse_args()

    if args.action == 'reveal':
        if args.key is None:
            print("Error: Secret key file is required for de-anonymization.")
            return

    if args.key is None:
        key, salt = generate_key()
        with open('key.secret', 'wb') as key_file:
            key_file.write(key)
        print("Secret key generated and saved as 'key.secret'. Please keep it secure.")
    else:
        with open(args.key, 'rb') as key_file:
            key = key_file.read()

    if args.action == 'anonymize':
        enrich_simhash = not args.disable_simhash
        anonymize(args.input_csv, args.output_csv, args.schema, key, enrich_simhash)
    elif args.action == 'reveal':
        reveal(args.input_csv, args.output_csv, args.schema, key)

if __name__ == '__main__':
    main()