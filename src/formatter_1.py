import panconazucar as pd
import json
import os


class Formatter:
    @classmethod
    def _data_framer(cls, directory: str, files: list, filename: str = r'../resource/Poslog.json') -> None:
        data_frames = []
        for file in files:
            with open(f"{directory}{file}") as _file:
                json_info = json.loads(_file.read())
                json_info = json_info['PosLog']['Transaction']['RetailTransaction']['LineItem']
                info_producto = list(filter(lambda x: True if 'POSIdentity' in x else False, json_info))
                info_tender = list(filter(lambda x: True if 'Tender' in x else False, json_info))
                info_producto_df = pd.DataFrame([{
                    'PLU': item['POSIdentity']['POSItemID'],
                    'Base': float(item['Tax'][0]['BaseAmount']),
                    item['Tax'][0]['Percent'][:-2]: float(item['Tax'][0]['Amount'])
                } for item in info_producto])
                info_tender_df = pd.DataFrame([
                    {
                        item['Tender']['TenderType']: float(item['Tender']['Amount']) - float(item['Tender']['TenderChange']['Amount'])
                    } if 'TenderChange' in item['Tender'] else {
                        item['Tender']['TenderType']: float(item['Tender']['Amount'])
                    } for item in info_tender
                ])
                info_full_df = pd.concat([info_producto_df, info_tender_df], axis=1)
                # pd.DataFrame([])
                data_frames.append(info_full_df)

        data_frame = pd.concat(data_frames)
        headers = data_frame.columns.to_list()
        headers = cls.make_reindex(headers)
        data_frame = data_frame.reindex(columns=headers)
        print(data_frame)
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

    @classmethod
    def make_reindex(cls, headers: list) -> list:
        headers.sort()
        plu = headers.pop(headers.index('PLU'))
        base = headers.pop(headers.index('Base'))
        return [plu, base] + headers


if __name__ == '__main__':
    a = Formatter()
    # print(a.make_reindex(['0', '19', '5', 'Base', 'Cash', 'CreditoEspecial', 'PLU', 'Vales']))
