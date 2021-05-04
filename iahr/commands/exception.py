
from iahr.config import IahrConfig
from iahr.exception import IahrBaseError

localization = {}

localization['english'] = {
    'cantdeduce' : """
    No reply in the event, can\'t deduce document
""",
    'toolarge' : """
    Too large file size({:.2f}mb), should be less than {:.2f}mb
"""
}
localization['russian'] = {
    'cantdeduce' : """
    Нет реплая в данном сообщении, не могу найти файл
""",
    'toolarge' : """
    Слишком большой размер файла({:.2f}mb), должен  быть не больше {:.2f}mb
"""
}


local = localization[IahrConfig.LOCAL['lang']]


class IahrBuiltinCommandError(IahrBaseError):
    pass


class IahrCantDeduceDocumentError(IahrBuiltinCommandError):
    def __init__(self):
        super().__init__(loca['cantdeduce'])

class IahrDocumentSizeTooLarge(IahrBuiltinCommandError):
    def __init__(self, cur_size, max_size):
        super().__init__(local['toolarge'].format(cur_size, max_size))

    @classmethod
    def check(self, current, custom_key, default):
        if (cursize := current/(1024*1024)) > (maxsize := IahrConfig.CUSTOM.get(custom_key, default)):
            raise IahrDocumentSizeTooLarge(cursize, maxsize)
