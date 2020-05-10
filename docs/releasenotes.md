# Release Notes

### 0.1.9

- Updated routes to only allow `GET` method if HTTP methods are not specified.
- API schema generator, `OpenAPISchema` and `SchemaGenerator`.
- [Swagger UI](https://swagger.io/tools/swagger-ui/), `get_swagger_ui`.

### 0.1.8

- Bugfix on router. Read more about issue [here](https://github.com/yaat-project/yaat/pull/25).

### 0.1.7

- Rewrite new routing strategy. Read more [here](https://github.com/yaat-project/yaat/pull/23).

### 0.1.6

- Fixed `StaticFiles` getting 404 when mounted to sub router instead of main Yaat application.

### 0.1.5

- Added path parameters datatype conversion.
- Configured `flake8` and `black` with a pre-commit hook for code formatting.
- Added path-parm type conversion based on the route type-hints.

### 0.1.4

- Fixed `asyncio` tasks not working on python3.6.

### 0.1.3

- Added `StreamResponse` for HTTP response streaming.
- Added server startup and shutdown events.

### 0.1.2

- Added CORS middleware.

### 0.1.1

- Added WebSockets functionality.
- Added built-in background task runner.
