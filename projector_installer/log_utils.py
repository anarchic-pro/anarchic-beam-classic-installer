# Copyright 2000-2020 JetBrains s.r.o.
# Use of this source code is governed by the Apache 2.0 license that can be found
# in the LICENSE file.

"""Log files management functions"""

from datetime import datetime
from os.path import isfile, getsize
from sys import stdout
from typing import TextIO

from projector_installer.run_config import get_path_to_log

MAX_LOG_FILE_SIZE = 1024 * 1024
START_SESSION_MARK = '--------------------- Projector log session start.'


def restrict_log_size(config_name: str) -> None:
    """
    Ensure that log file does not exceed MAX_LOG_FILE_SIZE
    """
    log_name = get_path_to_log(config_name)
    size = getsize(log_name)

    if isfile(log_name) and size > MAX_LOG_FILE_SIZE:
        with open(log_name, 'w+') as log:
            log.seek(size - MAX_LOG_FILE_SIZE)
            content = log.read()
            log.seek(0)
            log.truncate()
            log.write(content)
            log.flush()


def init_log(config_name: str) -> TextIO:
    """Performs initialization of log file"""
    restrict_log_size(config_name)
    log = open(get_path_to_log(config_name), 'a+')
    print(f"{START_SESSION_MARK} Run config: {config_name} - {datetime.now()}", file=log)
    log.flush()

    return log


def dump_last_log_session(log: TextIO) -> None:
    """Prints to stdout content of given file starting from last session mark"""
    log.seek(0)
    content = log.read()
    pos = content.rindex(START_SESSION_MARK)
    stdout.write(content[pos:])


def is_unexpected_exit(ret_code: int) -> bool:
    """Check if process exits without error"""
    return ret_code not in [0, -2]


def shutdown_log(ret_code: int, log_file: TextIO) -> None:
    """Closes log with last session dump if necessary"""

    if is_unexpected_exit(ret_code):
        dump_last_log_session(log_file)

    log_file.close()
