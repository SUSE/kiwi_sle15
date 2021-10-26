# Copyright (c) 2021 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
from typing import IO

from tempfile import (
    NamedTemporaryFile,
    TemporaryDirectory
)

# project
import kiwi.defaults as defaults


class Temporary:
    """
    **Provides namespace to handle temporary files and directories**
    """
    def __init__(
        self, dir: str = defaults.TEMP_DIR, prefix: str = ''
    ):
        self.prefix = prefix if prefix else 'kiwi_'
        self.dir = dir

    def new_file(self) -> IO[bytes]:
        return NamedTemporaryFile(
            dir=self.dir, prefix=self.prefix
        )

    def new_dir(self) -> TemporaryDirectory:
        return TemporaryDirectory(
            dir=self.dir, prefix=self.prefix
        )
