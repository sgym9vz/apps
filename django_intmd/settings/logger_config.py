import logging
import sys

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import CallsiteParameter


class LoggerConfig:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level, # ログレベルを追加
            structlog.stdlib.add_logger_name, # ロガー名を追加
            structlog.stdlib.PositionalArgumentsFormatter(), # 位置引数をフォーマット
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False), # タイムスタンプを追加
            structlog.processors.StackInfoRenderer(), # スタック情報を追加
            structlog.processors.UnicodeDecoder(), # ユニコードをデコード
            structlog.processors.CallsiteParameterAdder( # 呼び出し元のファイル名、行番号、関数名を追加
                parameters={
                    CallsiteParameter.FILENAME: True,
                    CallsiteParameter.LINENO: True,
                    CallsiteParameter.FUNC_NAME: True,
                }
            ),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter, # ProcessorFormatter で使える形式にラップ
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    def __init__(self):
        handler_stdout = logging.StreamHandler(sys.stdout)
        handler_stdout.setFormatter(structlog.stdlib.ProcessorFormatter(processor=ConsoleRenderer()))

        self.root_logger.addHandler(handler_stdout)
