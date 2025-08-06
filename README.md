# 📝 Blog API - com FastAPI e MongoDB

Este projeto consiste em uma **API RESTful** para gerenciamento de um **Sistema de Blog**, desenvolvida com **FastAPI** e **MongoDB**. O sistema permite o gerenciamento completo de posts, categorias, tags, comentários e usuários, incluindo funcionalidades avançadas como um sistema de likes, filtros, paginação, ordenação e um dashboard de estatísticas.

---

## 📚 Funcionalidades

- CRUD completo para todas as entidades principais (Posts, Categories, Tags, Users).
- Gerenciamento de interações como Comentários e Likes.
- Sistema de Usuários com endpoints para criação, listagem, busca, atualização e deleção.
- Sistema de Likes baseado em usuários, que impede curtidas duplicadas.
- Relacionamentos complexos implementados:
  - **1:1 (Embedding):** Perfil do Autor embutido dentro de cada Post.
  - **1:N (Referenciamento):** Entre `Category` e `Post`, e entre `Post` e `Comment`.
  - **N:N (Coleção extra):** Entre `Post` e `Tag`, e entre `Post` e `User` (para os likes).
- Paginação, filtros avançados (texto parcial, data) e ordenação (por data, por likes).
- Otimização de consultas com **índices** no MongoDB.
- Endpoint de estatísticas com **Pipeline de Agregação** do MongoDB.
- Registro detalhado de logs de operações e requisições.

---

## 🧱 Entidades e Relacionamentos

### 🔹 User (Usuário)
- `username`
- `email`
- `creation_date`
- *Responsável por interações como comentários e likes.*

### 🔹 Category (Categoria)
- `name`
- `description`

### 🔹 Tag
- `name`

### 🔹 AuthorProfile (Perfil do Autor - Embutido)
- `name`
- `bio` (opcional)
- *Representa o autor do conteúdo, embutido diretamente no Post.*

### 🔹 Post
- `title`
- `content`
- `author`: Relacionamento 1:1 com `AuthorProfile` (documento embutido).
- `publication_date`
- `likes`: Contador de curtidas.
- `category_id`: Relacionamento N:1 com `Category` (referência).
- `tags_id`: Lista de IDs de `Tags` (para a relação N:N).

### 🔹 Comment (Comentário)
- `user_id`: Relacionamento N:1 com `User` (referência).
- `post_id`: Relacionamento N:1 com `Post` (referência).
- `content`
- `creation_date`

### 🔹 PostTag & PostLike (Associações N:N)
- `PostTag`: Armazena a ligação entre `post_id` e `tag_id`.
- `PostLike`: Armazena a ligação entre `post_id` e `user_id`, registrando cada curtida.

---

## 🚀 Endpoints Principais (Exemplos)

- `POST /users/`: Cria um novo usuário no sistema.
- `GET /posts/`: Lista todos os posts, com opções de paginação, filtros e ordenação (`sort_by=likes`).
- `POST /posts/{post_id}/like/{user_id}`: Permite que um usuário curta um post.
- `DELETE /posts/{post_id}/like/{user_id}`: Permite que um usuário remova seu like.
- `GET /posts/{post_id}/full_details`: Retorna um documento completo com o post, sua categoria, tags e todos os comentários.
- `GET /dashboard/stats`: Retorna estatísticas gerais do blog, calculadas via pipeline de agregação.

---

## 🔧 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB](https://www.mongodb.com/)
- [Pydantic](https://docs.pydantic.dev/) (para validação de modelos)
- [Motor](https://motor.readthedocs.io/) (driver assíncrono para MongoDB)
- [Faker](https://faker.readthedocs.io/) (para povoamento de dados)

---

## ▶️ Como Executar

1.  **Clone o repositório**:
    ```bash
    git clone [https://github.com/wagdevce/Persistencia-TP3-API-Blog-Pessoal.git]
    cd Persistencia-TP3-API-Blog-Pessoal
    ```

2.  **Crie e ative um ambiente virtual** (Recomendado):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\Activate.ps1
    # Linux/macOS
    source venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente**:
    Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo, apontando para o seu banco de dados `blog`:
    ```env
    MONGO_URL=mongodb://localhost:27017/blog
    ```

5.  **(Opcional) Popule o banco com dados de exemplo**:
    Para ter dados iniciais para teste, execute o script de *seeding*:
    ```bash
    python seed.py
    ```

6.  **Inicie o servidor**:
    Execute o Uvicorn a partir da pasta raiz do projeto:
    ```bash
    uvicorn main:app --reload
    ```

7.  **Acesse a documentação**:
    Abra seu navegador e acesse `http://127.0.0.1:8000/docs`.