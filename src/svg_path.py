from easymunk import Vec2d
from typing import  List
import pyxel


def mk_path(src: str, origin=(0, 0)) -> List[Vec2d]:
    cursor = Vec2d(*origin)
    path = [cursor]

    parts = src.replace(",", " ").split()
    parts.reverse()

    def read_vec():
        return Vec2d(read_num(), read_num())

    def read_num():
        return float(parts.pop())

    cmd = "M"
    while parts:
        if parts[-1][-1] not in "0123456789-":
            cmd = parts.pop()
            if len(cmd) > 1:
                parts.append(cmd[1:])
                cmd = cmd[0]
        if cmd in "LM":
            cursor = read_vec()
        elif cmd in "lm":
            cursor += read_vec()
        elif cmd == "H":
            cursor = cursor.copy(x=read_num())
        elif cmd == "h":
            cursor = cursor.copy(x=cursor.x + read_num())
        elif cmd == "V":
            cursor = cursor.copy(y=read_num())
        elif cmd == "v":
            cursor = cursor.copy(y=cursor.y + read_num())
        elif cmd in ("z", "Z"):
            if parts:
                raise ValueError("caminho fechou antes de terminar.")
            break
        else:
            raise ValueError(f"comando inválido: {cmd!r}")
        path.append(cursor)

    if src.lstrip()[0] in "mM":
        path.pop(0)

    return path