import pandas as pd
import json
import os


class Formatter:
    @classmethod
    def _data_framer(cls, directory: str, files: list, filename: str = r'../tests/output/data') -> None:
        data_frames = []
        for file in files:
            with open(f"{directory}{file}") as _file:
                json_info = json.loads(_file.read())
                json_info = json_info['PosLog']['Transaction']['RetailTransaction']['LineItem']
                json_info = list(filter(lambda x: True if 'POSIdentity' in x else False, json_info))
                data_frames.append(
                    pd.DataFrame([{
                        'PLU': item['POSIdentity']['POSItemID'],
                        'Base': item['Tax'][0]['BaseAmount'],
                        item['Tax'][0]['Percent'][:-2]: item['Tax'][0]['Amount']
                    } for item in json_info])
                )

        data_frame = pd.concat(data_frames)
        data_frame.to_excel(f'{filename}.xlsx', index=False)

    @classmethod
    def _file_searcher(cls, directory: str) -> list:
        with os.scandir(directory) as folder:
            return list(filter(lambda x: x.endswith('.json'), [file.name for file in folder]))

    def __init__(self, directory: str = r'../tests/input/') -> None:
        self.__directory = directory
        self.__files = self._file_searcher(self.__directory)

        self._data_framer(self.__directory, self.__files)

    @property
    def directory(self) -> str:
        return self.__directory

    @property
    def files(self) -> list:
        return self.__files
