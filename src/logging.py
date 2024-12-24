import logging

core_logger = None
core_fh = None
core_ch = None

def setup_logging():
    global core_logger, core_fh, core_ch
    baseLevel = "INFO"

    logging.basicConfig(level=logging.NOTSET, handlers=[])
    core_logger = logging.getLogger('C')
    core_fh = logging.FileHandler("sbbs1k.log")
    core_fh.setLevel(baseLevel)
    core_ch = logging.StreamHandler()
    core_ch.setLevel(baseLevel)

    formatter = logging.Formatter('[{levelname: ^8}] [{name: ^6}] {message}', style='{')
    verbose_formatter = logging.Formatter('{asctime} - [{levelname}] [{name}] {message}', style='{')
    core_fh.setFormatter(verbose_formatter)
    core_ch.setFormatter(formatter)

    core_logger.handlers.clear()
    core_logger.addHandler(core_fh)
    core_logger.addHandler(core_ch)

def set_log_level(log_level:str):
    global core_logger, core_fh, core_ch
    core_fh.setLevel(log_level)
    core_ch.setLevel(log_level)