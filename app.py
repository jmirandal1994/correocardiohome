from flask import Flask, render_template, request, Response
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import json

app = Flask(__name__)

# Usar carpeta temporal en Render
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Leer credenciales desde variables de entorno
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
    try:
        data = request.form.get('data')
        if not data:
            return Response("No se recibió data para enviar.", status=400)

        records = json.loads(data)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS.strip(), EMAIL_PASSWORD.strip())

            for row in records:
                to_email = str(row.get('Correo', '')).strip()
                colegio = str(row.get('Colegio', '')).strip()
                neuro = str(row.get('Neurología', '')).strip()
                medicina = str(row.get('Medicina Familiar', '')).strip()

                if not to_email:
                    continue  # Saltar si falta correo

                msg = EmailMessage()
                msg['Subject'] = 'Solicitud de Estado de Conformidad'
                msg['From'] = EMAIL_ADDRESS.strip()
                msg['To'] = to_email

                body = f"""
Estimados equipo de {colegio},

Junto con saludarles, solicitamos su colaboración para remitir el estado de conformidad correspondiente a los estudiantes evaluados por nuestro equipo:

- Evaluados en Neurología: {neuro}
- Evaluados en Medicina Familiar: {medicina}

Agradecemos de antemano su apoyo y disposición. Favor enviarlo dentro de las próximas 24 horas hábiles a más tardar.

Quedamos atentos a cualquier consulta.

Saludos cordiales,
Equipo CardioHome
                """
                msg.set_content(body)
                smtp.send_message(msg)

        return "✅ Correos enviados correctamente."

    except Exception as e:
        print(f"Error interno: {e}")
        return Response(f"❌ Error interno: {e}", status=500)

if __name__ == '__main__':
    app.run(debug=True)
