#!/usr/bin/python
from utils import jsonclass
from dataclasses import dataclass
from typing import List


@jsonclass('JsonClass.json')
@dataclass
class Cleanup:
    name: str
    age: int
    array: List[int]


if __name__ == '__main__':
    c1 = Cleanup(name='John', age=25, array=[12, 20])
    c1.save()
    c2 = Cleanup.load()
    print(c1, c2)
