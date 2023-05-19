"""
Anonymizes/De-anonymizes a CSV file based on a provided YAML schema.
"""
import argparse
import yaml
from cryptography.fernet import Fernet
import pandas as pd
from simhash import Simhash


def generate_key() -> bytes:
    """Generates a Fernet key for encryption/decryption

    Returns:
        bytes: the generated Fernet key
    """
    return Fernet.generate_key()


def anonymize(input_csv_path: str, output_csv_path: str,
               schema_yaml_path: str, key: bytes, enrich_simhash: bool = True) -> None:
    """Anonymizes a CSV file based on a provided YAML schema.

    By default, enriches each PII column with a simhash value. 
    This can be disabled by setting enrich_simhash to False.

    The simhash enrichments creates a new column that has _simash appended 
    to the original column name. For example, if the original column name 
    is "email", the new column name will be "email_simhash".


    Args:
        input_csv_path (str): path for input csv file
        output_csv_path (str): path for output csv file
        schema_yaml_path (str): path for input schema
        key (bytes): Fernet key for encryption
        enrich_simhash (bool, optional): whether to enrich PII columns with Simhash values. 
            Defaults to True.
    """

    # Load YAML schema file
    with open(schema_yaml_path, 'r', encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    input_df = pd.read_csv(input_csv_path)

    # Initialize the fernet class
    fernet = Fernet(key)

    for column in input_df.columns:
        # If the column is PII, encrypt it
        if schema[column]['pii']:
            if enrich_simhash:
                # Add a simhash column for each column to enrich it
                input_df[f'{column}_simhash'] = input_df[column].apply(
                    lambda x: str(Simhash(x).value))
            # Encrypt the column
            input_df[column] = input_df[column].apply(lambda x: fernet.encrypt(x.encode()).decode())

    input_df.to_csv(output_csv_path, index=False)


def reveal(input_csv, output_csv, schema_yaml, key) -> None:
    """De-anonymizes the CSV file based on a provided YAML schema.

    Note that this will ignore any column that ends in _simhash.
    This is because the _simhash columns are only used for
    enrichment and are not part of the original data.

    Args:
        input_csv (str): path for input csv file
        output_csv (str): path for output csv file that's been de-anonymized
        schema_yaml (str): _description_
        key (bytes): Fernet key for decryption
    """

    # Load YAML schema file
    with open(schema_yaml, 'r', encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    input_df = pd.read_csv(input_csv)

    # Initialize the fernet class
    fernet = Fernet(key)

    for column in input_df.columns:
        # If the column is PII, decrypt it
        # If it ends in "_simhash", remove it
        if not (column.endswith("_simhash")) and schema[column]['pii']:
            input_df[column] = input_df[column].apply(lambda x: fernet.decrypt(x.encode()).decode())

    input_df.to_csv(output_csv, index=False)

def main():
    """Main function for command line usage.
    """
    parser = argparse.ArgumentParser(description='Anonymize/reveal a CSV file based on \
        a provided YAML schema.')
    parser.add_argument('action', choices=['anonymize', 'reveal'],
                        help='Action to perform: "anonymize" or "reveal".')
    parser.add_argument('input_csv',
                        help='Input CSV file.')
    parser.add_argument('output_csv',
                        help='Output CSV file.')
    parser.add_argument('-schema', required=True,
                        help='YAML file containing data schema.')
    parser.add_argument('-key', help='Secret key file for encryption/decryption.')
    parser.add_argument('-disable-simhash', action='store_true',
                        help='Disable Simhash enrichment.')

    args = parser.parse_args()

    if args.action == 'reveal':
        if args.key is None:
            print("Error: Secret key file is required for de-anonymization.")
            return

    if args.key is None:
        key= generate_key()
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
