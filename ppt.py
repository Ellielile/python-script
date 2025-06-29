import os
import re
import pdfplumber
from datetime import datetime

padrao_data_emissao = re.compile(
    r"DATA DA EMISSÃO\s*\n\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)

while True:
    pasta = input("Digite o caminho da pasta onde estão os PDFs: ").strip()
    hoje = datetime.now()

    dados_arquivos = []

    for arquivo in os.listdir(pasta):
        nome_lower = arquivo.lower()
        if "aguardando entrega" in nome_lower or nome_lower.startswith("1"):
            continue

        if os.path.splitext(arquivo)[1].lower() == ".pdf":
            caminho_arquivo = os.path.join(pasta, arquivo)
            try:
                with pdfplumber.open(caminho_arquivo) as pdf:
                    texto = ""
                    for pagina in pdf.pages:
                        t = pagina.extract_text()
                        if t:
                            texto += t + "\n"
                    match = padrao_data_emissao.search(texto)
                    if match:
                        data_str = match.group(1)
                        data_doc = datetime.strptime(data_str, "%d/%m/%Y")
                        dados_arquivos.append((arquivo, data_doc))
                    else:
                        dados_arquivos.append((arquivo, None))
            except Exception as e:
                dados_arquivos.append((arquivo, None))

    dados_arquivos.sort(key=lambda x: x[1] if x[1] else datetime.max)

    for arquivo, data_doc in dados_arquivos:
        if data_doc:
            atraso = (hoje - data_doc).days
            if atraso > 0:
                print(
                    f"{arquivo}: data {data_doc.strftime('%d/%m/%Y')} - atrasado há {atraso} dias")
            else:
                print(
                    f"{arquivo}: data {data_doc.strftime('%d/%m/%Y')} - dentro do prazo (vence em {-atraso} dias)")
        else:
            print(f"{arquivo}: data não encontrada")

    resposta = input("\nQuer atualizar a leitura? (s/n): ").strip().lower()
    if resposta != "s":
        print("Vamos recomeçar.")
        break
