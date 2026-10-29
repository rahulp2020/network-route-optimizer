import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(level: str) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | [%(request_id)s] | %(name)s | %(message)s")
    )
    handler.addFilter(RequestIdLogFilter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    return logging.getLogger("network_route_optimizer")
