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
                nome VARCHAR(100) NOT NULL UNIQUE,
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

def inserir_categoria(conn, cursor, nome_da_categoria):
    try:

        cursor.execute("SELECT id FROM categorias WHERE nome = %s",(nome_da_categoria,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]

        cursor.execute("""INSERT INTO categorias (nome) VALUES (%s)""", (nome_da_categoria,))
        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao inserir categoria '{nome_da_categoria}':", e)
        return None

def inserir_produto(conn, cursor, tabela, dados_do_produto):

    if not dados_do_produto:
            print("❌ Nenhum dado fornecido para inserção.")
            return None

    try:
        nome = dados_do_produto.get("nome")
        if nome:
            cursor.execute(
                "SELECT id FROM produtos WHERE nome = %s", (nome,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]

        colunas = ", ".join(dados_do_produto.keys())
        placeholders = ", ".join(["%s"] * len(dados_do_produto))
        valores = tuple(dados_do_produto.values())

        query = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

        cursor.execute(query, valores)
        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao inserir na tabela '{tabela}':", e)
        return None 



if __name__== "__main__":

    produto1 = {
    "nome": "Camisa Polo",
    "descricao": "Camisa de algodão piquet de alta qualidade.",
    "preco": 129.90,
    "estoque": 50,
    "categoria_id": 1
}

    conn, cursor = conectar_bd()
    if conn and cursor:
        # criar_categorias = criar_tabela_categorias(conn, cursor)
        # criar_produtos = criar_tabela_produtos(conn, cursor)
        id_camisa = inserir_categoria(conn, cursor, "Camisas")
        id_bermuda = inserir_categoria(conn, cursor, "Bermudas")

        print(f"ID_Camisa: {id_camisa}")
        print(f"ID_Bermduda: {id_bermuda}")

        adicionar_produto = inserir_produto(conn, cursor, "produtos", produto1)
        print(f"ID_Camisa_Polo: {adicionar_produto}")


        cursor.close()
        conn.close()

        print("\n✅ Conexão com o MySQL fechada.")