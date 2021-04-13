import sys
import csv
from datetime import datetime
from itertools import chain

from pypinyin import pinyin, Style

FILE = "-file"
SORT_KEY = "-sort"


def help_info():
    print("""
help:
  -file={file}
  -sort={h1},{h2},{h3}
""")


def parse_command_line():
    if len(sys.argv) <= 1:
        help_info()
        return

    need_args = sys.argv[1:]
    if len(need_args) % 2 != 0:
        help_info()
        return
    
    length = len(need_args)
    return {
        need_args[ki]: need_args[ki+1] 
        for ki in filter(lambda x: x & 1 == 0, range(length))
    }


def read_csv(file):
    with open(file, "r") as fin:
        reader = csv.reader(fin, delimiter="|")
        headers = next(reader)
        for line in reader:
            yield dict(zip(headers, line))


def write_csv(data, file):
    with open(file, "w") as fout:
        writer = csv.writer(fout, delimiter="|")
        writer.writerows(data)


def get_converter(key):
    if key == "日期":
        return lambda s: tuple([int(v) for v in s.split(".")])
    return lambda s: "".join(chain.from_iterable(pinyin(s, style=Style.TONE3)))


def main():
    cmds = parse_command_line()
    _file = cmds[FILE]
    _keys = cmds[SORT_KEY].split(",")

    # 排序
    sorted_data = sorted(
        read_csv(_file), 
        key=lambda item: tuple([get_converter(k)(item[k]) for k in _keys])
    )
    data = [list(sorted_data[0].keys())] + [list(line.values()) for line in sorted_data]
    
    write_csv(data, _file)
    
    print(f"{_file} ok")


if __name__ == "__main__":
    main()
