# 📝 API de Blog com FastAPI e MongoDB

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green?style=for-the-badge&logo=mongodb&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen?style=for-the-badge)

Uma API RESTful completa para um sistema de gerenciamento de conteúdo (Blog), desenvolvida para o Trabalho Prático 3 da disciplina de Desenvolvimento de Software para Persistência.

---

### 📚 Índice

- [✨ Sobre o Projeto](#-sobre-o-projeto)
- [🎥 Demonstração em Vídeo](#-demonstração-em-vídeo)
- [🚀 Principais Funcionalidades](#-principais-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [⛓️ Modelagem e Relacionamentos](#️-modelagem-e-relacionamentos)
- [🗺️ Rotas da API (Endpoints)](#️-rotas-da-api-endpoints)
- [▶️ Começando](#️-começando)

---

### ✨ Sobre o Projeto

Este projeto implementa um backend robusto para um sistema de Blog. A API gerencia posts, categorias, tags, comentários e usuários, incluindo funcionalidades avançadas como um sistema de likes, filtros complexos, paginação, e um dashboard de estatísticas, tudo construído com foco em performance e boas práticas de desenvolvimento.

---

### 🎥 Demonstração em Vídeo

Assista a uma demonstração completa da API em funcionamento, cobrindo a criação de entidades, as consultas avançadas e a interação entre os endpoints.

[![Demonstração da API de Blog](https://img.youtube.com/vi/alr87_tMOrc/0.jpg)](https://youtu.be/alr87_tMOrc)

---

### 🚀 Principais Funcionalidades

- ✅ **CRUD Completo:** Gerenciamento total para `Posts`, `Categories`, `Tags` e `Users`.
- 🔗 **Relacionamentos Complexos:** Implementação dos três tipos de relacionamentos exigidos:
  - **1:1 (Embedding):** Perfil do autor embutido no post.
  - **1:N (Referenciamento):** Categorias com múltiplos posts e posts com múltiplos comentários.
  - **N:N (Associação):** Posts com múltiplas tags e um sistema de likes baseado em usuários.
- 쿼 **Consultas Avançadas:** Suporte a paginação, ordenação (por data, likes), e filtros por texto e data.
- 📊 **Agregação de Dados:** Endpoints complexos que consolidam informações de múltiplas coleções, incluindo um dashboard de estatísticas.
- ⚡ **Otimização de Performance:** Uso de índices no MongoDB para acelerar as consultas mais comuns.
- 👤 **Sistema de Usuários:** Entidade `User` completa para gerenciar os leitores que interagem com o blog.

---

### 🛠️ Tecnologias Utilizadas

- **[Python 3.11+](https://www.python.org/)**: Linguagem principal do projeto.
- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web de alta performance para a construção da API.
- **[MongoDB](https://www.mongodb.com/)**: Banco de dados NoSQL orientado a documentos.
- **[Pydantic](https://docs.pydantic.dev/)**: Para validação e modelagem de dados.
- **[Motor](https://motor.readthedocs.io/)**: Driver assíncrono para comunicação com o MongoDB.
- **[Faker](https://faker.readthedocs.io/)**: Para a geração de dados de teste realistas (`seed.py`).

---

### ⛓️ Modelagem e Relacionamentos

A base de dados foi modelada com 5 entidades principais (`Post`, `Category`, `Tag`, `Comment`, `User`) e 2 entidades de suporte (`AuthorProfile`, `PostLike`). A estrutura de relacionamentos garante a integridade e a eficiência das consultas.

---

### 🗺️ Rotas da API (Endpoints)

Abaixo estão alguns dos principais endpoints disponíveis na API.

| Método HTTP | Endpoint                                     | Descrição                                                 |
| :---------- | :------------------------------------------- | :---------------------------------------------------------- |
| **Users** |                                              |                                                             |
| `POST`      | `/users/`                                    | Cria um novo usuário.                                       |
| `GET`       | `/users/`                                    | Lista todos os usuários com paginação.                      |
| `GET`       | `/users/{user_id}`                           | Busca um usuário específico por ID.                         |
| `PUT`       | `/users/{user_id}`                           | Atualiza os dados de um usuário.                            |
| `DELETE`    | `/users/{user_id}`                           | Deleta um usuário e seus comentários.                       |
| **Posts** |                                              |                                                             |
| `POST`      | `/posts/`                                    | Cria um novo post.                                          |
| `GET`       | `/posts/`                                    | Lista todos os posts com filtros, paginação e ordenação.    |
| `GET`       | `/posts/{post_id}/full_details`              | **Consulta Complexa:** Retorna o post com todos os seus dados relacionados. |
| `POST`      | `/posts/{post_id}/like/{user_id}`            | Registra o like de um usuário em um post.                   |
| `DELETE`    | `/posts/{post_id}/like/{user_id}`            | Remove o like de um usuário de um post.                     |
| `GET`       | `/posts/popular/`                            | Lista os posts mais populares (baseado em likes e comentários). |
| **Dashboard** |                                              |                                                             |
| `GET`       | `/dashboard/stats`                           | **Consulta com Agregação:** Retorna estatísticas gerais do blog. |


---

### ▶️ Começando

Siga os passos abaixo para executar o projeto localmente.

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
    Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
    ```env
    MONGO_URL=mongodb://localhost:27017/blog
    ```

5.  **(Opcional) Popule o banco com dados de exemplo**:
    Para ter dados iniciais para teste, execute o script de *seeding*:
    ```bash
    python seed.py
    ```

6.  **Inicie o servidor**:
    ```bash
    uvicorn main:app --reload
    ```

7.  **Acesse a documentação interativa**:
    Abra seu navegador e acesse `http://127.0.0.1:8000/docs`.