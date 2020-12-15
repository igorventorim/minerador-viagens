from scrapy import cmdline
import os
from spreadsheets import SpreadSheets
from dotenv import load_dotenv
import time
import subprocess
import pandas as pd
from datetime import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import glob


def get_config_data_by_spreadsheet():
    load_dotenv()
    SCOPES = [os.getenv('SCOPE')]
    SAMPLE_SPREADSHEET_ID_input = os.getenv('SAMPLE_SPREADSHEET_ID')
    SAMPLE_RANGE_NAME = os.getenv('SAMPLE_RANGE_CONFIG')
    spread_sheats = SpreadSheets(
        SCOPES, SAMPLE_SPREADSHEET_ID_input, SAMPLE_RANGE_NAME)
    spread_sheats.create_service(os.path.abspath(
        os.getcwd())+'/credentials.json', 'sheets', 'v4', os.path.abspath(
        os.getcwd())+'/token.pickle')
    spread_sheats.read_sheets()

    return spread_sheats.df


def write_df(parameters, time_elapsed):
    try:
        load_dotenv()
        SCOPES = [os.getenv('SCOPE')]
        SAMPLE_SPREADSHEET_ID_input = os.getenv('SAMPLE_SPREADSHEET_ID')
        SAMPLE_RANGE_NAME = os.getenv('SAMPLE_RANGE_DATA')
        spread_sheats = SpreadSheets(
            SCOPES, SAMPLE_SPREADSHEET_ID_input, SAMPLE_RANGE_NAME)
        spread_sheats.create_service(os.path.abspath(
            os.getcwd())+'/credentials.json', 'sheets', 'v4', os.path.abspath(
            os.getcwd())+'/token.pickle')
        spread_sheats.read_sheets()

        full_df = spread_sheats.df
        today = datetime.today().strftime("%d-%m-%y %H:%M")
        data = data = {
            'Data da execução': [today],
            'Parâmetros': [parameters],
            'Tempo de Execução': [time_elapsed]
        }
        df_log = pd.DataFrame(
            data, columns=['Data da execução',	'Parâmetros', 'Tempo de Execução'])
        frames = [full_df, df_log]
        result = pd.concat(frames)
        result.fillna('', inplace=True)
        spread_sheats.df = result

        spread_sheats.export_data_to_sheets()
    except Exception as e:
        print(e)
        print("Erro: Ocorreu um erro ao gravar o arquivo.")


def send_mail(subject, body):
    load_dotenv()
#    server = smtplib.SMTP_SSL(os.getenv('SERVIDOR_EMAIL'), 465)
    context = ssl.create_default_context()
    server = smtplib.SMTP(os.getenv('SERVIDOR_EMAIL'), 587)
    server.ehlo()
    server.ehlo()
    server.starttls(context=context)
    server.login(os.getenv('LOGIN_EMAIL'), os.getenv('PASSWORD_EMAIL'))

    fromaddr = os.getenv('LOGIN_EMAIL')
    toaddr = os.getenv('EMAIL_DESTINATARIO')
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', "utf-8"))

    for filename in glob.glob("*.csv"):
        attachment = open(os.getcwd()+"/"+filename, 'rb')
        if(attachment != None):
            try:
                filename = os.path.basename(attachment.name)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                "attachment; filename= %s" % filename)
                msg.attach(part)
            except:
                print("Erro ao adicionar o anexo.")

    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()


if __name__ == '__main__':

    df = get_config_data_by_spreadsheet()
    if df is not None:
        for i in range(0, df.shape[0]):
            start = time.time()
            print("Gerando input: "+str(i+1))

            city = df['cidade'][i]
            group_adults = df['adultos'][i]
            group_children = df['crianças'][i]
            checkin_monthday = df['check-in'][i].split('-')[0]
            checkin_month = df['check-in'][i].split('-')[1]
            checkin_year = df['check-in'][i].split('-')[2]
            checkout_monthday = df['check-out'][i].split('-')[0]
            checkout_month = df['check-out'][i].split('-')[1]
            checkout_year = df['check-out'][i].split('-')[2]

            parameters = "\'cidade\': {}, \'check-in\': {}-{}-{}, \'check-out\':{}-{}-{}, \'adultos\':{}, \'crianças\':{}".format(
                city, checkin_monthday, checkin_month, checkin_year, checkout_monthday, checkout_month, checkin_year, group_adults, group_children)

            cmd = "scrapy crawl Booking -a city={} -a group_adults={} -a group_children={} -a checkin_monthday={} -a checkin_month={} -a checkin_year={} -a checkout_monthday={} -a checkout_month={} -a checkout_year={} -o output_booking_{}_{}.csv".format(
                city, group_adults, group_children, checkin_monthday, checkin_month, checkin_year, checkout_monthday, checkout_month, checkout_year, str(i+1), datetime.now().strftime("%d%m%y%H%M"))

            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            process.wait()

            time_elapsed = (time.time() - start)
            write_df(parameters, time_elapsed)

            time.sleep(60)

        subject = "Dados extraídos pelo minerador Booking"
        body = "Segue em anexo o dados extraídos pelo minerador booking. Data da consulta {}/{}/{}.\n*Obs.: Este e-mail é enviado automaticamente.".format(
            datetime.now().day, datetime.now().month, datetime.now().year)
        send_mail(subject, body)

        process = subprocess.Popen(
            'mv *.csv backup/', shell=True, stdout=subprocess.PIPE)
        process.wait()

    else:
        cmdline.execute("scrapy crawl Booking -o booking.json".split())
