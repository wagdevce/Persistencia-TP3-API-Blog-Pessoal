# 📝 Blog API - com FastAPI e MongoDB

Este projeto consiste em uma **API RESTful** para gerenciamento de um **Sistema de Blog**, desenvolvida com **FastAPI** e **MongoDB**. O sistema permite o gerenciamento completo de posts, categorias, tags e comentários, incluindo filtros avançados, paginação, ordenação e um dashboard de estatísticas.

---

## 📚 Funcionalidades

- CRUD completo para todas as entidades.
- Relacionamentos complexos implementados:
  - **1:1 (Embedding):** Perfil do Autor embutido dentro de cada Post.
  - **1:N (Referenciamento):** Entre `Category` e `Post`, e entre `Post` e `Comment`.
  - **N:N (Coleção extra):** Entre `Post` e `Tag`.
- Paginação e filtros nos endpoints de listagem.
- Consultas avançadas (texto parcial, filtro por data, ordenação).
- Otimização de consultas com **índices** no MongoDB.
- Endpoint de estatísticas com **Pipeline de Agregação** do MongoDB.
- Registro de logs de operações.

---

## 🧱 Entidades e Relacionamentos

### 🔹 Category (Categoria)
- `name`
- `description`

### 🔹 AuthorProfile (Perfil do Autor - Embutido)
- `name`
- `bio` (opcional)

### 🔹 Post
- `title`
- `content`
- `author`: Relacionamento 1:1 com `AuthorProfile` (documento embutido).
- `publication_date`
- `category_id`: Relacionamento N:1 com `Category` (referência).
- `tags_id`: Lista de IDs de `Tags` (para a relação N:N).

### 🔹 Tag
- `name`

### 🔹 Comment (Comentário)
- `post_id`: Relacionamento N:1 com `Post` (referência).
- `author_name`
- `content`
- `creation_date`

### 🔹 PostTag (Associação N:N)
- `post_id`
- `tag_id`

---

## 🔧 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB](https://www.mongodb.com/)
- [Pydantic](https://docs.pydantic.dev/) (para validação de modelos)
- [Motor](https://motor.readthedocs.io/) (driver assíncrono para MongoDB)

---

## ▶️ Como Executar

1.  **Clone o repositório**:
    ```bash
    git clone [https://github.com/wagdevce/Persistencia-TP3-API-Blog-Pessoal.git](https://github.com/wagdevce/Persistencia-TP3-API-Blog-Pessoal.git)
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