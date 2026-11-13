import flet as ft

from components.navigation.navbar import Navbar
from components.pages.main_page import MainPage


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


# ==========================================
# Melhorias na Home
# ==========================================
# 1. Adicionar da badge de verificado (nao importante)
#
# 2. Criar template para tweets
# - baixar imagem e texto
# - baixar comentarios em txt
#
# 3. Criar template para Mercado Livre
# - Extrair principais dados
# - baixar html ou salvar dados em txt
# 
# 4. Colocar um botão para baixar as infos e thumb do video manualmente por item
#
# 5. Adicionar filtro por tags
#
# 6. Corrigir a barra de navegação, tipo: 1 10 20 ... 23 24 25 ... 30 40 43
#
# 7. Mostar a quantidade total de itens na parte superior proximo à barra de 
#
# 8. Apagar thumb(e dados) de itens excluidos no banco
# 
# 9. Colocar o link do canal na foto do Card
# 
# ok 10. Alterar o tamanho da thumb baixada (720p)


# ==========================================
# Melhorias no grupo
# ==========================================
# 1. Personalizar capa
#
# 2. Colocar icone e qtd de itens na capa
#
# 3. Adição de links individuais.
#
# 4. Reorganizar a ordem do itens.
#
# 5. Remover itens.
#
# 6. Marcar como visto.
#
# 7. Mover para o grupo X.
# 
# 8. Mover para a home.


# ==========================================
# Melhorias na tela de importação de arquivos dos grupos
# ==========================================
# 1. Permitir a importação de itens duplicados
# - Atualizar as tags de itens duplicados
#
# 2. Importar um arquivo e excluir o conteudo já presente em outro grupo
# ex: Grupo1 tem videos sobre programação, quero impotar um arquivo de todas as abas do chrome
# para o grupo2, menos os videos sobre programação. Teria um botão de opções avançadas, com a
# opção "remover conteudo já presente nos grupos: selecionar grupos".
#
# 3. Permitir criação de novas Tags na tela de Editar Tags


# ==========================================
# Melhorias na tela adicionar um link
# ==========================================
# 1. Buscar as info da net ao colar um link na pagina de adicionar Tabs


# ==========================================
# Melhorias na tela gerenciamento da fila de Downloads
# ==========================================
# 1. Deixar mais com cara de gerenciamentos de downsloads gerais.
#
# 2. Adicionar registro dos downloads de thumbs faltantes.
#
# 3. Adicionar um botão de baixar/carregar infos em cada Card, para não iniciar um lista gigante automaticamente.
# - Poder selecinar os items de uma pagina (home e grupo), e ao selecionar tem um botão de opções com
#   a opção de baixar todos itens selecionados.
#
# 4. Atualizar o titulo do itens concluidos da fila. Atualmente se colocar um link manualmente, e depois baixar ele
#    fica como titulo o link.


# ==========================================
# Melhorias na arquitetura
# ==========================================
# 1. Adicionar Podcasts via RSS.
#
# 2. Adicionar sistema de Backup.
#
# 3. Substituir Tabs e Videos por group_item, ou vice versa.


#alterações
#TODO: alterar o deletar tag, para ter uma mensagem desejando altera todos os registros de tabs, ou apenas remover sem altera o banco
#TODO: Ao clicar em uma tag no gerenciador de tags, abrir a pagina filtrando videos com aquela tag


# ==========================================
# Melhorias sugeridas pelo gpt
# ==========================================
# ok 1. Gerenciamento da fila de carregamento
# ok - Exibir vídeos aguardando carregamento.
# ok - Mostrar quais estão sendo processados.
# ok* - Criar uma forma de iniciar e controlar a fila manualmente.
# - Permitir tentar novamente os itens que falharam.
# - Criar botão no Card para enviar para a fila.
# - Permitir exclusão individual dos item concluidos e falhados.
#
# ok 2. Suporte a outros tipos de mídia
# ok - Outros conteúdos salvos por URL.
# - Shorts
# - Youtube Channel
# - Podcasts.
# - Sites e artigos.
# - Tweets e publicações.
# - Anuncios do Mercado Livre.
# 
# 3. Melhorias na Home
# - Filtros por tipo de mídia.
# - Ordenação por visualizações, data e prioridade.
# - Melhorias na pesquisa.
# - Filtros mais avançados por tags.
#
# 4. Melhorias na gestão dos grupos
# - Reordenar itens.
# - Mover itens entre grupos.
# - Melhorar as opções do menu de cada card.
# - Permitir editar informações dos itens.
#
# 5. Revisão e estabilidade
# - Corrigir suporte a URLs youtu.be.
# - Revisar Tab.from_dict().
# - Revisar cache e sincronização entre Home e grupos.
# - Melhorar tratamento de erros.
