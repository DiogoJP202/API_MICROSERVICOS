
# API MICROSERVIÇOS

Sistema acadêmico baseado em **microsserviços Flask** para:

* **Gerenciamento**: Professores, Turmas e Alunos (fonte de verdade dos IDs).
* **Reservas**: Reservas de salas (valida `turma_id` no Gerenciamento).
* **Atividades**: Atividades e Notas (valida `professor_id` e `turma_id` no Gerenciamento; Notas validam `aluno_id` no Gerenciamento e `atividade_id` localmente).

Cada serviço tem **banco próprio (SQLite)**, **CRUD REST**, **Swagger UI** e se comunica de forma **síncrona** com `requests`.

---

## 📦 Estrutura do repositório

```
.
├── docker-compose.yml
├── gerenciamento/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models/ (Professor, Turma, Aluno)
│   │   └── controllers/
│   │       ├── professor_controller.py
│   │       ├── turma_controller.py
│   │       ├── aluno_controller.py
│   │       └── seed_controller.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── reservas/
│   ├── app/
│   │   ├── models/reserva.py
│   │   └── controllers/
│   │       ├── reserva_controller.py
│   │       └── seed_controller.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
└── atividades/
    ├── app/
    │   ├── models/{atividade.py, nota.py}
    │   └── controllers/
    │       ├── atividade_controller.py
    │       ├── nota_controller.py
    │       └── seed_controller.py
    ├── Dockerfile
    ├── requirements.txt
    └── run.py
```

---

## 🧩 Arquitetura & Integração entre Serviços

* **Três microsserviços independentes**, cada um com:

  * Flask + SQLAlchemy + Swagger (Flasgger)
  * Banco **SQLite** próprio (isolado)
  * Camada MVC (models/controllers; sem views)
* **Comunicação síncrona** entre serviços via HTTP interno (rede Docker `schoolnet`):

  * `ms-gerenciamento:5000` (fonte de Professores/Turmas/Alunos)
  * `ms-reservas:5002`
  * `ms-atividades:5003`
* **Resolução de hostnames** por Docker Compose: os containers se chamam `ms-gerenciamento`, `ms-reservas`, `ms-atividades` na rede `schoolnet`.

### Fluxos de validação (requests)

* **Reservas** (POST `/api/reservas/`):

  * valida `turma_id` consultando **Gerenciamento**:

    ```python
    # reservas/app/controllers/reserva_controller.py
    GERENCIAMENTO_URL = os.getenv("GERENCIAMENTO_URL", "http://ms-gerenciamento:5000/api")
    requests.get(f"{GERENCIAMENTO_URL}/turmas/{turma_id}")  # 200 = OK, !=200 = erro
    ```
* **Atividades** (POST `/api/atividades/`):

  * valida `professor_id` e `turma_id` consultando **Gerenciamento**:

    ```python
    GERENCIAMENTO_URL = os.getenv("GERENCIAMENTO_URL", "http://ms-gerenciamento:5000/api")
    requests.get(f"{GERENCIAMENTO_URL}/professores/{prof_id}")
    requests.get(f"{GERENCIAMENTO_URL}/turmas/{turma_id}")
    ```
* **Notas** (POST `/api/notas/`):

  * valida `aluno_id` em **Gerenciamento** via `requests`;
  * valida `atividade_id` **localmente** (mesmo serviço), via SQLAlchemy (sem HTTP), por eficiência e simplicidade.

> Obs.: evitar chamadas HTTP para recursos **do mesmo serviço**. Para relacionamento **intra-serviço**, prefira o model SQLAlchemy.

---

## 🐳 Execução com Docker

### 1) Subir tudo

```bash
docker compose up --build
```

**Portas (host → container):**

* **Gerenciamento**: `localhost:8001` → `5000`
* **Reservas**: `localhost:8002` → `5002`
* **Atividades**: `localhost:8003` → `5003`

### 2) Health & Swagger

* Gerenciamento:

  * Health: [http://localhost:8001/health](http://localhost:8001/health)
  * Swagger: [http://localhost:8001/apidocs](http://localhost:8001/apidocs)
* Reservas:

  * Health: [http://localhost:8002/health](http://localhost:8002/health)
  * Swagger: [http://localhost:8002/apidocs](http://localhost:8002/apidocs)
* Atividades:

  * Health: [http://localhost:8003/health](http://localhost:8003/health)
  * Swagger: [http://localhost:8003/apidocs](http://localhost:8003/apidocs)

### 3) Popular os bancos (opcional)

```bash
curl -X POST http://localhost:8001/api/seed
curl -X POST http://localhost:8002/api/seed
curl -X POST http://localhost:8003/api/seed
```

---

## 🧪 Roteiro rápido de teste (fim-a-fim)

> Use `curl` no Windows PowerShell (a quebra de linha com `^` é opcional — você pode enviar numa linha só).

### 1) Gerenciamento

Criar Professor:

```bash
curl -X POST http://localhost:8001/api/professores/ ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Marcos Paulo\",\"materia\":\"Matemática\"}"
```

Criar Turma:

```bash
curl -X POST http://localhost:8001/api/turmas/ ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Turma A\",\"professor_id\":1}"
```

Criar Aluno:

```bash
curl -X POST http://localhost:8001/api/alunos/ ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Ana Silva\",\"turma_id\":1}"
```

### 2) Reservas (valida turma via Gerenciamento)

```bash
curl -X POST http://localhost:8002/api/reservas/ ^
  -H "Content-Type: application/json" ^
  -d "{\"sala\":\"Sala 101\",\"data_reserva\":\"2025-11-20\",\"turma_id\":1}"
```

### 3) Atividades (valida professor e turma via Gerenciamento)

```bash
curl -X POST http://localhost:8003/api/atividades/ ^
  -H "Content-Type: application/json" ^
  -d "{\"titulo\":\"Prova de Matemática\",\"descricao\":\"Geometria\",\"nota\":8.5,\"professor_id\":1,\"turma_id\":1}"
```

### 4) Notas (valida aluno via Gerenciamento e atividade localmente)

```bash
curl -X POST http://localhost:8003/api/notas/ ^
  -H "Content-Type: application/json" ^
  -d "{\"valor\":9.5,\"aluno_id\":1,\"atividade_id\":1}"
```

---

## 📚 Descrição da API (principais endpoints)

### Gerenciamento (8001)

* **Professores**

  * `GET /api/professores/`
  * `POST /api/professores/` (`nome`, `materia`)
  * `GET /api/professores/<id>`
  * `PUT /api/professores/<id>`
  * `DELETE /api/professores/<id>`
* **Turmas**

  * `GET /api/turmas/`
  * `POST /api/turmas/` (`nome`, `professor_id`)
  * `GET /api/turmas/<id>`
  * `PUT /api/turmas/<id>`
  * `DELETE /api/turmas/<id>`
* **Alunos**

  * `GET /api/alunos/`
  * `POST /api/alunos/` (`nome`, `turma_id`)
  * `GET /api/alunos/<id>`
  * `PUT /api/alunos/<id>`
  * `DELETE /api/alunos/<id>`

### Reservas (8002)

* **Reservas**

  * `GET /api/reservas/`
  * `POST /api/reservas/` (`sala`, `data_reserva`, `turma_id`)
  * `GET /api/reservas/<id>`
  * `PUT /api/reservas/<id>`
  * `DELETE /api/reservas/<id>`

### Atividades (8003)

* **Atividades**

  * `GET /api/atividades/`
  * `POST /api/atividades/` (`titulo`, `descricao`, `nota`, `professor_id`, `turma_id`)
  * `GET /api/atividades/<id>`
  * `PUT /api/atividades/<id>`
  * `DELETE /api/atividades/<id>`
* **Notas**

  * `GET /api/notas/`
  * `POST /api/notas/` (`valor`, `aluno_id`, `atividade_id`)
  * `GET /api/notas/<id>`
  * `PUT /api/notas/<id>`
  * `DELETE /api/notas/<id>`

---

## 🔒 Variáveis de ambiente (Docker Compose)

No `docker-compose.yml`, cada serviço usa hostnames internos para se falar:

```yaml
services:
  ms-gerenciamento:
    build: ./gerenciamento
    container_name: ms-gerenciamento
    ports: ["8001:5000"]
    networks: [schoolnet]

  ms-reservas:
    build: ./reservas
    container_name: ms-reservas
    ports: ["8002:5002"]
    depends_on: [ms-gerenciamento]
    environment:
      - GERENCIAMENTO_URL=http://ms-gerenciamento:5000/api
    networks: [schoolnet]

  ms-atividades:
    build: ./atividades
    container_name: ms-atividades
    ports: ["8003:5003"]
    depends_on: [ms-gerenciamento]
    environment:
      - GERENCIAMENTO_URL=http://ms-gerenciamento:5000/api
    networks: [schoolnet]

networks:
  schoolnet:
    driver: bridge
```

> Importante: **não** use `localhost` de dentro de um container para falar com outro container. Use o **nome do serviço** definido no Compose (`ms-gerenciamento`) e a **porta interna** exposta pelo app (5000/5002/5003).

---
