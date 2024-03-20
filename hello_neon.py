import psycopg2

conn_str = "postgresql://neondb_owner:4slSQ8XqNYxm@ep-sweet-mode-a2vbydq9.eu-central-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(conn_str)

with conn.cursor() as cur:
 cur.execute("SELECT 'hello neon';")
 print(cur.fetchall())