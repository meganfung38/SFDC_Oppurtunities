from impala.dbapi import connect
from impala.util import as_pandas
import sys

# Run Instructions:
# 1. enable kerberos client-- kinit megan.fung@ringcentral.com
# 2. create hive ticket-- kinit -S hive/hiveserver.ringcentral.com megan.fung@RINGCENTRAL.COM
# 3. klist to confirm ticket was successfully made
# 4. activate virtual environment-- source .venv/bin/activate
# 5. run script-- python3 SFDC_Data.py

# Create a connection to the Hive cluster
conn = connect(
    host="hiveserver.ringcentral.com",
    port=10000,
    auth_mechanism="GSSAPI",
    user="megan.fung@RINGCENTRAL.COM",
    kerberos_service_name="hive",
)

# # Create a connection to the Impala cluster
# conn = connect(
#     host="impalad.ringcentral.com",
#     port=21050,
#     auth_mechanism="GSSAPI",
#     use_ssl=True,
#     user=[insert username],
#     kerberos_service_name="impala",
# )

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Execute an SQL query
cursor.execute("SELECT sfid, name FROM sfdc_production.latest_account LIMIT 10")

# Fetch and print the results
results = cursor.fetchall()
for row in results:
    print(row)

# Close the connection
cursor.close()
conn.close()