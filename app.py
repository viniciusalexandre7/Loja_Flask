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
    campos_obrigatorios = set(['nome', 'descricao', 'preco', 'estoque', 'nome_categoria'])
    faltando = campos_obrigatorios - set(dados_recebidos.keys())
    if faltando:
        return jsonify({"erro": f"Campos ausentes: {', '.join(faltando)}"}), 400

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

#===== PUT =====

@app.route("/api/produtos/<int:produto_id>", methods=['PUT'])
def atualizar_produto(produto_id):
    dados_recebidos = request.json
    colunas_permitidas = set(["descricao", "estoque", "nome", "nome_categoria", "preco"])
    novos_dados = {}

    for chave, valor in dados_recebidos.items():
        if chave in colunas_permitidas and valor is not None:
            novos_dados[chave] = valor

    buscar_produto = catalogo.listar_produtos_por_filtro({'id': produto_id})

    if not buscar_produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados_atualizados = catalogo.atualizar_produto(produto_id, novos_dados)

    if dados_atualizados is not None:
        produto_recarregado = catalogo.listar_produtos_por_filtro({'id': produto_id})
        if dados_atualizados > 0:
            return jsonify({"mensagem": "Produto atualizado com sucesso!","produto":produto_recarregado[0].to_dict(), 'url': f"/api/produtos/{produto_id}"}), 200
        else:
            return jsonify({"mensagem": "Nenhuma alteração foi feita. Os dados já estavam atualizados.","produto":produto_recarregado[0].to_dict(), 'url': f"/api/produtos/{produto_id}"}), 200
    else:
        return jsonify({"erro": f"Falha ao atualizar o produto, revise os dados antes de enviar."}), 400

#===DELETE===

@app.route("/api/produtos/<int:produto_id>", methods=['DELETE'])
def deletar_produto(produto_id):
    dados_recebidos = request.json
    buscar_produto = catalogo.listar_produtos_por_filtro({'id': produto_id})

    if not buscar_produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    try:
        apagar_produto = catalogo.deletar_produto(produto_id)
        if apagar_produto:
            return jsonify({"mensagem": "Produto deletado com sucesso"}), 200
        else:
            return jsonify({"erro": "Falha ao deletar o produto. Nenhuma linha foi afetada."}), 400
    except Exception as erro:
        return jsonify({"erro": f"Erro interno ao tentar deletar: {str(erro)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)
