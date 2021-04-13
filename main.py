from typing import List, Optional, NewType, Dict, Tuple

import os
import abc
import csv
import random
import string


############################ type #################################
Word = NewType("Word", str)
Line = NewType("Line", List[str])
Page = NewType("Page", List[Line])
Book = NewType("Book", List[Page])


############################ tool #################################

class CSVReader(object):
    def read_csv(self, file_path: str, ignore_header=True) -> List:
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, "r") as fin:
            reader = csv.reader(fin, delimiter="|")
            if ignore_header:
                return list(reader)[1:]
            return list(reader)
    
    def write_csv(self, page: Page, file_path: str):
        if not os.path.exists(file_path):
            return

        with open(file_path, "w") as fout:
            writer = csv.writer(fout, delimiter="|")
            writer.writerows(page)


class GenReadme(object):

    def __init__(self, template_string: str):
        self.temlate_string = string.Template(template_string)

    @property
    def readme_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    
    def render(self, **kwargs):
        with open(self.readme_path, "w") as fout:
            fout.write(self.temlate_string.substitute(**kwargs))


############################ action #################################

class Action(metaclass=abc.ABCMeta):
    title: str = ""

    @abc.abstractmethod
    def act(self):
        pass

    @property
    def root_path(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))
    
    @property
    def data_path(self) -> dir:
        return os.path.join(self.root_path, "data")
    

class NoAction(Action):
    title = "no action"
    
    def act(self):
        pass


class InfoAction(Action):
    title = "info"

    def _to_word(self) -> Word:
        return f"""
# {self.title.capitalize()}

- 📝 blog: https://youguanxinqing.xyz/
- ✉️  mail: youguanxinqing@gmail.com || youguanxinqing@qq.com
- 📙 favorites: https://youguanxinqing.github.io/favorites/#/
"""

    def act(self) -> Tuple:
        return self.title, self._to_word()


class OneWordAction(Action, CSVReader):
    title = "one" 

    def __init__(self, files: Optional[List[str]] = None):
        self._files = files or []

        self.ALLOW_MAX_DIFF = 5
        # 频次, 作者, 作品, 内容
        self.freq, self.author, self.name, self.content = 0, 1, 2, 3
        # 页号, 行号
        self.pno, self.lno = 4, 5

    def _read_csvs(self) -> Page:
        """
            获取多页内容，整合到一页

            存在 header, 因此 line_no + 1
        """
        return [
            [*line, pno, lno+1] for pno, page in enumerate(map(self.read_csv, map(lambda f: os.path.join(self.data_path, f), self._files))) for lno, line in enumerate(page)
        ]
    
    def _drop_hot_freq(self, page: Page) -> Page:
        """
            过滤掉频率过高的句子
        """
        min_freq = int(page[0][self.freq])
        allow_max_freq = min_freq + self.ALLOW_MAX_DIFF
        return list(filter(lambda l: int(l[self.freq]) <= allow_max_freq, page))
    
    def _random_choose(self, words) -> Page:
        """
            随机选择一句
        """
        idx = random.randrange(0, len(words))
        return words[idx]
    
    def _incr_freq(self, page_no: int, line_no: int):
        for file_path in map(lambda f: os.path.join(self.data_path, f), self._files[page_no:]):
            page = self.read_csv(file_path, ignore_header=False)
            if len(page) <= 1:
                continue
            
            page[line_no][self.freq] = int(page[line_no][self.freq]) + 1
            self.write_csv(page, file_path)
            break

    
    def _to_word(self, line: Line) -> Word:
        return f"""
# {self.title.capitalize()} 
 
  
{line[self.author]}{line[self.name]} 
 
>{line[self.content]}        
 
"""

    def act(self) -> Tuple:
        page = sorted(self._read_csvs(), key=lambda item: item[self.freq])
        if not page:
            return
        
        line: Line = self._random_choose(self._drop_hot_freq(page))
        self._incr_freq(line[self.pno], line[self.lno])
        return self.title, self._to_word(line)


if __name__ == "__main__":
    actions = [
        OneWordAction(["book.csv", "mood.csv", "poetry.csv"]),
        InfoAction(),
    ]
    GenReadme("$one$info").render(**{k: v for k, v in map(lambda action: action.act(), actions)})

    