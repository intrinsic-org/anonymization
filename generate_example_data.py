"""Example script to generate fake data for the example.
"""

from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Create a Faker instance
fake = Faker()

# Create lists to hold our fake data
emails = [fake.email() for _ in range(100)]
email_domains = [email.split('@')[1] for email in emails]
ip_addresses = [fake.ipv4(network=False) for _ in range(100)]
ages = [fake.random_int(min=20, max=80) for _ in range(100)]

# Make some ip addreses and emails duplicate with each other
ip_addresses[10] = ip_addresses[20]
emails[10] = emails[20]

# Generate random dates within the last month for event_time
start_date = datetime.now() - timedelta(days=30)
event_times = [fake.date_time_between_dates(datetime_start=start_date) for _ in range(100)]

# Create a DataFrame
df = pd.DataFrame({
    'event_time': event_times,
    'email': emails,
    'email_domain': email_domains,
    'ip_address': ip_addresses,
    'age': ages,
})

# Save the DataFrame to a CSV file
df.to_csv('example.csv', index=False)
