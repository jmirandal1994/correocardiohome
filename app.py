from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os

# ✅ Toma las credenciales desde las Variables de Entorno
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT'))

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
Estimados equipo de {row['Colegio']},

Junto con saludarles, solicitamos su colaboración para remitir el estado de conformidad correspondiente a los estudiantes evaluados por nuestro equipo:

- Evaluados en Neurología: {row['Neurología']}
- Evaluados en Medicina Familiar: {row['Medicina Familiar']}

Agradecemos de antemano su apoyo y disposición, Favor enviarlo dentro de las proximas 24 horas habiles a mas tardar.

Quedamos atentos a cualquier consulta.

Saludos cordiales,
Equipo CardioHome
            """
            msg.set_content(body)
            smtp.send_message(msg)

    return "Correos enviados correctamente."

if __name__ == '__main__':
    app.run(debug=True)
