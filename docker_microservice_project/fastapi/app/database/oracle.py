import oracledb

def get_connection():
    return oracledb.connect(
        user="omsystem",
        password="12345",
        dsn="192.168.66.21:1521/oms_pdb"
    )