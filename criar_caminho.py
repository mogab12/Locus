import networkx as nx
from PIL import Image, ImageDraw




# Criar um grafo com nós e arestas (representando interseções e caminhos)
grafo = nx.Graph()

#criado o grafo:
        # Nós:

grafo.add_node("A", pos=(100, 150))
grafo.add_node("B", pos=(200, 250))
grafo.add_node("C", pos=(300, 350))
grafo.add_node("D", pos=(400, 300))


        # Arestas:
grafo.add_edge("A", "B", weight=5)
grafo.add_edge("B", "C", weight=3)
grafo.add_edge("A", "C", weight=10)
grafo.add_edge("C", "D", weight=4)

#criando destino X origem:

origem = "A"
destino = "D"

#Aplicando o algoritimo Dijkstra:

caminho_mais_curto = nx.shortest_path(grafo, source=origem, target=destino, weight='weight')



# Carregar a imagem do mapa
mapa = Image.open("mapa.png")  # Substitua pelo caminho da sua imagem

# Criar uma interface de desenho sobre a imagem
desenho = ImageDraw.Draw(mapa)

# Obter as coordenadas dos nós no caminho mais curto
coordenadas_caminho = [grafo.nodes[nodo]["pos"] for nodo in caminho_mais_curto]

# Desenhar o caminho como uma linha sobre o mapa
cor_linha = (255, 0, 0)  # Vermelho
largura_linha = 5
desenho.line(coordenadas_caminho, fill=cor_linha, width=largura_linha)

# Salvar e exibir a imagem com o caminho desenhado
mapa.save("mapa_com_caminho.png")
mapa.show()

