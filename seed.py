# seed.py

import asyncio
import random
from datetime import datetime
from faker import Faker

# Importando nossas coleções do banco
from app.core.db import (
    category_collection,
    tag_collection,
    post_collection,
    comment_collection,
    post_tag_collection,
)

# Inicializa o Faker para gerar dados de apoio em português do Brasil
fake = Faker('pt_BR')

# --- CONTEÚDO PRÉ-DEFINIDO E COERENTE (VERSÃO FINAL E EXPANDIDA) ---

CATEGORIES = [
    {"name": "Tecnologia", "description": "Artigos sobre desenvolvimento, gadgets e o futuro da tecnologia."},
    {"name": "Viagens", "description": "Guias, dicas e histórias sobre destinos incríveis."},
    {"name": "Culinária", "description": "Receitas e segredos da gastronomia mundial."},
    {"name": "Esportes", "description": "Análises, notícias e histórias do mundo esportivo."},
    {"name": "Música", "description": "Críticas, lançamentos e a história por trás das canções."}
]

TAGS = [
    # Tecnologia
    {"name": "Python"}, {"name": "FastAPI"}, {"name": "MongoDB"}, {"name": "Docker"},
    # Viagens
    {"name": "Europa"}, {"name": "Praia"}, {"name": "Aventura"},
    # Culinária
    {"name": "Sobremesa"}, {"name": "Massa"}, {"name": "Vegano"},
    # Esportes
    {"name": "Futebol"}, {"name": "Basquete"}, {"name": "Fórmula 1"},
    # Música
    {"name": "Rock"}, {"name": "Pop"}, {"name": "MPB"}
]

AUTHORS = [
    {"name": "Ana Coder", "bio": "Desenvolvedora Python e entusiasta de novas tecnologias."},
    {"name": "Bernardo Viajante", "bio": "Explorador de culturas e paisagens."},
    {"name": "Carla Chef", "bio": "Apaixonada por descobrir novos sabores."},
    {"name": "Daniel Esportivo", "bio": "Jornalista e analista esportivo."},
    {"name": "Elena Melodia", "bio": "Crítica musical e historiadora do rock."}
]

POST_TEMPLATES = [
    # Tecnologia
    {
        "category": "Tecnologia",
        "title": "Primeiros Passos com FastAPI e MongoDB",
        "content": "Neste guia, vamos explorar como iniciar um projeto utilizando a velocidade do FastAPI com a flexibilidade do MongoDB. Abordaremos a configuração inicial, a criação de modelos com Pydantic e a implementação dos primeiros endpoints CRUD."
    },
    {
        "category": "Tecnologia",
        "title": "Otimizando Consultas no MongoDB com Índices",
        "content": "Consultas lentas podem ser um grande gargalo em qualquer aplicação. Aprenda a identificar consultas que precisam de otimização e como usar diferentes tipos de índices no MongoDB para que suas buscas de dados voem."
    },
    {
        "category": "Tecnologia",
        "title": "Deploy de Aplicações FastAPI com Docker",
        "content": "Levar sua aplicação para produção é um passo crucial. Neste tutorial, veremos como containerizar uma API FastAPI usando Docker, garantindo um ambiente consistente e facilitando o deploy em qualquer provedor de nuvem."
    },
    # Viagens
    {
        "category": "Viagens",
        "title": "Um Roteiro de 7 Dias pela Costa Amalfitana",
        "content": "A Costa Amalfitana, na Itália, é um dos destinos mais deslumbrantes do mundo. Prepare-se para um roteiro inesquecível por cidades como Positano, Amalfi e Ravello, com dicas de transporte, gastronomia e os melhores pontos para fotos."
    },
    {
        "category": "Viagens",
        "title": "As Maravilhas Escondidas da Serra Gaúcha",
        "content": "Além de Gramado e Canela, a Serra Gaúcha esconde vales, vinícolas e cidades encantadoras. Explore o Vale dos Vinhedos, conheça a história da imigração italiana e descubra paisagens de tirar o fôlego."
    },
    # Culinária
    {
        "category": "Culinária",
        "title": "O Segredo do Risoto Perfeito: Dicas de um Chef",
        "content": "Fazer um risoto cremoso e no ponto certo é mais fácil do que parece. Aprenda as técnicas essenciais, desde a escolha do arroz até o ponto da 'mantecatura', para impressionar a todos com um prato clássico italiano."
    },
    {
        "category": "Culinária",
        "title": "Como Fazer Massa Fresca em Casa: Guia para Iniciantes",
        "content": "Nada se compara ao sabor de uma massa fresca feita em casa. Com este guia passo a passo, você vai aprender a fazer a massa básica com ovos e a transformá-la em pratos como tagliatelle, ravioli e lasanha."
    },
    # Esportes
    {
        "category": "Esportes",
        "title": "Análise Tática: A Evolução do Meio-Campo Moderno",
        "content": "O futebol moderno exige meio-campistas versáteis. Analisamos como a função evoluiu, desde o clássico 'camisa 10' até os 'box-to-box' de hoje, e o impacto tático que isso tem nas maiores equipes do mundo."
    },
    {
        "category": "Esportes",
        "title": "As Maiores Rivalidades da História da Fórmula 1",
        "content": "De Senna vs. Prost a Hamilton vs. Verstappen, a Fórmula 1 é palco de duelos épicos. Relembramos as disputas mais intensas que marcaram a história do automobilismo, dentro e fora das pistas."
    },
    {
        "category": "Esportes",
        "title": "NBA: Como as Estatísticas Avançadas Mudaram o Jogo",
        "content": "O basquete vai muito além de pontos e rebotes. Entenda como métricas como 'Player Efficiency Rating' (PER) e 'True Shooting Percentage' (TS%) revolucionaram a forma como jogadores e equipes são avaliados."
    },
    # Música
    {
        "category": "Música",
        "title": "A História por Trás do 'The Dark Side of the Moon'",
        "content": "O icônico álbum do Pink Floyd é uma obra-prima conceitual. Mergulhamos nas letras, nos efeitos sonoros e nas histórias de bastidores que fizeram deste um dos álbuns mais importantes de todos os tempos."
    },
    {
        "category": "Música",
        "title": "O Impacto do Samba na Identidade Cultural Brasileira",
        "content": "Mais do que um gênero musical, o samba é um pilar da cultura brasileira. Exploramos suas origens, sua evolução e como ele se tornou um símbolo de resistência e celebração da identidade nacional."
    },
    {
        "category": "Música",
        "title": "Analisando a Genialidade de 'Bohemian Rhapsody'",
        "content": "A obra-prima do Queen quebrou todas as regras da música pop de sua época. Analisamos sua estrutura inovadora, que mistura ópera, balada e hard rock, e o legado que ela deixou para as gerações futuras."
    }
]

async def seed_database():
    print("Iniciando o povoamento TEMÁTICO (versão final) do banco de dados...")

    # --- Limpando coleções antigas ---
    print("Limpando coleções...")
    await asyncio.gather(
        category_collection.delete_many({}), tag_collection.delete_many({}),
        post_collection.delete_many({}), comment_collection.delete_many({}),
        post_tag_collection.delete_many({})
    )

    # --- 1. Criando Categorias e Tags ---
    print("Criando categorias e tags...")
    category_result = await category_collection.insert_many(CATEGORIES)
    tag_result = await tag_collection.insert_many(TAGS)
    
    categories_map = {cat['name']: str(cat_id) for cat, cat_id in zip(CATEGORIES, category_result.inserted_ids)}
    tags_map = {tag['name']: str(tag_id) for tag, tag_id in zip(TAGS, tag_result.inserted_ids)}
    
    print("Categorias e Tags criadas.")

    # --- 2. Criando Posts a partir dos Modelos ---
    # Vamos duplicar os posts para ter mais volume
    all_templates = POST_TEMPLATES * 2 
    print(f"Criando {len(all_templates)} posts temáticos...")
    posts_data = []
    for template in all_templates:
        posts_data.append({
            "title": template["title"],
            "content": template["content"],
            "author": random.choice(AUTHORS),
            "publication_date": fake.date_time_this_year(),
            "category_id": categories_map[template["category"]],
            "tags_id": [str(id) for id in random.sample(list(tags_map.values()), k=random.randint(1, 3))],
            "likes": random.randint(0, 150)
        })
            
    post_result = await post_collection.insert_many(posts_data)
    post_ids = [str(id) for id in post_result.inserted_ids]
    print("Posts criados.")
    
    # --- 3. Criando Comentários ---
    print("Criando 150 comentários...")
    comments_data = []
    for _ in range(150):
        comments_data.append({
            "post_id": random.choice(post_ids),
            "author_name": fake.name(),
            "content": fake.sentence(nb_words=random.randint(5, 15)),
            "creation_date": fake.date_time_this_year()
        })
    await comment_collection.insert_many(comments_data)
    print("Comentários criados.")

    print("\nBanco de dados final populado com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed_database())