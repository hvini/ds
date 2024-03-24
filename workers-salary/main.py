from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv
import pandas as pd
import requests
import tqdm
import os

load_dotenv()

ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 200


class Main:

    def __init__(self, **kwargs):

        self.__headers = kwargs.get('headers', None)
        self.__siape = kwargs.get('siape', None)
        self.__mesano = kwargs.get('mesano', None)
        self.__iter = kwargs.get('iter', 1000)
        self.__servidores_url = 'https://api.portaldatransparencia.gov.br/api-de-dados/servidores'

    def generate(self):

        for cod_siape in self.__siape:

            for pagina in tqdm.tqdm(range(1, self.__iter),
                                    desc=f"Processing cod_siape: {cod_siape}"):

                params = {'orgaoServidorLotacao': cod_siape, 'pagina': pagina}
                try:

                    servidores = self._get_servidores(params)
                    if len(servidores) == 0:
                        break

                except requests.exceptions.RequestException as e:

                    print(f'Erro na requisição: {e}')
                    continue

                data = []
                for servidor_data in servidores:

                    servidor = servidor_data.get('servidor', {})
                    id_servidor = servidor.get(
                        'idServidorAposentadoPensionista')
                    if not id_servidor:
                        continue

                    res = {
                        'orgao': servidor['orgaoServidorLotacao']['nome'] if servidor.get('orgaoServidorLotacao') else '',
                        'situacao': servidor.get('situacao', ''),
                        'tipo': 'federal'
                    }

                    params = {'id': id_servidor,
                              'mesAno': self.__mesano, 'pagina': 1}
                    try:
                        remuneracoes = self._get_remuneracoes_servidor(params)
                        if len(remuneracoes) == 0:
                            continue

                        remuneracoes_dto = remuneracoes[0].get(
                            'remuneracoesDTO', [])
                        fichas_cargo = servidor_data.get(
                            'fichasCargoEfetivo', [])

                        res['remuneracao_apos_deducoes'] = remuneracoes_dto[0].get(
                            'valorTotalRemuneracaoAposDeducoes', '') if len(remuneracoes_dto) > 0 else ''
                        res['cargo'] = fichas_cargo[0].get(
                            'cargo', '') if len(fichas_cargo) > 0 else ''

                    except requests.exceptions.RequestException as e:
                        print(f'Erro na requisição para o servidor {
                              id_servidor}: {e}')
                        # se o id é negativo servidor é confidencial
                        if int(id_servidor) < 0:

                            res['remuneracao_apos_deducoes'] = ''
                            res['cargo'] = 'CONFIDENCIAL'

                    data.append(res)

                self._save_data(data)

    def _save_data(self, data):

        df = pd.DataFrame(data)
        if not os.path.exists('data.csv'):
            df.to_csv('data.csv', index=False)
        else:
            df.to_csv('data.csv', mode='a', index=False, header=False)

    @sleep_and_retry
    @limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
    def _get_remuneracoes_servidor(self, params):

        remuneracao_url = f'{self.__servidores_url}/remuneracao'
        response = requests.get(
            remuneracao_url, params=params, headers=self.__headers)
        response.raise_for_status()
        remuneracoes = response.json()
        return remuneracoes

    @sleep_and_retry
    @limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
    def _get_servidores(self, params):

        response = requests.get(self.__servidores_url,
                                params=params, headers=self.__headers)
        response.raise_for_status()
        servidores = response.json()
        return servidores


key = os.environ.get('API_KEY')
headers = {'chave-api-dados': key}
siape = [
    '17000',
    '23000',
    '20000',
    '37000',
    '21000',
    '16000',
    '45203',
    '22202',
    '29205',
    '70000'
    '40106',
    '20114',
    '21300',
    '32300',
    '39251',
    '39250',
    '44205',
    '52201',
    '32200',
    '36208',
    '41231',
    '36207',
    '20224',
    '40805',
    '21201',
    '40301',
    '29214',
    '20605',
    '99010',
    '22203',
    '22200',
    '38000',
    '40501',
    '20125',
    '20115',
    '32100',
    '39252',
    '30802',
    '42204',
]
mesano = '202401'

Main(headers=headers, siape=siape, mesano=mesano).generate()
