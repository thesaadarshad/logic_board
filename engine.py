import time
from dotenv import load_dotenv
import os


base_stages = [0.1,0.2,0.4,0.8,1.7,3.6,7.5,15.7]
fixed_call_percentages = [0.336,0.669,1.347,2.75,5.965,13.429,32.318,99.956]

available_splitters = [':','：']

signal_fileName = 'trading_signal.txt'


def getEnvValue(key):
    return os.environ.get(key)

class Engine():

    def __init__(self):
        load_dotenv()

    def getInvestmentChart(self, investment):

        chart = []
        accumulated = 0
        for x in range(8):
            stage = {}
            stage['stage'] = x+1
            stage['percentage'] = fixed_call_percentages[x]
            stage['buy'] = round(((investment-accumulated) / 100) * fixed_call_percentages[x], 1)
            accumulated = accumulated+stage['buy']
            chart.append(stage)
        return chart

    def parse_text(self):
        parsed_message = {}
        with open(signal_fileName) as file:
            for line in file:
                line = line.strip()
                if len(line) > 1:

                    if ":" in line:
                        (key, value) = line.split(":")
                        parsed_message[key] = value.replace(" USDT", "").strip()

                    if "：" in line:
                        (key, value) = line.split("：")
                        parsed_message['Select'] = value.strip()

        return parsed_message


    def run(self):
        print("--Start Trade--")

        print(f"Username: {getEnvValue('HFC_USER')}")
        investment = int(getEnvValue('HFC_INVESTMENT'))
        print(f"Investment: {investment}")
        investmentChart = self.getInvestmentChart(investment)
        print("Investment Chart:")
        print(investmentChart)

        print('Waiting for Signals')
        originalTime = 0

        while (True):
            if (os.path.getmtime(signal_fileName) > originalTime):
                print("Reading Messages")
                originalTime = os.path.getmtime(signal_fileName)
                parsed_message = self.parse_text()

                if float(parsed_message['Amount']) in base_stages:
                    found_stage_number = base_stages.index(float(parsed_message['Amount']))
                    print("##")
                    print(f"Stage {found_stage_number+1} Call Found.")
                    print(f"Call: {parsed_message['Select']}")
                    print(f"Target Price: {investmentChart[found_stage_number]['buy']}")
                    print("##")
            else:
                print('No New Messages')
            time.sleep(5)


if __name__ == '__main__':
    engine = Engine()
    engine.run()
