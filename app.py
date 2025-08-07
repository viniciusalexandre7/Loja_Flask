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

@app.route("/api/categorias", methods=['GET'])
def api_listar_categorias():
    lista_objetos_categorias = catalogo.listar_todas_as_categorias()
    categoria_em_dict = [categoria.to_dict() for categoria in lista_objetos_categorias]
    return jsonify(categoria_em_dict)

@app.route("/api/categorias/<int:categoria_id>", methods=['GET'])
def api_listar_categoria_por_id(categoria_id):
    categoria_id = {"id": categoria_id}
    id_buscado = catalogo.listar_categorias_por_filtro(categoria_id)
    categoria_em_dict = [categoria.to_dict() for categoria in id_buscado]
    if categoria_em_dict:
        return jsonify(categoria_em_dict)
    else:
        return jsonify({"erro": "Categoria não encontrada"}), 404

@app.route("/api/categorias/<int:categoria_id>/produtos", methods=["GET"])
def api_listar_categoria_por_id_com_produtos(categoria_id):
    categoria_buscada = catalogo.listar_categorias_por_filtro({'id': categoria_id})

    if not categoria_buscada:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    else:
        categoria = categoria_buscada[0].to_dict()
        produtos = catalogo.listar_produtos_por_filtro({'categoria_id': categoria_id})
        produtos_em_dict = [produto.to_dict() for produto in produtos]
        categoria['produtos'] = produtos_em_dict
        return jsonify(categoria), 200

#===== POST =====

@app.route("/api/categorias", methods=['POST'])
def api_adicionar_categoria():
    dados_recebidos = request.json
    nome_categoria = dados_recebidos.get('nome', '').strip().lower()

    if not nome_categoria:
        return jsonify({"erro": "Campo 'nome' da categoria é obrigatório."}), 400

    buscar_categoria = catalogo.listar_categorias_por_filtro({'nome':nome_categoria})
    if buscar_categoria:
        return jsonify({"erro": f"Falha ao criar a categoria. a Categoria '{nome_categoria}' já existe."}), 400

    id_da_categoria = catalogo.criar_categoria(nome_categoria)
    if id_da_categoria:
        id = {'id': id_da_categoria}
        categoria_criada = catalogo.listar_categorias_por_filtro(id)
        if categoria_criada:
                return jsonify({"mensagem": "Categoria criada com sucesso!","categoria":categoria_criada[0].to_dict(), 'url': f"/api/categorias/{id_da_categoria}"}), 201
        else:
            return jsonify({"erro": "Categoria criado, mas falha ao recuperar os dados."}), 500
    else:
        return jsonify({"erro": "Não foi possível criar a categoria. Verifique se ela já existe ou tente novamente mais tarde."}), 400

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

    buscar_produto = catalogo.listar_produtos_por_filtro({'nome': dados_recebidos['nome'],
        'descricao': dados_recebidos['descricao']})
    if buscar_produto:
        return jsonify({"erro": f"Falha ao criar o produto. O Produto '{dados_recebidos['nome']}' já existe."}), 400

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

@app.route("/api/categorias/<int:categoria_id>", methods=['PUT'])
def api_atualizar_categoria(categoria_id):
    dados_recebidos = request.json
    nome_categoria = dados_recebidos.get('nome', '').strip().lower()

    if not nome_categoria:
        return jsonify({"erro": "Campo 'nome' da categoria é obrigatório."}), 400

    buscar_categoria = catalogo.listar_categorias_por_filtro({'id': categoria_id})
    if not buscar_categoria:
        return jsonify({"erro": "Categoria não encontrado"}), 404

    dados_atualizados = catalogo.atualizar_categoria(categoria_id, {'nome':nome_categoria})
    if dados_atualizados is not None:
        categoria_recarregada = catalogo.listar_categorias_por_filtro({'id': categoria_id})
        if dados_atualizados > 0:
            return jsonify({"mensagem": "Categoria atualizado com sucesso!","produto":categoria_recarregada[0].to_dict(), 'url': f"/api/categorias/{categoria_id}"}), 200
        else:
            return jsonify({"mensagem": "Nenhuma alteração foi feita. Os dados já estavam atualizados.","produto":categoria_recarregada[0].to_dict(), 'url': f"/api/categorias/{categoria_id}"}), 200
    else:
        return jsonify({"erro": "Erro ao atualizar a categoria."}), 500

@app.route("/api/produtos/<int:produto_id>", methods=['PUT'])
def api_atualizar_produto(produto_id):
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

@app.route("/api/categorias/<int:categoria_id>", methods=['DELETE'])
def api_deletar_categoria(categoria_id):
    buscar_categoria = catalogo.listar_categorias_por_filtro({'id': categoria_id})
    if not buscar_categoria:
        return jsonify({"erro": "Categoria não encontrado"}), 404
    try:
        resultado = catalogo.deletar_categoria(categoria_id)
        if resultado:
            return jsonify({"mensagem": f"Categoria '{buscar_categoria[0].nome}' deletada com sucesso"}), 200
        else:
            return jsonify({"erro": "Falha ao deletar a Categoria. Nenhuma linha foi afetada."}), 400
    except Exception as erro:
        return jsonify({"erro": f"Erro interno ao tentar deletar: {str(erro)}"}), 500


@app.route("/api/produtos/<int:produto_id>", methods=['DELETE'])
def deletar_produto(produto_id):
    buscar_produto = catalogo.listar_produtos_por_filtro({'id': produto_id})
    if not buscar_produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    try:
        resultado = catalogo.deletar_produto(produto_id)
        if resultado:
            return jsonify({"mensagem": "Produto deletado com sucesso"}), 200
        else:
            return jsonify({"erro": "Falha ao deletar o produto. Nenhuma linha foi afetada."}), 400
    except Exception as erro:
        return jsonify({"erro": f"Erro interno ao tentar deletar: {str(erro)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)
