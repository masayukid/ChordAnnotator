from typing import List, Callable

class Command:
    def __init__(
            self,
            do: Callable[[], None],
            undo: Callable[[], None],
        ) -> None:
        self._do = do
        self._undo = undo

    def do(self) -> None:
        self._do()

    def undo(self) -> None:
        self._undo()

class Commander:
    def __init__(self) -> None:
        self.initialize()
        
    def initialize(self) -> None:
        self._num_change = 0
        self._undo_list: List[Command] = []
        self._redo_list: List[Command] = []

    def send(self, command: Command) -> None:
        self._undo_list.append(command)
        self._redo_list.clear()
        command.do()
        self._num_change += 1

    def undo(self) -> None:
        if len(self._undo_list) == 0:
            return
        
        command = self._undo_list.pop()
        self._redo_list.append(command)
        command.undo()
        self._num_change -= 1

    def redo(self) -> None:
        if len(self._redo_list) == 0:
            return
        
        command = self._redo_list.pop()
        self._undo_list.append(command)
        command.do()
        self._num_change += 1

    def clear_num_change(self) -> None:
        self._num_change = 0

    @property
    def has_been_changed(self) -> bool:
        return self._num_change != 0