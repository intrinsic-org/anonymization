# Anonymization Library

This Library provides a set of functions for anonymizing, de-anonymizing, and enriching personally identifiable information (PII) in CSV files based on a provided YAML schema.

The anonymization works by encrypting each row with a supplied cryptographic key (or one generated through the script). We also enrich the CSV with a simhash column to allow for searching and matching of anonymized data.

## Installation

To install the anonymization library from source, run the following commands
to setup a virtual environment and install the library:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CLI Usage

To anonymize a CSV file, use the following command:

```shell
python anonymize.py anonymize example.csv example_anonymized.csv -schema example_schema.yaml -key key.secret
```

Replace `example.csv` with the path to your input CSV file, `example_anonymized.csv` with the desired path for the anonymized CSV output file, `example_schema.yaml` with the path to your YAML schema file, and `key.secret` with the path to your secret key file.

If key.secret does not exist, a new key will be generated and saved as `key.secret`.

To de-anonymize a previously anonymized CSV file, use the following command:

```shell
python anonymize.py reveal example_anonymized.csv example_revaled.csv -schema example_schema.yaml -key key.secret
```

Replace `example_anonymized.csv` with the path to your input CSV file, `example_revaled.csv` with the desired path for the de-anonymized CSV output file, `example_schema.yaml` with the path to your YAML schema file, and `key.secret` with the path to your secret key file.

## Schema File

The YAML schema file defines which columns in the CSV file contain PII. Here's an example schema:

```yaml
column_name:
  pii: true
another_column:
  pii: false
```

In this example, `column_name` is marked as containing PII, while `another_column` is not.

## Enrichments

During the anonymization process, extra columns are added for the PII columns including the simhash. More details on SimHash can be found here: https://en.wikipedia.org/wiki/SimHash.

To disable simhash enrichment, pass `-disable-simhash`

## Secret Key

The secret key is used for encryption and decryption of the PII data. If you don't provide a key file, a new key will be generated and saved as `key.secret`. If you want to use your own key, provide the path to the key file.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
