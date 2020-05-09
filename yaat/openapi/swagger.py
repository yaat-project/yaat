from yaat.responses import HTMLResponse


def get_swagger_ui(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    swagger_favicon_url: str = "https://avatars0.githubusercontent.com/u/62506028?s=200&v=4",
) -> HTMLResponse:
    # TODO: replace Yaat logo from proper domain

    html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
                <link rel="shortcut icon" href="{swagger_favicon_url}">
                <title>{title}</title>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="{swagger_js_url}"></script>
                <script>
                    const ui = SwaggerUIBundle({{
                        url: '{openapi_url}',
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout",
                        deepLinking: true
                    }})
                </script>
            </body>
        </html>
    """

    return HTMLResponse(html)
