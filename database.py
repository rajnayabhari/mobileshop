import psycopg2
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    return psycopg2.connect(
    #for local
        database="mobile_shop",
        user="postgres",
        password="@hybesty123",
        host="localhost",
        port=5432
    )

def database():
    email='ishan@gmail.com'       
    password='admin'
    username='ishan'
    contact='9860014276'
    address='bhaktapur'
    hashed_password = hash_password(password)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS credential(
            USER_ID SERIAL PRIMARY KEY NOT NULL,
            USERNAME VARCHAR(250) NOT NULL,
            EMAIL VARCHAR(250) NOT NULL UNIQUE,
            PASSWORD VARCHAR(250) NOT NULL,
            Contact varchar(15) not null,
            address varchar(200) not null,
            ROLE VARCHAR(250) NOT NULL
            );
            INSERT INTO credential (username, password, email, role,contact,address)
            SELECT %s, %s, %s, %s,%s,%s
            WHERE NOT EXISTS (
                SELECT 1 FROM credential WHERE email = %s
            );
            """,
            (username, hashed_password, email, "admin", contact, address, email),
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2) NOT NULL,
                    stock INTEGER NOT NULL,
                    image_filename TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        conn.commit()
