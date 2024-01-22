from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from telegram import Bot
import pyautogui
import re
import shutil
import asyncio
import csv
import base64
import uuid
import os

# Abre o arquivo CSV e obter a última DataMessageId
csv_filename = 'punter/mensagens.csv'
ultima_data_message_id = None

with open(csv_filename, 'r') as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:
        ultima_data_message_id = row['data-message-id']

# ByPass para testes
date = 'Today'
print(ultima_data_message_id,'-',date)

# Configurações
url_canal_origem = 'https://web.telegram.org/a/#-1001822192935' 
telegram_token = '6545127338:AAHVYe1X3Ij1WTytzmFhAdEY05sBoGIJXfA'
grupo_id = -4047018375

# Caminho para o perfil personalizado do Chrome
profile_path = r'C:\Users\Leonardo\AppData\Local\Google\Chrome\User Data\Default'

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument('--user-data-dir=' + profile_path)
chrome_options.add_argument('--profile-directory=PerfilPadrao')
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)

driver.get(url_canal_origem)
driver.implicitly_wait(40)
time.sleep(2)
screen_width, screen_height = pyautogui.size()

# Calcula as coordenadas do centro da tela
center_x, center_y = screen_width // 2, screen_height // 2

# Simula um clique do mouse no centro da tela
pyautogui.click(center_x, center_y)
time.sleep(1)
pyautogui.press('esc')
time.sleep(1)
# Simula 5 pressionamentos da tecla Page Up
for _ in range(5):
    pyautogui.press('pageup')
    time.sleep(1)  # Aguarda um segundo entre as teclas para evitar ações rápidas demais

# Simula 5 pressionamentos da tecla Page Down
for _ in range(7):
    pyautogui.press('pagedown')
    time.sleep(1)  # Aguarda um segundo entre as teclas para evitar ações rápidas demais

time.sleep(10)

div_element = driver.find_element('xpath', f'//div[@class="message-date-group" and .//span[text()="{date}"]]')

# Obtém o conteúdo HTML da div
div_html = div_element.get_attribute('outerHTML')

# Salva o conteúdo HTML em um arquivo
with open('punter/output.html', 'w', encoding='utf-8') as file:
    file.write(div_html)

def extrair_informacoes(html):
    soup = BeautifulSoup(html, 'html.parser')

    with open('punter/indice_bruto.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['data-message-id', 'message-text', 'link_bet', 'link_img_bet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        messages = soup.find_all('div', class_='message-list-item')

        for message in messages:
            message_id = message.get('data-message-id')

            text_content = message.find('div', class_='text-content')
            if text_content:
                message_text = text_content.get_text(strip=True)
            else:
                message_text = None

            link_bet = None
            link_img_bet = None

            if message.find('a', class_='text-entity-link'):
                link_bet = message.find('a', class_='text-entity-link')['href']

            img_tag = message.find('img', class_='full-media')
            if img_tag and 'src' in img_tag.attrs:
                link_img_bet = img_tag['src']

            writer.writerow({
                'data-message-id': message_id,
                'message-text': message_text,
                'link_bet': link_bet,
                'link_img_bet': link_img_bet
            })

# Carregar o código HTML do arquivo
with open('punter/output.html', 'r', encoding='utf-8') as file:
    codigo_html = file.read()

extrair_informacoes(codigo_html)

input_file = 'punter/indice_bruto.csv'
output_file = 'punter/indice.csv'

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # Use expressão regular para remover qualquer parte do link na coluna 'message-text'
        row['message-text'] = re.sub(r'https[^\s]*', '', row['message-text'])
        writer.writerow(row)

os.remove('punter/indice_bruto.csv')

driver.execute_script("window.open('', '_blank');")
driver.switch_to.window(driver.window_handles[1])

def salvar_imagem(html_content, nome_pasta):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Encontrar a URL da imagem
    img_tag = soup.find('img')
    img_url = img_tag['src']
    
    # Obter os dados base64 da imagem
    img_data = driver.execute_script(f"return fetch('{img_url}').then(response => response.blob()).then(blob => new Promise((resolve, reject) => {{const reader = new FileReader();reader.onloadend = () => resolve(reader.result);reader.onerror = reject;reader.readAsDataURL(blob);}}));")
    
    # Decodificar os dados base64 e salvar a imagem com um nome aleatório
    img_data = img_data.split(',')[1]
    nome_arquivo = os.path.join(nome_pasta, f"{uuid.uuid4().hex}.jpg")
    with open(nome_arquivo, 'wb') as file:
        file.write(base64.b64decode(img_data))
    
    return nome_arquivo

# Criar uma pasta para salvar as punter/imagens
if not os.path.exists('punter/imagens'):
    os.makedirs('punter/imagens')

# Abrir o arquivo CSV e criar um novo arquivo CSV para a saída
with open('punter/indice.csv', 'r') as input_file, open('punter/mensagens.csv', 'w', newline='') as output_file:
    # Configurar o leitor e escritor CSV
    reader = csv.DictReader(input_file)
    
    # Remover a coluna 'link_img_bet' dos fieldnames
    fieldnames = [field for field in reader.fieldnames if field != 'link_img_bet']
    fieldnames += ['Local']
    
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()

    # Lista temporária para armazenar as linhas atualizadas
    updated_rows = []

    # Iterar sobre as linhas do arquivo CSV
    for row in reader:
        # Verificar se há um link de imagem disponível
        link_img = row['link_img_bet']
        if link_img:
            # Abrir a URL usando o Selenium
            driver.get(link_img)
            
            # Extrair o conteúdo da página
            html_content = driver.page_source
            
            # Salvar a imagem usando a função modificada
            local = salvar_imagem(html_content, 'punter/imagens')
            
            # Adicionar o valor corrigido à lista temporária
            row['Local'] = local
            
        else:
            # Se não houver link de imagem, deixar a coluna 'Local' vazia
            row['Local'] = ''
        
        # Remover a coluna 'link_img_bet' antes de adicionar à lista
        del row['link_img_bet']
        
        updated_rows.append(row.copy())

    # Escrever as linhas atualizadas no novo arquivo CSV
    writer.writerows(updated_rows)

# Fechar o driver do Selenium
driver.quit()

os.remove('punter/output.html')
os.remove('punter/indice.csv')

def ler_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

async def enviar_mensagens(telegram_token, grupo_id, dados_csv, ultima_data_message_id):
    # Inicialize o bot do Telegram
    bot = Bot(token=telegram_token)

    # Itere sobre as linhas dos dados do CSV
    for row in dados_csv:
        # Obtenha o conteúdo da coluna 'LinkBet', 'Local' e 'DataMessageId'
        link_bet = row.get('link_bet', '')
        local_imagem = row.get('Local', '')
        data_message_id = row.get('data-message-id', '')
        message_text = row.get('message-text', '')

    if data_message_id and int(data_message_id) > int(ultima_data_message_id):
        await bot.send_message(chat_id=grupo_id, text='Atenção - Entradas do Grupo Punter Fut')

        # Verifique se o DataMessageId é maior que o valor salvo
        if data_message_id and int(data_message_id) > int(ultima_data_message_id):
            # Construa a mensagem
            mensagem = f"{link_bet.encode('utf-8').decode('utf-8')}" if link_bet else ""
            texto = f"{message_text.encode('utf-8').decode('utf-8')}" if message_text else ""

            # Envie a mensagem e a imagem juntas para o grupo
            if local_imagem:
                await bot.send_photo(chat_id=grupo_id, photo=open(local_imagem, 'rb'), caption=f"{texto}\n\n{mensagem}", parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=grupo_id, text=f"{texto}\n\n{mensagem}", parse_mode='Markdown')

            # Aguarde um intervalo (por exemplo, 1 segundo) entre cada mensagem para evitar bloqueios
            await asyncio.sleep(1)
    if data_message_id and int(data_message_id) > int(ultima_data_message_id):
        await bot.send_message(chat_id=grupo_id, text='Envio finalizado')

# Caminho do arquivo CSV
arquivo = 'punter/mensagens.csv'

# Ler os dados do CSV
dados_csv = list(csv.DictReader(open(arquivo, 'r')))

# Crie um loop de eventos e execute a função assíncrona
asyncio.run(enviar_mensagens(telegram_token, grupo_id, dados_csv, ultima_data_message_id))

print('Entradas enviadas')
try:
    shutil.rmtree('punter/imagens')
    print('Arquivos apagados')
except:
    print('Arquivos não deletados.')
print(ultima_data_message_id)