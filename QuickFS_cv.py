import pandas as pd
import requests
import time

class qfs:
    
    def __init__(self, api: str, limit: int):
        self.api = api
        self.limit = int(limit)
        self.link = 'https://public-api.quickfs.net/v1/'

        metrics = requests.get(self.link + 'metrics')
        # print(metrics)
        metrics = metrics.json()

        n = {}
        for metric in metrics['data']:
            n[metric['metric']] = {'statement_type': metric['statement_type'], 'company_types': metric['company_types'],
                                   'data_type': metric['data_type'], 'periods': metric['periods'], }

        df = pd.DataFrame(n)
        df = df.transpose()
        df = df.reset_index()
        df.columns = ['metric', 'statement_type',
                      'company_types', 'data_type', 'periods']

        is_metrics = df[df.statement_type == 'income_statement']
        bs_metrics = df[df.statement_type == 'balance_sheet']
        cs_metrics = df[df.statement_type == 'cash_flow_statement']
        computed = df[df.statement_type == 'computed'].query(
            'periods == [["FY", "FQ"]]')
        medians = df[df.statement_type == 'computed'].query(
            'periods != [["FY", "FQ"]]')
        misc = df[df.statement_type == 'misc']

        all_statements = df[
            (df.statement_type == 'income_statement') |
            (df.statement_type == 'balance_sheet') |
            (df.statement_type == 'cash_flow_statements')]

        everything = df.query('periods == [["FY", "FQ"]]')

        self.is_metrics = is_metrics
        self.bs_metrics = bs_metrics
        self.cs_metrics = cs_metrics
        self.computed = computed
        self.medians = medians
        self.misc = misc
        self.statements = all_statements
        self.everything = everything

    def usage(self):
        usage = requests.get(self.link + f'usage?api_key={self.api}').json()
        return usage

    def when_reset(self):
        return self.usage()['usage']['quota']['resets']

    def used(self):
        used = self.usage()
        used = used['usage']['quota']['used']
        return used

    def remain(self):
        remain = self.usage()
        remain = remain['usage']['quota']['remaining']
        return remain

    def dcf(self, ticker, period='FY-19:FY'):

        mis = ['revenue', 'cogs', 'gross_profit', 'sga', 'rnd', 'other_opex',
               'total_opex', 'operating_income', 'interest_expense', 'income_tax', 'shares_diluted']
        mcs = ['cfo_da', 'cfo_change_in_working_capital', 'cf_cfo', 'capex']
        mbs = ['cash_and_equiv', 'st_debt', 'lt_debt']
        stats = mis + mcs + mbs
        dcf = self.metrics(ticker, stats, period)

        return dcf

    def metric(self, ticker, metric, period='FY-19:FY'):
        # IBM/revenue?period=FY-9:FY
        url = f'{self.link}data/{ticker}/{metric}?period={period}&api_key={self.api}'
        # url = f'https://public-api.quickfs.net/v1/data/IBM/revenue?period=FY&api_key={self.api}'
        r = requests.get(url).json()
        r = r['data']
        return r

    def metrics(self, ticker, *metrics, period='FY-19:FY'):

        # self.is_metrics
        # self.bs_metrics
        # self.cs_metrics
        # self.computed
        # self.medians
        # self.misc
        # self.statements
        # self.everything

        print('Zbieranie danych...')
        t = time.time()
        try:
            lf = self.metric(ticker, 'period_end_date', period=period)
        except:
            print('Limit punktów został wyczerpany!')
            quit()

        request_body = {"data": {
            # "roa" : "QFS(KO:US,roa,FY-2:FY)",
            # "roic" : "QFS(KO:US,roic,FY-2:FY)"
        }}

        frames = pd.DataFrame()
        for m in metrics:
            if type(m) == str:
                request_body['data'][m] = f'QFS({ticker.upper()},{m},{period})'

            if type(m) == pd.DataFrame:
                if m.equals(self.medians) and len(metrics) == 1:
                    frames = self.medians
                    break
                elif m.equals(self.everything) and len(metrics) > 1:
                    frames = self.everything
                    break
                else:
                    frames = pd.concat([frames, m])

            if type(m) == list:
                for thing in m:
                    request_body['data'][thing] = f'QFS({ticker.upper()},{thing},{period})'

        # print(frames)
        if not frames.empty:
            for frame in frames['metric']:
                request_body['data'][frame] = f'QFS({ticker.upper()},{frame},{period})'

        nr_of_rq = len(request_body['data'])
        # print(nr_of_rq)
        u = self.used()
        if u + nr_of_rq > self.limit:
            print(
                f'{self.limit - u} dostępnych punktów, {nr_of_rq} zostało zażądanych.')
            print('Nie wszystkie pozycje zostaną zwrócone!')

        header = {'x-qfs-api-key': self.api}

        # print(request_body)
        # return
        #####

        r = requests.post(
            "https://public-api.quickfs.net/v1/data/batch", json=request_body, headers=header).json()

        print('Pobrano dane!')

        r = r['data']
        prep = {}
        for thing in r:
            if r[thing] != [f'UnsupportedMetricError: {thing}']:
                prep[thing] = r[thing]

        prep = pd.DataFrame(prep)
        prep = prep.transpose().reset_index()
        prep.columns = ['metric'] + lf

        ev = self.everything
        df = ev.merge(prep, how='outer', on='metric')
        df = df.dropna()
        df = df.set_index('metric')

        tt = time.time()
        uu = self.used()
        print(f'Zakończono! ({round(tt-t)}s)')
        print(f'Zużyto {uu - u} punktów.')

        # print(df)
        return df

    def last_filling_date(self, ticker, annual=True):

        if annual == True:
            period = 'FY'
        else:
            period = 'FQ'

        date = self.metric(ticker, 'original_filing_date', period)[0]

        return date


if __name__ == '__main__':

    # self.is_metrics
    # self.bs_metrics
    # self.cs_metrics
    # self.computed
    # self.medians
    # self.misc
    # self.statements
    # self.everything
    api = 'api_to_qfs_here'

    stonk = qfs(api, 500)
    ticker = 'AAPL'
    data = stonk.metrics(ticker,['revenue', 'enterprise_value', 'market_cap'], period='FQ-3:FQ')
    data.to_excel('D:\skhynix.xlsx')
