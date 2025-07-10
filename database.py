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

def buscar_todas_categorias(conn, cursor):
    try:
        cursor.execute("""SELECT * FROM categorias ORDER BY nome ASC""")
        return cursor.fetchall()

    except Exception as e:
        print(f"❌ Erro ao buscar categorias:", e)
        return None 

def buscar_categoria_por_filtro(conn, cursor, filtros={}):
    # Exemplo de filtros: {'id': 1, 'nome': 'camisas'}
    try:
        query = """
            SELECT c.id, c.nome
            FROM categorias AS c
        """

        clausulas_where = []
        valores = []

        if filtros: 
            for chave, valor in filtros.items():
                if chave == 'id':
                    clausulas_where.append("c.id = %s")
                    valores.append(valor)
                elif chave == 'nome':
                    clausulas_where.append("c.nome LIKE %s")
                    valores.append(f"%{valor}%")

            if clausulas_where:
                query += " WHERE " + " AND ".join(clausulas_where)

        cursor.execute(query, tuple(valores))
        return cursor.fetchall()

    except Error as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        return None

def buscar_todos_produtos(conn, cursor):
    try:
        cursor.execute("""SELECT 
    p.id,
    p.nome AS nome_produto,
    p.descricao,
    p.preco,
    p.estoque,
    c.nome AS nome_categoria
    FROM produtos AS p
    JOIN categorias AS c ON p.categoria_id = c.id""")
        return cursor.fetchall()

    except Exception as e:
        print(f"❌ Erro ao buscar todos os produtos:", e)
        return None 

def buscar_produtos_por_filtro(conn, cursor, filtros={}):
    # Exemplo de filtros: {'nome': 'camisa polo', 'preco_max': 150.00}
    try:
        query = """
            SELECT p.id, p.nome, p.descricao, p.preco, p.estoque, c.nome AS nome_categoria
            FROM produtos AS p
            JOIN categorias AS c ON p.categoria_id = c.id
        """
        clausulas_where = []
        valores = []

        if filtros: 
            for chave, valor in filtros.items():
                if chave == 'id':
                    clausulas_where.append("p.id = %s")
                    valores.append(valor)
                elif chave == 'nome':
                    clausulas_where.append("p.nome LIKE %s")
                    valores.append(f"%{valor}%")
                elif chave == 'categoria':
                    clausulas_where.append("c.nome = %s")
                    valores.append(valor)
                elif chave == 'preco_max':
                    clausulas_where.append("p.preco <= %s")
                    valores.append(valor)
                elif chave == 'preco_min':
                    clausulas_where.append("p.preco >= %s")
                    valores.append(valor)
                elif chave == 'estoque':
                    clausulas_where.append("p.estoque >= %s")
                    valores.append(valor)

            if clausulas_where:
                query += " WHERE " + " AND ".join(clausulas_where)

        cursor.execute(query, tuple(valores))
        return cursor.fetchall()

    except Error as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return None

def atualizar_por_valor_busca(conn, cursor, valor_busca, id_busca, novos_dados={}):

    if None in [valor_busca, id_busca, novos_dados]:
            print("❌ Dados fornecidos para a atualização estão ínvalidos.")
            return None
    try:
        if valor_busca == "produtos":
            tabela = "produtos"
            cursor.execute("SELECT id FROM produtos WHERE id = %s", (id_busca,))
            resultado = cursor.fetchone()

            if not resultado :
                print(f"⚠️ Produto com ID {id_busca} não encontrado.")
                return None

        elif valor_busca == "categorias":
            tabela = "categorias"
            cursor.execute("SELECT id FROM categorias WHERE id = %s", (id_busca,))
            resultado = cursor.fetchone()

            if not resultado :
                print(f"⚠️ Categoria com ID {id_busca} não encontrado.")
                return None

        else:
            print(f"{valor_busca} não encontrado.")
            return

        #aqui um list compresion em que vai interar cada valor dos dados e por um %s de acordo com dado interado, ex: nome = %s, preco_min = %s....
        clausulas_set = ", ".join([f"{coluna} = %s" for coluna in novos_dados.keys()])
        valores = list(novos_dados.values())
        valores.append(id_busca)

        query = f"UPDATE {tabela} SET {clausulas_set} WHERE id = %s"

        cursor.execute(query, tuple(valores))
        conn.commit()
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar os itens: {e}")
        return None


def atualizar_produto(conn, cursor, id_busca, novos_dados={}):

    if not id_busca or not novos_dados:
            print("❌ Dados fornecidos para a atualização estão ínvalidos.")
            return None
    try:
        #aqui um list compresion em que vai interar cada valor dos dados e por um %s de acordo com dado interado, ex: nome = %s, preco_min = %s....
        clausulas_set = ", ".join([f"{coluna} = %s" for coluna in novos_dados.keys()])
        valores = list(novos_dados.values())
        valores.append(id_busca)

        query = f"UPDATE produtos SET {clausulas_set} WHERE id = %s"

        cursor.execute(query, tuple(valores))
        conn.commit()
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar os itens: {e}")
        return None

def atualizar_categoria(conn, cursor, id_busca, novos_dados={}):

    if not id_busca or not novos_dados:
            print("❌ Dados fornecidos para a atualização estão ínvalidos.")
            return None
    try:
        #aqui um list compresion em que vai interar cada valor dos dados e por um %s de acordo com dado interado, ex: nome = %s, preco_min = %s....
        clausulas_set = ", ".join([f"{coluna} = %s" for coluna in novos_dados.keys()])
        valores = list(novos_dados.values())
        valores.append(id_busca)

        query = f"UPDATE categorias SET {clausulas_set} WHERE id = %s"

        cursor.execute(query, tuple(valores))
        conn.commit()
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar os itens: {e}")
        return None

def deletar_por_valor_busca(conn, cursor, valor_busca, id_busca):

    if None in [valor_busca, id_busca]:
            print("❌ Dados fornecidos para a exclusão estão ínvalidos.")
            return None
    try:
        if valor_busca == "produtos":
            tabela = "produtos"
            cursor.execute("SELECT id FROM produtos WHERE id = %s", (id_busca,))
            resultado = cursor.fetchone()

            if not resultado :
                print(f"⚠️ Produto com ID {id_busca} não encontrado.")
                return None
        elif valor_busca == "categorias":
            tabela = "categorias"
            cursor.execute("SELECT id FROM categorias WHERE id = %s", (id_busca,))
            resultado = cursor.fetchone()

            if not resultado :
                print(f"⚠️ Categoria com ID {id_busca} não encontrado.")
                return None
        else:
            print(f"{valor_busca} não encontrado.")
            return

        query = f"DELETE FROM {tabela} WHERE id = %s"

        cursor.execute(query, (id_busca,))
        conn.commit()

        print(f"✅ {valor_busca.capitalize()} com ID {id_busca} deletado com sucesso.")
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao deletar os itens: {e}")
        return None

def deletar_produto(conn, cursor, id_busca):

    if not id_busca:
        print("❌ Dados fornecidos para a exclusão estão ínvalidos.")
        return None

    try:
        query = f"DELETE FROM produtos WHERE id = %s"
        cursor.execute(query, (id_busca,))
        conn.commit()
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao deletar os itens: {e}")
        return None

def deletar_categoria(conn, cursor, id_busca):

    if not id_busca:
        print("❌ Dados fornecidos para a exclusão estão ínvalidos.")
        return None

    try:
        query = f"DELETE FROM categorias WHERE id = %s"
        cursor.execute(query, (id_busca,))
        conn.commit()
        return cursor.rowcount

    except Error as e:
        conn.rollback()
        print(f"❌ Erro ao deletar os itens: {e}")
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
        buscar_categorias = buscar_todas_categorias(conn, cursor)
        buscar_produtos = buscar_todos_produtos(conn, cursor)
        # print(buscar_categorias)
        # print(buscar_produtos)
        buscar_categorias_filtro = buscar_categoria_por_filtro(conn, cursor, filtros={"nome": 'bermudas',})
        print(buscar_categorias_filtro)
        buscar_produto_filtro = buscar_produtos_por_filtro(conn, cursor, filtros={"nome":"camisa", "preco_max":130})
        print(buscar_produto_filtro)

        cursor.close()
        conn.close()

        print("\n✅ Conexão com o MySQL fechada.")