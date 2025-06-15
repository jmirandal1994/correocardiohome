from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ajusta tus credenciales SMTP aquí:
EMAIL_ADDRESS = 'contacto@cardiohome.cl'
EMAIL_PASSWORD = 'TU_CONTRASEÑA_SMTP_O_APP_PASSWORD'
SMTP_SERVER = 'smtp.tuservidor.com'  # ej: smtp.gmail.com o el de tu hosting
SMTP_PORT = 587  # usualmente 587 (TLS) o 465 (SSL)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df = pd.read_excel(filepath)
        data = df.to_dict(orient='records')

        return render_template('index.html', data=data)

    return render_template('index.html', data=None)

@app.route('/send_emails', methods=['POST'])
def send_emails():
    data = request.form.get('data')
    import json
    records = json.loads(data)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        for row in records:
            msg = EmailMessage()
            msg['Subject'] = 'Solicitud de Estado de Conformidad'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = row['Correo']

            body = f"""
Estimados {row['Colegio']},

Solicitamos su apoyo para enviar el estado de conformidad de los estudiantes evaluados:

- Neurología: {row['Neurología']}
- Medicina Familiar: {row['Medicina Familiar']}

Saludos cordiales,
CardioHome
            """
            msg.set_content(body)
            smtp.send_message(msg)

    return "Correos enviados correctamente."

if __name__ == '__main__':
    app.run(debug=True)
