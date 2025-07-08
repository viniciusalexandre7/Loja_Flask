import mysql.connector
from mysql.connector import errorcode, Error


def conectar_bd():
    try:
       conn = mysql.connector.connect(
        host="localhost",    
        user="vinicius",  
        password="1234567890",
        database="loja_db",
        auth_plugin="mysql_native_password",
        )

       if conn:
        print("✅ Conexão bem sucedida")
        cursor = conn.cursor()
        return conn, cursor

    except Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Usuário ou senha inválidos")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ O banco de dados não existe")
        else:
            print(f"❌ Erro ao conectar no banco de dados: {e}")
        return None, None

def criar_tabela_categorias(conn, cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE
            );
        """)

        conn.commit()
        print("🛠️ Tabela 'categorias' criada com sucesso!")

    except Exception as e:
        conn.rollback()
        print("❌ Erro ao criar tabela:", e)

def criar_tabela_produtos(conn, cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco DECIMAL(10, 2) NOT NULL,
                estoque INT NOT NULL,
                categoria_id INT,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        print("🛠️ Tabela 'produtos' criada com sucesso!")

    except Exception as e:
        conn.rollback()
        print("❌ Erro ao criar tabela:", e)

if __name__== "__main__":

    conn, cursor = conectar_bd()
    if conn and cursor:
        criar_categorias = criar_tabela_categorias(conn, cursor)
        criar_produtos = criar_tabela_produtos(conn, cursor)

        cursor.close()
        conn.close()

        print("\n✅ Conexão com o MySQL fechada.")