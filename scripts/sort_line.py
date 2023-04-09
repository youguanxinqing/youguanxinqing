import re
import csv
from typing import NoReturn, List, Dict, Iterator, Tuple
from dataclasses import dataclass, asdict
from itertools import chain
from functools import partial

from pypinyin import pinyin, Style
from tornado.options import define, options, parse_command_line


@dataclass
class Header(object):
    freq: str
    author: str
    title_or_date: str
    content: str

    @classmethod
    def from_lyst(cls, lyst: List) -> "Header":
        return cls(
            freq=lyst[0],
            author=lyst[1],
            title_or_date=lyst[2],
            content=lyst[3],
        )


@dataclass
class Liner(object):
    freq: int
    author: str
    title_or_date: str
    content: str

    @classmethod
    def from_lyst(cls, lyst: List) -> "Liner":
        return cls(
            freq=int(lyst[0]),
            author=lyst[1],
            title_or_date=lyst[2],
            content=lyst[3],
        )
    
    def is_date(self, pattern: re.Pattern = re.compile(r"(\d+\.){1,2}\d")) -> bool:
        return bool(pattern.match(self.title_or_date))


def get_cmp_key(line: Liner, keys: List[str]) -> Tuple:
    result = []
    for key in keys:
        line_dict = asdict(line)
        value = line_dict[key]
        if key == "title_or_date" and line.is_date():
            # breakpoint()
            result.append(tuple([int(s) for s in value.split(".")]))
        else:
            result.append("".join(chain.from_iterable(pinyin(value, style=Style.TONE3))))
    return tuple(result)


class CSV(object):

    @staticmethod
    def read_header(file: str) -> Header:
        with open(file, "r") as fin:
            reader = csv.reader(fin, delimiter="|")
            headers = next(reader)
            return Header.from_lyst(headers)

    @staticmethod
    def read(file: str) -> Iterator[Liner]:
        with open(file, "r") as fin:
            reader = csv.reader(fin, delimiter="|")
            next(reader)
            for line in reader:
                yield Liner.from_lyst(line)

    @staticmethod
    def write(header: Header, lines: List[Liner], file: str):

        data = chain([asdict(header).values()], [asdict(l).values() for l in lines])

        with open(file, "w") as fout:
            writer = csv.writer(fout, delimiter="|")
            writer.writerows(data)


def init_freq(lines: List[Liner]) -> NoReturn:
    old_liner = [l for l in lines if l.freq > 0]
    avg_freq = sum(map(lambda l: l.freq, old_liner)) / (len(old_liner) or 1)
    
    for line in lines:
        if line.freq < 0:
            line.freq = avg_freq


define("file", help="file path")
define("keys", multiple=True, help="sort by key(s)")


def main():
    parse_command_line()

    # 获取 header
    header = CSV.read_header(file=options.file)
    # 排序
    sorted_data = sorted(CSV.read(options.file), key=partial(get_cmp_key, keys=options.keys))
    # 对新进数据初始化频次
    init_freq(lines=sorted_data)

    CSV.write(header=header, lines=sorted_data, file=options.file)
    
    print(f"{options.file} ok")


if __name__ == "__main__":
    main()
