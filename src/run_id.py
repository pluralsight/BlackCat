import os
from typing import Optional


class RunId(object):
    def __init__(self, filename: Optional[str] = 'run-id.txt'):
        self.filename = filename
        if not os.path.isfile(self.filename):
            self.value = 0
            with open(self.filename, 'w+') as f:
                f.write(str(self.value))
        else:
            with open(self.filename) as f:
                self.value = int(f.read().strip())

    def inc_run_id(self):
        self.value += 1
        with open(self.filename, 'w+') as f:
            f.write(str(self.value))
