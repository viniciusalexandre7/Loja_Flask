from flask import Flask, request, jsonify
from logic import Catalogo
from models import Produto

app = Flask(__name__)
catalogo = Catalogo()

#==== GET ====

@app.route("/api/produtos", methods=['GET'])
def api_listar_produtos():
    lista_objetos_produtos = catalogo.listar_todos_os_produtos()
    produto_em_dict = [produto.to_dict() for produto in lista_objetos_produtos]
    return jsonify(produto_em_dict)

@app.route("/api/produtos/<int:produto_id>", methods=['GET'])
def api_listar_produtos_por_id(produto_id):
    produto_id = {"id": produto_id}
    lista_produto = catalogo.listar_produtos_por_filtro(produto_id)
    produto_em_dict = [produto.to_dict() for produto in lista_produto]
    if produto_em_dict:
        return jsonify(produto_em_dict)
    return jsonify({"erro": "Produto não encontrado"}), 404

#===== POST =====

@app.route('/api/produtos', methods=['POST'])
def api_adicionar_produto():
    dados_recebidos = request.json
    campos_obrigatorios = ['nome', 'descricao', 'preco', 'estoque', 'nome_categoria']
    if not all(campo in dados_recebidos for campo in campos_obrigatorios):
        return jsonify({"erro": "Dados incompletos. Campos obrigatórios: nome, descricao, preco, estoque, nome_categoria"}), 400
    
    nome_categoria = dados_recebidos['nome_categoria']

    dados_do_produto = {
        'nome': dados_recebidos['nome'],
        'descricao': dados_recebidos['descricao'],
        'preco': dados_recebidos['preco'],
        'estoque': dados_recebidos['estoque']
    }

    id_novo_produto = catalogo.adicionar_produto(nome_categoria, dados_do_produto)

    if id_novo_produto:
        id = {'id': id_novo_produto}
        produto_criado = catalogo.listar_produtos_por_filtro(id)
        if produto_criado:
            return jsonify({"mensagem": "Produto criado com sucesso!","produto":produto_criado[0].to_dict(), 'url': f"/api/produtos/{id_novo_produto}"}), 201
        else:
            return jsonify({"erro": "Produto criado, mas falha ao recuperar os dados."}), 500
    else:
        return jsonify({"erro": f"Falha ao criar o produto. A categoria '{nome_categoria}' não foi encontrada. Cadastre-a antes ou use uma categoria já existente."}), 400



if __name__ == '__main__':
    app.run(debug=True)
