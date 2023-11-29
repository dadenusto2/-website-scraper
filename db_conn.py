import psycopg2
conn = psycopg2.connect(dbname='postgres', user='postgres',
                        password='docker', host='localhost', port='543')
cursor = conn.cursor()