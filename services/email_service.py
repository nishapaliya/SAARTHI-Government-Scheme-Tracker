import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app


def send_email(to_email, to_name, subject, html_content):
    """
    Send email using Brevo API
    """

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = {
        "name": current_app.config["BREVO_SENDER_NAME"],
        "email": current_app.config["BREVO_SENDER_EMAIL"]
    }

    receiver = [
        {
            "email": to_email,
            "name": to_name
        }
    ]

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=receiver,
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)
        return True

    except ApiException as e:
        print("Brevo Error:", e)
        return False