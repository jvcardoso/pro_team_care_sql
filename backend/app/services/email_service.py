"""
Serviço de envio de emails.

Utiliza smtp4dev em desenvolvimento e SMTP real em produção.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        """Inicializa configurações de email"""
        # smtp4dev em desenvolvimento
        self.smtp_host = "192.168.11.64"
        self.smtp_port = 25  # smtp4dev usa porta 25 por padrão
        self.from_email = "noreply@proteamcare.com.br"
        self.from_name = "Pro Team Care"
    
    async def send_password_reset_email(
        self,
        to_email: str,
        to_name: str,
        reset_token: str,
        expires_at: str
    ) -> bool:
        """
        Envia email de reset de senha.
        
        Args:
            to_email: Email do destinatário
            to_name: Nome do destinatário
            reset_token: Token de reset
            expires_at: Data/hora de expiração
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # URL do frontend (token como path parameter)
            reset_url = f"http://192.168.11.83:3001/reset-password/{reset_token}"
            
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = "Recuperação de Senha - Pro Team Care"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Corpo do email em texto simples
            text_body = f"""
Olá {to_name},

Você solicitou a recuperação de senha da sua conta no Pro Team Care.

Para redefinir sua senha, clique no link abaixo:
{reset_url}

Este link expira em: {expires_at}

Se você não solicitou esta recuperação, ignore este email.

---
Pro Team Care
Sistema de Gestão de Home Care
            """.strip()
            
            # Corpo do email em HTML
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #2563eb;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
        .warning {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 10px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Recuperação de Senha</h1>
        </div>
        <div class="content">
            <p>Olá <strong>{to_name}</strong>,</p>
            
            <p>Você solicitou a recuperação de senha da sua conta no <strong>Pro Team Care</strong>.</p>
            
            <p>Para redefinir sua senha, clique no botão abaixo:</p>
            
            <div style="text-align: center;">
                <a href="{reset_url}" class="button">Redefinir Senha</a>
            </div>
            
            <p>Ou copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; background-color: #f3f4f6; padding: 10px; border-radius: 3px;">
                {reset_url}
            </p>
            
            <div class="warning">
                <strong>⏰ Atenção:</strong> Este link expira em <strong>{expires_at}</strong>
            </div>
            
            <p>Se você não solicitou esta recuperação, ignore este email. Sua senha permanecerá inalterada.</p>
        </div>
        <div class="footer">
            <p>Pro Team Care - Sistema de Gestão de Home Care</p>
            <p>Este é um email automático, não responda.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            # Anexar ambas as versões
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(html_body, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)
            
            # Enviar email via smtp4dev
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # smtp4dev não requer autenticação
                server.send_message(message)
            
            print(f"✅ Email de reset enviado para {to_email} via smtp4dev")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            # Em caso de erro, ainda imprime no console (fallback)
            print(f"""
            ═══════════════════════════════════════════════════════
            📧 EMAIL DE RESET DE SENHA (FALLBACK - ERRO NO SMTP)
            ═══════════════════════════════════════════════════════
            Para: {to_email}
            Nome: {to_name}
            
            Link de reset:
            http://localhost:3000/reset-password?token={reset_token}
            
            Token expira em: {expires_at}
            
            Erro: {str(e)}
            ═══════════════════════════════════════════════════════
            """)
            return False
    
    async def send_welcome_email(
        self,
        to_email: str,
        to_name: str,
        temporary_password: Optional[str] = None
    ) -> bool:
        """
        Envia email de boas-vindas para novo usuário.
        
        Args:
            to_email: Email do destinatário
            to_name: Nome do destinatário
            temporary_password: Senha temporária (opcional)
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = "Bem-vindo ao Pro Team Care"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Corpo do email em texto simples
            text_body = f"""
Olá {to_name},

Bem-vindo ao Pro Team Care!

Sua conta foi criada com sucesso.

Email: {to_email}
"""
            
            if temporary_password:
                text_body += f"""
Senha temporária: {temporary_password}

Por favor, faça login e altere sua senha.
"""
            
            text_body += """
---
Pro Team Care
Sistema de Gestão de Home Care
            """.strip()
            
            # Corpo do email em HTML
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #10b981;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .credentials {{
            background-color: #f3f4f6;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Bem-vindo!</h1>
        </div>
        <div class="content">
            <p>Olá <strong>{to_name}</strong>,</p>
            
            <p>Bem-vindo ao <strong>Pro Team Care</strong>!</p>
            
            <p>Sua conta foi criada com sucesso.</p>
            
            <div class="credentials">
                <p><strong>Email:</strong> {to_email}</p>
"""
            
            if temporary_password:
                html_body += f"""
                <p><strong>Senha temporária:</strong> {temporary_password}</p>
                <p style="color: #dc2626; margin-top: 10px;">
                    ⚠️ Por favor, faça login e altere sua senha.
                </p>
"""
            
            html_body += """
            </div>
            
            <p>Acesse o sistema em: <a href="http://localhost:3000">http://localhost:3000</a></p>
        </div>
        <div class="footer">
            <p>Pro Team Care - Sistema de Gestão de Home Care</p>
            <p>Este é um email automático, não responda.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            # Anexar ambas as versões
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(html_body, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)
            
            # Enviar email via smtp4dev
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(message)
            
            print(f"✅ Email de boas-vindas enviado para {to_email} via smtp4dev")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email de boas-vindas: {str(e)}")
            return False
