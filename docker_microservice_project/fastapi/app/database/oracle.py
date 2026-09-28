import oracledb

def get_connection():
    return oracledb.connect(
        user="omsdb",
        password="omsdb",
        dsn="164.68.124.251:1521/pdb_ukm"
    )