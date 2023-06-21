from flask import Flask, render_template, request, redirect, url_for
import stripe
import sendgrid
from sendgrid.helpers.mail import Mail
import os
from flask import current_app

app = Flask(__name__)

stripe_keys = {
    "secret_key": os.environ.get("STRIPE_SECRET_KEY"),
    "publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
}

stripe.api_key = stripe_keys["secret_key"]

sendgrid_api_key = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))  # SendGrid API key

@app.route('/')
def index():
   
    return render_template('index.html')

@app.route('/payment', methods=['POST'])
def payment():
    amount = request.form['amount']
    return render_template('payment.html', amount=amount)

@app.route('/charge', methods=['POST'])
def charge():
    amount = int(request.form['amount']) * 0.034  # Convert amount to cents
    customer = stripe.Customer.create(
        email=request.form['email'],
        source=request.form['stripeToken']
    )

    stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='inr',
        description='Giving a little is better than not giving at all'
    )

    # Generate invoice
    invoice = stripe.Invoice.create(
        customer=customer.id,
        auto_advance=True
    )

    # Send email with payment details
    send_email(request.form['email'], invoice.total )

    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

def send_email(email, amount):
    message = Mail(
        from_email='vijayapyriya1892003@gmail.com',  # email
        to_emails=email,
        subject='Payment Received',
        plain_text_content=f'Thank you for your payment. Amount: {amount}'
    )

    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
    response = sg.send(message)

    return response

if __name__ == '__main__':
    app.run(debug=True)
