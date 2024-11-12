from impala.dbapi import connect
import pandas as pd
# import sys

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

# queries using columns:
# name-- company name of opportunity
# stagename-- (0. Downgraded, 7. Closed Won)
sample_opportunities = """
            SELECT name, stagename
            FROM sfdc_production.opportunity
            LIMIT 20
        """

# run queries
cursor.execute(sample_opportunities)
sample = cursor.fetchall()

# sort by stagename
df = pd.DataFrame(sample, columns=pd.Index(["Name", "Stage"]))
downgraded_df = df[df["Stage"] == "0. Downgraded"].sort_values(by="Name")
closed_won_df = df[df["Stage"] == "7. Closed Won"].sort_values(by="Name")

# print results
print("Downgraded Opportunities Table:")
print(downgraded_df)
print("\nClosed Won Opportunities Table:")
print(closed_won_df)


# Close the connection
cursor.close()
conn.close()