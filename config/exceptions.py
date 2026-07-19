import logging

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

logger = logging.getLogger("apps")

ERROR_CODES = {
    400: "REQUISICAO_INVALIDA",
    401: "NAO_AUTENTICADO",
    403: "ACESSO_NEGADO",
    404: "NAO_ENCONTRADO",
    405: "METODO_NAO_PERMITIDO",
    409: "CONFLITO",
    422: "VALIDACAO",
    429: "MUITAS_REQUISICOES",
    500: "ERRO_INTERNO",
}


def _extract_details(exc):
    details = []
    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, dict):
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    for msg in messages:
                        details.append({"campo": field, "mensagem": str(msg)})
                else:
                    details.append({"campo": field, "mensagem": str(messages)})
        elif isinstance(exc.detail, list):
            for msg in exc.detail:
                details.append({"mensagem": str(msg)})
    return details


def _get_path(context):
    request = context.get("request")
    return getattr(request, "path", "desconhecido") if request else "desconhecido"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        error_code = ERROR_CODES.get(status_code, "ERRO_DESCONHECIDO")
        details = _extract_details(exc)

        message_map = {
            400: "Dados da requisição inválidos.",
            401: "Autenticação necessária. Forneça uma API Key válida.",
            403: "Você não tem permissão para acessar este recurso.",
            404: "Recurso não encontrado.",
            405: "Método HTTP não permitido para este recurso.",
            422: "Dados enviados não passaram na validação.",
            429: "Limite de requisições excedido. Aguarde e tente novamente.",
            500: "Erro interno do servidor. Nossa equipe foi notificada.",
        }
        message = message_map.get(status_code, str(exc))

        response.data = {
            "erro": error_code,
            "mensagem": message,
            "detalhes": details,
        }

        extra = {
            "status_code": status_code,
            "error_code": error_code,
            "exception": str(exc),
            "path": _get_path(context),
        }

        if 400 <= status_code < 500:
            logger.warning("Erro do cliente na requisição", extra=extra)
        else:
            logger.error("Erro interno na requisição", extra=extra)

    return response
