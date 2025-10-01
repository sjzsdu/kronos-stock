# -*- coding: utf-8 -*-
"""
邮件服务
处理用户注册验证邮件、密码重置邮件等邮件发送功能
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import bool
from datetime import datetime
from flask import current_app, render_template_string
import logging


class EmailService:
    """邮件服务类"""
    
    @staticmethod
    def send_verification_email(email: str, token: str) -> bool:
        """
        发送邮箱验证邮件
        
        Args:
            email: 用户邮箱
            token: 验证令牌
            
        Returns:
            发送是否成功
        """
        try:
            subject = "Kronos 股票预测 - 邮箱验证"
            
            # 邮件模板
            html_template = """
            <html>
            <body>
                <h2>欢迎注册 Kronos 股票预测平台</h2>
                <p>感谢您注册我们的服务！请点击下面的链接验证您的邮箱地址：</p>
                <p><a href="{{ verification_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">验证邮箱</a></p>
                <p>如果按钮无法点击，请复制以下链接到浏览器：</p>
                <p>{{ verification_url }}</p>
                <p>此链接将在24小时后过期。</p>
                <br>
                <p>如果您没有注册此账户，请忽略此邮件。</p>
                <p>Kronos 股票预测团队</p>
            </body>
            </html>
            """
            
            # 构建验证链接
            verification_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/auth/verify-email?token={token}"
            
            html_content = render_template_string(html_template, verification_url=verification_url)
            
            return EmailService._send_email(email, subject, html_content)
            
        except Exception as e:
            current_app.logger.error(f"发送验证邮件失败: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, token: str) -> bool:
        """
        发送密码重置邮件
        
        Args:
            email: 用户邮箱
            token: 重置令牌
            
        Returns:
            发送是否成功
        """
        try:
            subject = "Kronos 股票预测 - 密码重置"
            
            # 邮件模板
            html_template = """
            <html>
            <body>
                <h2>Kronos 股票预测 - 密码重置</h2>
                <p>您请求重置您的账户密码。请点击下面的链接来重置密码：</p>
                <p><a href="{{ reset_url }}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">重置密码</a></p>
                <p>如果按钮无法点击，请复制以下链接到浏览器：</p>
                <p>{{ reset_url }}</p>
                <p>此链接将在1小时后过期。</p>
                <br>
                <p>如果您没有请求密码重置，请忽略此邮件。您的密码不会被更改。</p>
                <p>为了保护您的账户安全，请勿将此邮件转发给他人。</p>
                <p>Kronos 股票预测团队</p>
            </body>
            </html>
            """
            
            # 构建重置链接
            reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/auth/reset-password?token={token}"
            
            html_content = render_template_string(html_template, reset_url=reset_url)
            
            return EmailService._send_email(email, subject, html_content)
            
        except Exception as e:
            current_app.logger.error(f"发送密码重置邮件失败: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email: str, full_name: str) -> bool:
        """
        发送欢迎邮件
        
        Args:
            email: 用户邮箱
            full_name: 用户全名
            
        Returns:
            发送是否成功
        """
        try:
            subject = "欢迎加入 Kronos 股票预测平台"
            
            # 邮件模板
            html_template = """
            <html>
            <body>
                <h2>欢迎加入 Kronos 股票预测平台，{{ full_name }}！</h2>
                <p>恭喜您成功注册！现在您可以享受以下功能：</p>
                <ul>
                    <li>🔮 智能股票价格预测</li>
                    <li>📊 个性化投资组合分析</li>
                    <li>⭐ 股票关注列表管理</li>
                    <li>📈 历史预测记录追踪</li>
                    <li>🔔 实时价格提醒</li>
                </ul>
                <p><a href="{{ dashboard_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">开始使用</a></p>
                <br>
                <p>如有任何问题，请随时联系我们的客服团队。</p>
                <p>祝您投资顺利！</p>
                <p>Kronos 股票预测团队</p>
            </body>
            </html>
            """
            
            # 构建仪表板链接
            dashboard_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/dashboard"
            
            html_content = render_template_string(html_template, 
                                                full_name=full_name, 
                                                dashboard_url=dashboard_url)
            
            return EmailService._send_email(email, subject, html_content)
            
        except Exception as e:
            current_app.logger.error(f"发送欢迎邮件失败: {str(e)}")
            return False
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件的内部方法
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            
        Returns:
            发送是否成功
        """
        try:
            # 获取邮件配置
            smtp_server = current_app.config.get('MAIL_SERVER', 'localhost')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            smtp_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@kronos-stock.com')
            
            # 如果在测试环境或开发环境，只记录日志不实际发送
            if current_app.config.get('TESTING') or current_app.config.get('MAIL_SUPPRESS_SEND'):
                current_app.logger.info(f"模拟发送邮件到 {to_email}: {subject}")
                return True
            
            # 创建邮件对象
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = from_email
            message['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # 发送邮件
            if smtp_server and smtp_username and smtp_password:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    if smtp_use_tls:
                        server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(message)
                
                current_app.logger.info(f"邮件发送成功到 {to_email}")
                return True
            else:
                # 配置不完整，只记录日志
                current_app.logger.warning(f"邮件配置不完整，跳过发送邮件到 {to_email}")
                return True
                
        except Exception as e:
            current_app.logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    @staticmethod
    def send_security_alert(email: str, event: str, ip_address: str = None) -> bool:
        """
        发送安全提醒邮件
        
        Args:
            email: 用户邮箱
            event: 安全事件
            ip_address: IP地址
            
        Returns:
            发送是否成功
        """
        try:
            subject = "Kronos 股票预测 - 安全提醒"
            
            # 邮件模板
            html_template = """
            <html>
            <body>
                <h2>安全提醒</h2>
                <p>您的账户发生了以下安全事件：</p>
                <p><strong>事件：</strong>{{ event }}</p>
                <p><strong>时间：</strong>{{ timestamp }}</p>
                {% if ip_address %}
                <p><strong>IP地址：</strong>{{ ip_address }}</p>
                {% endif %}
                <br>
                <p>如果这不是您本人的操作，请立即：</p>
                <ol>
                    <li>更改您的密码</li>
                    <li>检查账户活动</li>
                    <li>联系客服团队</li>
                </ol>
                <p><a href="{{ security_url }}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">查看账户安全</a></p>
                <p>Kronos 股票预测团队</p>
            </body>
            </html>
            """
            
            # 构建安全页面链接
            security_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/profile/security"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            html_content = render_template_string(html_template, 
                                                event=event,
                                                timestamp=timestamp,
                                                ip_address=ip_address,
                                                security_url=security_url)
            
            return EmailService._send_email(email, subject, html_content)
            
        except Exception as e:
            current_app.logger.error(f"发送安全提醒邮件失败: {str(e)}")
            return False