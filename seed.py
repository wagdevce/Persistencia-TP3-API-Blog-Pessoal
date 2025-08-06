
import asyncio
import random
from datetime import datetime
from faker import Faker
from bson import ObjectId

# Importando nossas coleções do banco
from app.core.db import (
    category_collection,
    tag_collection,
    post_collection,
    comment_collection,
    post_tag_collection,
    user_collection,
    post_like_collection
)

fake = Faker('pt_BR')

# --- lista de conteudo ---
CATEGORIES = [
    {"name": "Tecnologia", "description": "Artigos sobre desenvolvimento, gadgets e o futuro da tecnologia."},
    {"name": "Viagens", "description": "Guias e dicas para suas próximas aventuras."},
    {"name": "Culinária", "description": "Receitas e segredos da gastronomia mundial."},
    {"name": "Esportes", "description": "Análises, notícias e histórias do mundo esportivo."},
    {"name": "Música", "description": "Críticas, lançamentos e a história por trás das canções."}
]
TAGS = [
    {"name": "Python"}, {"name": "FastAPI"}, {"name": "MongoDB"}, {"name": "Docker"},
    {"name": "Europa"}, {"name": "Praia"}, {"name": "Aventura"},
    {"name": "Sobremesa"}, {"name": "Massa"}, {"name": "Vegano"},
    {"name": "Futebol"}, {"name": "Basquete"}, {"name": "Fórmula 1"},
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
COMMENT_TEMPLATES = [
    "Excelente artigo! Muito bem explicado e direto ao ponto.",
    "Não tinha pensado por esse lado. Ótima perspectiva!",
    "Esse post me ajudou a resolver um problema que estava tendo há dias. Muito obrigado!",
    "Simplesmente incrível! Vou compartilhar com minha equipe agora mesmo.",
    "Adorei as dicas, especialmente a sobre a otimização de índices. Fez toda a diferença.",
    "Você tem a fonte para o dado que citou no terceiro parágrafo? Gostaria de ler mais a respeito.",
    "Conteúdo de altíssima qualidade. Parabéns pelo trabalho!",
    "Já passei por essa situação e a solução que encontrei foi um pouco diferente. Funcionou bem também.",
    "Faltou mencionar a biblioteca X, que também é uma ótima alternativa para este caso.",
    "Estou ansioso pela parte 2 deste post!",
    "Isso me lembrou de uma viagem que fiz no ano passado. Que saudades!",
    "Essa receita parece deliciosa, vou tentar fazer no final de semana!",
    "Concordo 100%. A tática defensiva desse time precisa urgentemente de uma revisão.",
    "Para mim, essa banda marcou uma geração. Ótima análise do álbum.",
    "Existe alguma alternativa open-source para a ferramenta que você mencionou?",
    "Que fotos incríveis! Qual câmera você usou?",
    "Nunca consegui acertar o ponto do risoto, vou seguir sua dica da próxima vez.",
]

async def seed_database():
    print("Iniciando o povoamento (versão com likes aleatórios)...")

    # --- Limpando coleções ---
    print("Limpando coleções...")
    await asyncio.gather(
        category_collection.delete_many({}), tag_collection.delete_many({}),
        post_collection.delete_many({}), comment_collection.delete_many({}),
        post_tag_collection.delete_many({}), user_collection.delete_many({}),
        post_like_collection.delete_many({})
    )

    # --- 1. Criando Usuários ---
    print("Criando 10 usuários de exemplo...")
    users_data = [{"username": fake.user_name(), "email": fake.email(), "password": "password123", "creation_date": fake.date_time_this_year()} for _ in range(10)]
    user_result = await user_collection.insert_many(users_data)
    user_ids = [str(id) for id in user_result.inserted_ids]
    print(f"{len(user_ids)} usuários criados.")

    # --- 2. Criando Categorias e Tags ---
    print("Criando categorias e tags...")
    category_result = await category_collection.insert_many(CATEGORIES)
    tag_result = await tag_collection.insert_many(TAGS)
    categories_map = {cat['name']: str(cat_id) for cat, cat_id in zip(CATEGORIES, category_result.inserted_ids)}
    tags_map = {tag['name']: str(tag_id) for tag, tag_id in zip(TAGS, tag_result.inserted_ids)}
    print("Categorias e Tags criadas.")

    # --- 3. Criando Posts ---
    all_templates = POST_TEMPLATES * 2 
    print(f"Criando {len(all_templates)} posts temáticos...")
    posts_data = []
    for template in all_templates:
        posts_data.append({
            "title": template["title"], "content": template["content"],
            "author": random.choice(AUTHORS), "publication_date": fake.date_time_this_year(),
            "category_id": categories_map[template["category"]],
            "tags_id": [str(id) for id in random.sample(list(tags_map.values()), k=random.randint(1, 3))],
            "likes": 0
        })
    post_result = await post_collection.insert_many(posts_data)
    post_ids = [str(id) for id in post_result.inserted_ids]
    print("Posts criados.")
    
    # --- 4. Criando Comentários ---
    print("Criando 150 comentários realistas...")
    comments_data = []
    for _ in range(150):
        comments_data.append({
            "post_id": random.choice(post_ids), "user_id": random.choice(user_ids),
            "content": random.choice(COMMENT_TEMPLATES), "creation_date": fake.date_time_this_year()
        })
    await comment_collection.insert_many(comments_data)
    print("Comentários criados.")

    # --- 5. Criando Likes  ---
    print("Criando likes aleatórios de forma eficiente...")
    
    all_possible_likes = [(post_id, user_id) for post_id in post_ids for user_id in user_ids]
    random.shuffle(all_possible_likes)
    
   
    max_likes = len(all_possible_likes)
    num_likes_to_create = random.randint(int(max_likes * 0.4), int(max_likes * 0.8))
    
    
    selected_likes = all_possible_likes[:num_likes_to_create]
    
    likes_data = []
    post_like_counts = {}
    
    for post_id, user_id in selected_likes:
        likes_data.append({
            "post_id": post_id,
            "user_id": user_id,
            "created_at": fake.date_time_this_year()
        })
        post_like_counts[post_id] = post_like_counts.get(post_id, 0) + 1

    if likes_data:
        await post_like_collection.insert_many(likes_data)

    # --- 6. Atualizando o contador de likes nos posts ---
    print("Atualizando contadores de likes nos posts...")
    for post_id, count in post_like_counts.items():
        await post_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"likes": count}}
        )

    print(f"{len(likes_data)} likes criados e contadores atualizados.")
    print("\nBanco de dados final populado com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed_database())