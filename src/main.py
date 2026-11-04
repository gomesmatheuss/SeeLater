import flet as ft
from components.navbar import Navbar
from components.main_page import MainPage

def main(page: ft.Page):
    page.title = "SeeLater"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.ON_SECONDARY

    page.window.width = 1080
    page.window.height = 720
    page.window.min_width = 480

    page.add(
        Navbar(),
        MainPage(page)
    )

ft.app(main)


#TODO: Criar template para tweets
    #TODO: baixar imagem e texto
    #TODO: baixar comentarios em txt
#TODO: Criar template para Mercado Livre
    #TODO: Extrair principais dados
    #TODO: baixar html ou salvar dados em txt

#ok - TODO: Ajeitar os textos do Card
    #ok - TODO: Trocar fonte
    #ok - TODO: Ajeitar espaço do titulo
    #ok - TODO: Adicionar tooltip no titulo
#ok - TODO: Ajeitar a posição da imagem do canal no Card
#ok - TODO: Adicionar data de upload no Card
#TODO: Adicionar da badge de verificado (nao importante)
#ok - TODO: Formatar as visualizações, ex: 3M 1B 900 mil (nao importante)

#ok - TODO: Alterar os index do link em Tabs no Mongo
#ok - TODO: Resolver problemas de links duplicados

#ok - TODO: Criar tela de confirmação ao inportar .json, listando a qtd total de itens, item validos, e listar todos com uma caixa de seleção
    #TODO: Selecionar e desselecionar todos os item de uma vez
    #TODO: Contador de items selecionados
    #TODO: Tela de adicionar tags
    #ok - TODO: Salvar no MongoDB

    #TODO: Mostrar itens duplicados
    #TODO: Atualizar as tags de itens duplicados

#ok - TODO: Criar o molde do video não carregado (thumb), com titulo - add status no mongo
    #TODO: Colocar um botão para baixar as infos e thumb do video
    #TODO: Baixar as info de forma asyncrona


#ok - TODO: Adicionar barra de pesquisa
    #TODO: Filtrar por tags
#ok - TODO: Adicionar paginação
    #TODO: Trocar a barra de navegação por algo mais organizado, tipo 1 ... 3 4 5 6 7 ... 10 20 30 33
    #TODO: Mostar a quantidade total de itens
#TODO: Editar os Cards

#TODO: Ao dar update no grid, verificar itens para apagar(thumb) e baixar

#TODO: Adicionar as tags no Card do video
#TODO: Adicionar categorias no menu lateral
#TODO: Filtrar por categorias, tags
#TODO: Botão para copiar o link do video
#ok - TODO: Adicionar tamanho do video no Card

#TODO: Pegar as infos do canal
#ok - TODO: Colocar a foto do canal no Card
#TODO: Colocar o link do canal na foto do Card
#TODO: Colocar um contador com a quantidade total de Tabs

#ok - TODO: Alterar o tamanho da thumb baixada
#TODO: Remover thumbs de videos assistidos/deletados

#TODO: Criar tabela com tags
#TODO: Trocar input das tags para um combobox
#ok - TODO: Buscar as info da net ao colar um link na pagina de adicionar Tabs

#TODO: Adicionar Podcasts via RSS


#alterações
#TODO: alterar o deletar tag, para ter uma mensagem desejando altera todos os registros de tabs, ou apenas remover sem altera o banco
#TODO: Ao clicar em uma tag no gerenciador de tags, abrir a pagina filtrando videos com aquela tag
