import os

import dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

def send_email(to,title,message):
    load_dotenv()
    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "DOS Updates"
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] =to

    # Plain-text fallback
    text = """\
    Hi,
    This is a plain-text fallback message.
    """

    # HTML version
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title></title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }

        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .logo {
            padding: 0px;
            background-color: white;
            text-align: center;
        }

        .logo-squares {
            display: flex;
            justify-content: center;
            margin: 0 auto;
        }

        .logo-square {
            width: 12px;
            height: 12px;
            margin-right: 1px;
            margin-bottom: 1px;
        }

        .logo-square:nth-child(1) { background-color: #f25022; }
        .logo-square:nth-child(2) { background-color: #7fba00; }
        .logo-square:nth-child(3) { background-color: #00a4ef; }
        .logo-square:nth-child(4) { background-color: #ffb900; }

        .logo-text {
            font-size: 20px;
            font-weight: 400;
            color: #737373;
            vertical-align: top;
            margin-left: 8px;
        }

        .header-banner {
            background-color: #0cb04a;
            color: white;
            padding: 10px 10px;
            text-align: center;
        }

        .header-title {
            font-size: 28px;
            font-weight: 300;
            margin: 0;
        }

        .email-content {
            padding: 30px;
            color: #323130;
        }

        .greeting {
            margin-bottom: 20px;
            font-size: 16px;
        }

        .content-paragraph {
            margin-bottom: 20px;
            font-size: 14px;
            line-height: 1.6;
        }

        .content-link {
            color: #0cb04a;
            text-decoration: underline;
        }

        .content-link:hover {
            text-decoration: none;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin: 30px 0;
            flex-wrap: wrap;
        }

        .action-button {
            background-color: #0cb04a;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            flex: 1;
            text-align: center;
            min-width: 150px;
        }

        .action-button:hover {
            background-color: #0cb04a;
        }

        .footer {
            background-color: #f8f8f8;
            padding: 20px;
            font-size: 12px;
            color: #737373;
            line-height: 1.5;
        }

        .footer-text {
            margin-bottom: 10px;
        }

        .footer-link {
            color: #737373;
            text-decoration: underline;
        }

        .footer-address {
            margin: 15px 0;
        }

        .footer-logo {
            margin-top: 15px;
        }

        @media (max-width: 600px) {
            .action-buttons {
                flex-direction: column;
            }

            .action-button {
                margin-bottom: 10px;
            }

            .header-title {
                font-size: 24px;
            }

            .email-content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
<div class="email-container">
    <!-- Microsoft Logo Header -->
    <div class="logo">
        <div class="logo-squares">
<!--            <img src="--><?php //echo base_url() . '/uploads/image/uzimalogo.jpeg'?><!--" width="120" height="120">-->
            <!--img src="https://cdn.tracxn.com/images/seo/social/companies/uzima-health-overview-1709838620324.webp" width="120" height="120"-->
        </div>
    </div>

    <!-- Header Banner -->
    <div class="header-banner">
        <h1 class="header-title">"""+title+"""</h1>
    </div>

    <!-- Email Content -->
    <div class="email-content">
        <div class="greeting"></div>

        <div class="content-paragraph">
            """+message+"""
        </div>

    </div>

    <!-- Footer -->
    <div class="footer">
        <div class="footer-text">This email was sent from an unmonitored mailbox.</div>
    </div>
</div>
</body>
</html>
    """

    # Attach both plain and HTML versions
    # msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send the email
    try:
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT')) as server:
            server.starttls()  # Secure connection
            server.login(os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'))
            server.sendmail(os.getenv('SENDER_EMAIL'), to, msg.as_string())
            print("[+] Email sent successfully")
    except Exception as e:
        print("[-] Failed to send email:", e)