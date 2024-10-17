from typing import List
from fastapi import FastAPI, Header, Path
from motor.motor_asyncio import AsyncIOMotorClient
from fleximongo import exc_handlers, schemas, strategies
from fastapi.middleware.cors import CORSMiddleware


class FlexiMongo:
    """
    Classe FlexiMongo para integração com o MongoDB.

    A classe fornece uma interface para operações em um banco de dados MongoDB
    usando o FastAPI. Permite a execução de operações CRUD e outras ações
    administrativas através de um único endpoint.

    Atributos:
    - `url`: URL de conexão com o banco de dados MongoDB.
    """

    def __init__(self, url: str, cors_origins: List[str] = []) -> None:
        """
        Inicializa a classe FlexiMongo.

        Parâmetros:
        - `url`: Uma string representando a URL de conexão com o MongoDB.
        """
        self.url = url
        self.cors_origins = cors_origins

    def init_app(self, app: FastAPI):
        """
        Inicializa o aplicativo FastAPI com manipuladores de exceção e
        registra o endpoint de operações no banco de dados.

        Parâmetros:
        - `app`: A instância do FastAPI onde as exceções serão tratadas
          e o endpoint será registrado.
        """
        exc_handlers.register_exception_handlers(app)
        self.register_entrypoint(app=app, url=self.url)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def register_entrypoint(self, app: FastAPI, url: str):
        """
        Registra o endpoint para operações no banco de dados MongoDB.

        Este endpoint permite executar operações CRUD e outras ações
        sobre coleções em um banco MongoDB.

        Parâmetros:
        - `app`: A instância do FastAPI onde o endpoint será registrado.
        - `url`: A URL de conexão com o MongoDB.
        """

        @app.post("/{db_name}/{collection_name}/")
        async def operation(
            body: schemas.OperationSchema,
            operation_name: str = Header(
                ...,
                title=(
                    "Nome da operação a ser executada no banco: "
                    "`find`, `find-many`, `delete`, `create`, `update`, `clear-collection`"
                ),
                description=(
                    "Especifica qual operação CRUD ou operação administrativa deve ser "
                    "executada na coleção do banco de dados. As operações permitidas são:\n"
                    "- `find`: Busca um único documento.\n"
                    "- `find-many`: Busca múltiplos documentos.\n"
                    "- `delete`: Deleta um ou mais documentos.\n"
                    "- `create`: Cria um novo documento.\n"
                    "- `update`: Atualiza um ou mais documentos existentes.\n"
                    "- `clear-collection`: Remove todos os documentos de uma coleção."
                ),
            ),
            collection_name: str = Path(
                ...,
                title="Nome da coleção onde as operações serão executadas",
                description=(
                    "Define a coleção específica do MongoDB onde a operação será realizada. "
                    "A coleção deve existir no banco de dados selecionado."
                ),
            ),
            db_name: str = Path(
                ...,
                title="Nome do banco de dados onde as operações serão executadas",
                description=(
                    "Especifica o banco de dados do MongoDB onde a coleção está localizada. "
                    "É importante que o banco de dados seja acessível para a operação."
                ),
            ),
        ):
            """
            Executa uma operação no banco de dados MongoDB com base no `operation_name`, usando a
            estratégia mapeada da camada `strategies`. As operações podem incluir CRUD básico e
            ações como limpar uma coleção inteira.

            Parâmetros:
            - `body`: O corpo da requisição contendo os dados necessários para a operação, definido
                      pelo esquema `schemas.OperationSchema`.
            - `operation_name`: O nome da operação a ser realizada (find, find-many, delete, etc.).
            - `collection_name`: O nome da coleção onde a operação será aplicada (fornecido no cabeçalho).
            - `db_name`: O nome do banco de dados onde a coleção está localizada (fornecido no cabeçalho).

            Retorna:
            - O resultado da operação executada, conforme definido pela estratégia aplicada.
            """

            # Seleciona a coleção MongoDB com base na URL,
            # no nome do banco e no nome da coleção
            mongo_collection = self.get_collection(url, db_name, collection_name)

            # Mapeia a operação fornecida para a estratégia correta
            strgy = strategies.operation_mapping[operation_name](mongo_collection)

            # Configura a operação e a executa
            return (
                await strategies.Operation(strgy)
                .set_options(operation_name, body)
                .excecute_operation()
            )

    def get_collection(self, url, db_name, collection_name):
        """
        Obtém a coleção do MongoDB com base na URL, no nome do banco de dados e no nome da coleção.

        Parâmetros:
        - `url`: URL de conexão com o MongoDB.
        - `db_name`: Nome do banco de dados onde a coleção está localizada.
        - `collection_name`: Nome da coleção que se deseja acessar.

        Retorna:
        - A coleção do MongoDB correspondente aos parâmetros fornecidos.
        """
        client = AsyncIOMotorClient(url)
        db = client[db_name]
        collection = db[collection_name]
        return collection
