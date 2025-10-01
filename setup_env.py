#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kronos股票预测系统 - 环境配置助手
自动生成安全密钥并创建.env文件
"""

import secrets
import os
import sys
from pathlib import Path


def generate_secret_key() -> str:
    """生成Flask会话密钥"""
    return secrets.token_hex(16)


def generate_jwt_secret() -> str:
    """生成JWT密钥"""
    return secrets.token_urlsafe(32)


def create_env_file():
    """创建.env文件"""
    
    print("🔧 Kronos股票预测系统 - 环境配置助手")
    print("=" * 50)
    
    # 检查是否已存在.env文件
    env_file = Path('.env')
    if env_file.exists():
        response = input("⚠️  .env文件已存在，是否覆盖？ (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ 配置取消")
            return False
    
    # 生成密钥
    print("\n🔐 生成安全密钥...")
    flask_secret = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    print("✅ 密钥生成完成")
    
    # 获取用户配置
    print("\n📋 配置信息收集...")
    
    # 环境选择
    print("\n选择运行环境:")
    print("1. 开发环境 (development)")
    print("2. 生产环境 (production)")
    env_choice = input("请选择 [1]: ").strip() or "1"
    
    flask_env = "development" if env_choice == "1" else "production"
    flask_debug = "True" if env_choice == "1" else "False"
    
    # 数据库配置
    print(f"\n数据库配置 ({'SQLite(推荐)' if env_choice == '1' else 'MySQL(推荐)'}):")
    
    if env_choice == "1":
        # 开发环境 - SQLite
        db_url = ""
        print("  使用SQLite数据库（默认）")
    else:
        # 生产环境 - MySQL
        print("  配置MySQL数据库:")
        db_host = input("  MySQL主机 [localhost]: ").strip() or "localhost"
        db_port = input("  MySQL端口 [3306]: ").strip() or "3306"
        db_name = input("  数据库名 [kronos_stock]: ").strip() or "kronos_stock"
        db_user = input("  用户名 [kronos]: ").strip() or "kronos"
        db_password = input("  密码: ").strip()
        
        if db_password:
            db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            db_url = ""
            print("  ⚠️  未设置密码，将使用SQLite")
    
    # 邮件服务配置
    print("\n📧 邮件服务配置（用于密码重置）:")
    configure_mail = input("是否配置邮件服务？ (y/N): ").lower() in ['y', 'yes']
    
    mail_config = {}
    if configure_mail:
        mail_config['server'] = input("  SMTP服务器 [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
        mail_config['port'] = input("  SMTP端口 [587]: ").strip() or "587"
        mail_config['username'] = input("  邮箱地址: ").strip()
        mail_config['password'] = input("  邮箱密码/应用专用密码: ").strip()
        mail_config['sender'] = mail_config['username']
    
    # 生成.env文件内容
    env_content = f"""# Kronos股票预测系统 - 自动生成的环境配置
# 生成时间: {secrets.token_urlsafe(8)}

# ============ Flask基础配置 ============
FLASK_CONFIG={flask_env}
FLASK_ENV={flask_env}
FLASK_DEBUG={flask_debug}

# Flask会话密钥（自动生成）
SECRET_KEY={flask_secret}

# ============ 用户认证安全配置 ============
# JWT密钥（自动生成）
JWT_SECRET_KEY={jwt_secret}

# 会话超时时间（秒，默认24小时）
PERMANENT_SESSION_LIFETIME=86400

# 密码策略配置
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL=True

# 登录安全限制
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=1800

# ============ 数据库配置 ============
"""
    
    if db_url:
        env_content += f"DATABASE_URL={db_url}\n"
    else:
        env_content += "# 使用默认SQLite数据库\nDATABASE_URL=\n"
    
    env_content += """
# 数据库连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============ 邮件服务配置 ============
"""
    
    if mail_config:
        env_content += f"""MAIL_SERVER={mail_config['server']}
MAIL_PORT={mail_config['port']}
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME={mail_config['username']}
MAIL_PASSWORD={mail_config['password']}
MAIL_DEFAULT_SENDER={mail_config['sender']}
"""
    else:
        env_content += """# 邮件服务未配置，请手动设置
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
# MAIL_DEFAULT_SENDER=your-email@gmail.com
"""
    
    env_content += """
# ============ 跨域资源共享配置 ============
CORS_ORIGINS=http://localhost:5000,http://localhost:5001,http://127.0.0.1:5000,http://127.0.0.1:5001

# ============ 股票预测API配置 ============
MAX_PREDICTION_DAYS=30
DEFAULT_TEMPERATURE=0.7
DEFAULT_MODEL=kronos-mini
MAX_CONCURRENT_PREDICTIONS=3

# 股票数据配置
STOCK_DATA_PROVIDER=china_stock_data
DATA_UPDATE_INTERVAL=15

# ============ 文件上传配置 ============
UPLOAD_FOLDER=app/static/uploads
MAX_UPLOAD_SIZE=5242880
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif

# ============ 日志配置 ============
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# ============ 性能和缓存配置 ============
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# ============ 开发环境配置 ============
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5001
FLASK_RUN_DEBUG=True
"""
    
    # 写入.env文件
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ .env文件创建成功！")
        print(f"📁 文件位置: {env_file.absolute()}")
        
        # 创建必要的目录
        os.makedirs('logs', exist_ok=True)
        os.makedirs('app/static/uploads', exist_ok=True)
        print("📁 已创建必要的目录: logs/, app/static/uploads/")
        
        print("\n🚀 配置完成！可以运行以下命令启动应用:")
        print("   python run.py")
        
        if not mail_config:
            print("\n⚠️  提醒: 邮件服务未配置，密码重置功能将不可用")
            print("   如需配置，请编辑 .env 文件中的邮件设置")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False


def main():
    """主函数"""
    try:
        # 检查是否在项目根目录
        if not Path('config.py').exists():
            print("❌ 错误: 请在项目根目录运行此脚本")
            print("   应包含 config.py 文件")
            sys.exit(1)
        
        # 创建.env文件
        success = create_env_file()
        
        if success:
            print("\n🎉 环境配置完成！")
        else:
            print("\n❌ 环境配置失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ 配置取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()