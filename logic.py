import database
from models import Categoria, Produto

class Catalogo:
    def __init__(self):
        self.conn, self.cursor = database.conectar_bd()
        if self.conn and self.cursor:
            database.criar_tabela_categorias(self.conn, self.cursor)
            database.criar_tabela_produtos(self.conn, self.cursor)

    def criar_categoria(self, nome_categoria):
        return database.inserir_categoria(self.conn, self.cursor, nome_categoria)
    
    #dados do produto é um dict 
    def criar_produto(self, nome_categoria, dados_do_produto):
        id_categoria = database.inserir_categoria(self.conn, self.cursor, nome_categoria)
        if id_categoria is None:
            print("❌ Falha ao obter ID da categoria. O produto não será adicionado.")
            return None
        dados_do_produto['categoria_id'] = id_categoria
        id_novo_produto = database.inserir_produto(self.conn, self.cursor, dados_do_produto)
        return id_novo_produto

    def listar_todas_as_categorias(self):
        categorias_tuplas = database.buscar_todas_categorias(self.conn, self.cursor)
        lista_de_objetos = []
        for tupla in categorias_tuplas:
            categoria_objeto = Categoria(id=tupla[0], nome=tupla[1])
            lista_de_objetos.append(categoria_objeto)
        return lista_de_objetos

    def listar_categorias_por_filtro(self, filtro):
        categorias_tuplas = database.buscar_categoria_por_filtro(self.conn, self.cursor, filtro)
        lista_de_objetos = []
        for tupla in categorias_tuplas:
            categoria_objeto = Categoria(id=tupla[0], nome=tupla[1])
            lista_de_objetos.append(categoria_objeto)
        return lista_de_objetos

    def listar_todos_os_produtos(self):
        produtos_tuplas = database.buscar_todos_produtos(self.conn, self.cursor)
        lista_de_objetos = []
        for tupla in produtos_tuplas:
            produto_objeto = Produto(id=tupla[0], nome=tupla[1], descricao=tupla[2], preco=tupla[3], estoque=tupla[4], categoria_id=tupla[5], nome_categoria=tupla[6])
            lista_de_objetos.append(produto_objeto)
        return lista_de_objetos

    def listar_produtos_por_filtro(self, filtro):
        produtos_tuplas = database.buscar_produtos_por_filtro(self.conn, self.cursor, filtro)
        lista_de_objetos = []
        for tupla in produtos_tuplas:
            produto_objeto = Produto(id=tupla[0], nome=tupla[1], descricao=tupla[2], preco=tupla[3], estoque=tupla[4], categoria_id=tupla[5], nome_categoria=tupla[6])
            lista_de_objetos.append(produto_objeto)
        return lista_de_objetos

    def atualizar_categoria(self, id_busca, novos_dados={}):
        return database.atualizar_categoria(self.conn, self.cursor, id_busca, novos_dados)

    def atualizar_produto(self, id_busca, novos_dados={}):
        return database.atualizar_produto(self.conn, self.cursor, id_busca, novos_dados)

    def deletar_categoria(self, id_busca):
        return database.deletar_categoria(self.conn, self.cursor, id_busca)

    def deletar_produto(self, id_busca):
        return database.deletar_produto(self.conn, self.cursor, id_busca)

    def fechar_conexao(self):
        self.cursor.close()
        self.conn.close()