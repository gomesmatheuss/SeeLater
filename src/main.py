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


#ok - TODO: Ajeitar os textos do Card
    #ok - TODO: Trocar fonte
    #ok - TODO: Ajeitar espaço do titulo
#ok - TODO: Ajeitar a posição da imagem do canal no Card
#ok - TODO: Adicionar data de upload no Card
#TODO: Adicionar da badge de verificado (nao importante)
#TODO: Formatar as visualizações, ex: 3M 1B 900 mil (nao importante)

#TODO: Criar o molde do video não carregado (thumb), com titulo - add status no mongo
#TODO: Colocar um botão para baixar as infos e thumb do video
#TODO: Baixar as info de forma asyncrona
#TODO: Adicionar as tags no Card do video
#TODO: Adicionar barra de pesquisa
#TODO: Adicionar paginação
#TODO: Adicionar categorias no menu lateral
#TODO: Filtrar por categorias, tags
#TODO: Botão para copiar o link do video
#TODO: Adicionar tamanho do video no Card

#TODO: Pegar as infos do canal
#TODO: Colocar a foto do canal no Card
#TODO: Colocar o link do canal na foto do Card
#TODO: Colocar um contador com a quantidade total de Tabs

#TODO: Resolver problemas de links duplicados
#TODO: Alterar os index do link em Tabs no Mongo

#TODO: Alterar o tamanho da thumb baixada
#TODO: Remover thumbs de videos assistidos/deletados

#TODO: Criar tela de confirmação ao inportar .json, listando a qtd total de itens, item validos, e listar todos com uma caixa de seleção

