class Categoria:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome

    def __str__(self):
        return f"Categoria: {self.nome}"

    def to_dict(self):
        
        return {
            'id':self.id,
            'nome':self.nome
        }


class Produto:
    def __init__(self, id, nome, descricao, preco, estoque, categoria_id, nome_categoria):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.categoria_id = categoria_id
        self.nome_categoria = nome_categoria

    def __str__(self) -> str:
        return f"id: {self.id} | nome: {self.nome} | descrição: {self.descricao} | preço: {self.preco:.2f}R$ | estoque: {self.estoque} | nome da categoria: {self.nome_categoria}"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "estoque": self.estoque,
            "categoria_id": self.categoria_id,
            "nome_categoria": self.nome_categoria
        }
