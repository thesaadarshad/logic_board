import time
from dotenv import load_dotenv
import os


base_stages = [0.1,0.2,0.4,0.8,1.7,3.6,7.5,15.7]
fixed_call_percentages = [0.336,0.669,1.347,2.75,5.965,13.429,32.318,99.956]

signal_fileName = 'trading_signal.txt'


def getEnvValue(key):
    return os.environ.get(key)

class Engine():

    def __init__(self):
        load_dotenv()
        self.original_time = 0

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

    def parse_text(self, message):
        parsed_message = {}
        for line in message:
            line = line.strip()
            if len(line) > 1:
                if ":" in line:
                    (key, value) = line.split(":")
                    parsed_message[key] = value.replace(" USDT", "").strip()
                if "：" in line:
                    (key, value) = line.split("：")
                    parsed_message['Select'] = value.strip()
        return parsed_message

    def CheckForNewMessages(self):
        if os.path.getmtime(signal_fileName) > self.original_time:
            self.original_time = os.path.getmtime(signal_fileName)
            return True
        else:
            return False

    def get_signal_message(self):
        file = open(signal_fileName, 'r')
        message = file.readlines()
        return message

    def run(self):

        investment = int(getEnvValue('HFC_INVESTMENT'))
        investmentChart = self.getInvestmentChart(investment)


        print("--Start Trade--")
        print(f"Username: {getEnvValue('HFC_USER')}")
        print(f"Investment: {investment}")
        print("Investment Chart:")
        print(investmentChart)

        print('Starting Engine')
        print("###############")
        while (True):
            if (self.CheckForNewMessages()):
                print("New Message Found")

                signal_message = self.get_signal_message()

                if len(signal_message) < 1:
                    exit('no input message found')

                parsed_message = self.parse_text(signal_message)

                if float(parsed_message['Amount']) in base_stages:
                    found_stage_number = base_stages.index(float(parsed_message['Amount']))
                    print(f"-stage {found_stage_number+1} Call Found.")
                    print(f"-call: {parsed_message['Select']}")
                    print(f"-target price: {investmentChart[found_stage_number]['buy']}")
            else:
                print('No New Messages. Refreshing...')
            time.sleep(5)


if __name__ == '__main__':
    engine = Engine()
    engine.run()
