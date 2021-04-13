import csv
from itertools import chain

from pypinyin import pinyin, Style
from tornado.options import define, options, parse_command_line


class CSV(object):
    @staticmethod
    def read(file):
        with open(file, "r") as fin:
            reader = csv.reader(fin, delimiter="|")
            headers = next(reader)
            for line in reader:
                yield dict(zip(headers, line))

    @staticmethod
    def write(data, file):
        with open(file, "w") as fout:
            writer = csv.writer(fout, delimiter="|")
            writer.writerows(data)


def get_converter(key):
    if key == "日期":
        return lambda s: tuple([int(v) for v in s.split(".")])
    return lambda s: "".join(chain.from_iterable(pinyin(s, style=Style.TONE3)))


define("file", help="file path")
define("keys", multiple=True, help="sort by key(s)")

def main():
    parse_command_line()
    
    # 排序
    sorted_data = sorted(
        CSV.read(options.file), 
        key=lambda item: tuple([get_converter(k)(item[k]) for k in options.keys])
    )
    data = [list(sorted_data[0].keys())] + [list(line.values()) for line in sorted_data]
    
    CSV.write(data, options.file)
    print(f"{options.file} ok")


if __name__ == "__main__":
    main()
