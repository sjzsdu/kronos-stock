# -*- coding: utf-8 -*-
"""
用户认证API
提供登录、注册、密码重置等认证接口
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app.services.auth_service import AuthService
from app.decorators.auth_decorators import token_required
from app.utils.validators import sanitize_input, validate_email


auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        # 调试信息
        current_app.logger.info(f"收到注册请求 - Method: {request.method}, Path: {request.path}")
        current_app.logger.info(f"Content-Type: {request.content_type}")
        current_app.logger.info(f"Form data: {dict(request.form)}")
        current_app.logger.info(f"JSON data: {request.get_json(silent=True)}")
        # 获取数据：支持JSON和表单数据
        if request.is_json:
            try:
                data = request.get_json(force=False)
            except Exception as json_error:
                return jsonify({
                    'success': False,
                    'message': 'JSON格式错误',
                    'errors': {'json': ['无效的JSON数据']}
                }), 400
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供注册信息',
                    'errors': {'data': ['请求体不能为空']}
                }), 400
        else:
            # 处理表单数据 (HTMX请求)
            data = request.form.to_dict()
            # 转换checkbox值
            if 'agree_terms' in data:
                data['agree_terms'] = data['agree_terms'] == 'on'
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供注册信息',
                    'errors': {'data': ['表单数据不能为空']}
                }), 400
        
        # 获取并验证输入
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        full_name = sanitize_input(data.get('full_name', ''))
        nickname = sanitize_input(data.get('nickname', ''))
        
        # 如果没有提供full_name，使用nickname作为full_name
        if not full_name and nickname:
            full_name = nickname
        
        # 验证必填字段和格式
        errors = {}
        
        # 邮箱验证
        if not email:
            errors['email'] = ['邮箱不能为空']
        elif not validate_email(email):
            errors['email'] = ['邮箱格式无效']
        
        # 密码验证
        if not password:
            errors['password'] = ['密码不能为空']
        elif len(password) < 8:
            errors['password'] = ['密码长度至少8位']
        elif not any(c.isdigit() for c in password):
            errors['password'] = ['密码必须包含至少一个数字']
        elif not any(c.isalpha() for c in password):
            errors['password'] = ['密码必须包含至少一个字母']
        
        # 确认密码验证
        if confirm_password and confirm_password != password:
            errors['confirm_password'] = ['两次输入的密码不一致']
        
        # 昵称验证（必填）
        if not nickname:
            errors['nickname'] = ['昵称不能为空']
        elif len(nickname) > 50:
            errors['nickname'] = ['昵称长度不能超过50个字符']
        elif nickname.strip() == '':
            errors['nickname'] = ['昵称不能为空']
        else:
            # 检查是否包含特殊字符（只允许中文、英文、数字）
            import re
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', nickname.strip()):
                errors['nickname'] = ['昵称只能包含中文、英文和数字']
        
        # 如果既没有full_name也没有nickname，报错
        if not full_name and not nickname:
            errors['nickname'] = ['昵称不能为空']
        
        if errors:
            return jsonify({
                'success': False,
                'message': '输入信息有误',
                'errors': errors
            }), 400
        
        # 检查邮箱是否已存在
        from app.models.user import User
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': '该邮箱已被注册',
                'errors': {'email': ['邮箱已存在']}
            }), 409
        
        # 执行注册
        try:
            success, message, user = AuthService.register_user(email, password, full_name, nickname)
            
            if success:
                # 检查是否是HTMX请求
                if request.headers.get('HX-Request'):
                    # 返回成功的HTML片段
                    success_html = f"""
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <i class="fas fa-check-circle text-green-400"></i>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm font-medium text-green-800">
                                    注册成功！{message} 正在跳转到登录页面...
                                </p>
                            </div>
                        </div>
                    </div>
                    <script>
                        setTimeout(() => {{
                            window.location.href = '/auth/login';
                        }}, 2000);
                    </script>
                    """
                    return success_html, 200
                else:
                    # API调用返回JSON
                    return jsonify({
                        'success': True,
                        'message': message,
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'full_name': user.full_name,
                            'nickname': nickname,
                            'created_at': user.created_at.isoformat()
                        }
                    }), 201
            else:
                # 注册失败
                if request.headers.get('HX-Request'):
                    # 返回错误的HTML片段
                    error_html = f"""
                    <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <i class="fas fa-exclamation-circle text-red-400"></i>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm font-medium text-red-800">
                                    {message}
                                </p>
                            </div>
                        </div>
                    </div>
                    """
                    return error_html, 200
                else:
                    return jsonify({
                        'success': False,
                        'message': message,
                        'errors': {'registration': [message]}
                    }), 400
        except Exception as register_error:
            current_app.logger.error(f"注册服务调用失败: {str(register_error)}")
            if request.headers.get('HX-Request'):
                error_html = f"""
                <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-circle text-red-400"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-red-800">
                                注册过程出现错误，请稍后重试
                            </p>
                        </div>
                    </div>
                </div>
                """
                return error_html, 200
            else:
                return jsonify({
                    'success': False,
                    'message': '注册过程出现错误',
                    'errors': {'registration': [str(register_error)]}
                }), 500
            
    except Exception as e:
        current_app.logger.error(f"注册API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '注册失败，请稍后重试',
            'errors': {'server': ['服务器内部错误']}
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 获取数据：支持JSON和表单数据
        if request.is_json:
            try:
                data = request.get_json(force=False)
            except Exception as json_error:
                return jsonify({
                    'success': False,
                    'message': 'JSON格式错误',
                    'errors': {'json': ['无效的JSON数据']}
                }), 400
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供登录信息',
                    'errors': {'data': ['请求体不能为空']}
                }), 400
        else:
            # 处理表单数据 (HTMX请求)
            data = request.form.to_dict()
            # 转换checkbox值
            if 'remember_me' in data:
                data['remember'] = data.pop('remember_me') == 'on'
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供登录信息',
                    'errors': {'data': ['表单数据不能为空']}
                }), 400
        
        # 获取并验证输入
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # 验证必填字段和格式
        errors = {}
        
        if not email:
            errors['email'] = ['邮箱不能为空']
        elif not validate_email(email):
            errors['email'] = ['邮箱格式无效']
            
        if not password:
            errors['password'] = ['密码不能为空']
        
        if errors:
            return jsonify({
                'success': False,
                'message': '输入信息有误',
                'errors': errors
            }), 400
        
        # 执行登录
        result = AuthService.authenticate_user(email, password, remember)
        
        if len(result) == 5:
            success, message, user, token, expires_at = result
        elif len(result) == 4:
            success, message, user, token = result
            expires_at = None
        else:
            success, message, user = result
            token = None
            expires_at = None
        
        if success:
            # 获取用户档案信息
            from app.models.user import UserProfile
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            
            if request.headers.get('HX-Request'):
                # HTMX请求，重定向到仪表盘
                from flask import make_response
                response = make_response('', 200)
                response.headers['HX-Redirect'] = '/dashboard'
                return response
            else:
                # API调用，返回用户信息
                response_data = {
                    'success': True,
                    'message': message,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'nickname': profile.nickname if profile else None,
                        'role': user.role,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                }
                
                if token:
                    response_data['token'] = token
                
                if expires_at:
                    response_data['expires_at'] = expires_at.isoformat()
                    
                return jsonify(response_data), 200
        else:
            if request.headers.get('HX-Request'):
                # HTMX请求，返回错误消息
                error_html = f"""
                <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-circle text-red-400"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-red-800">
                                {message}
                            </p>
                        </div>
                    </div>
                </div>
                """
                return error_html, 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 401
            
    except Exception as e:
        current_app.logger.error(f"登录API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user_id):
    """用户登出"""
    try:
        # 通过ID获取用户对象
        from app.models.user import User
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
            
        # 检查是否请求登出所有会话
        data = request.get_json(silent=True) or {}
        logout_all = data.get('logout_all', False)
        
        # 对于API调用，我们需要使session失效
        if hasattr(request, 'current_session'):
            from app.models import db
            
            if logout_all:
                # 登出所有会话
                from app.models.user import UserSession
                UserSession.query.filter_by(
                    user_id=current_user.id,
                    is_active=True
                ).update({'is_active': False})
            else:
                # 只登出当前会话
                current_session = request.current_session
                current_session.is_active = False
                
            db.session.commit()
            success = True
        else:
            success = AuthService.logout_user_session(current_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': '已成功登出'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '登出失败'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"登出API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登出失败，请稍后重试'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user_id):
    """修改密码"""
    try:
        # 通过ID获取用户对象
        from app.models.user import User
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供密码信息'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not all([current_password, new_password]):
            return jsonify({
                'success': False,
                'message': '当前密码和新密码都是必填项'
            }), 400
        
        # 执行密码修改
        success, message = AuthService.change_password(
            current_user, current_password, new_password
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"修改密码API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '修改密码失败，请稍后重试'
        }), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 发送重置链接"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供邮箱地址'
            }), 400
        
        email = sanitize_input(data.get('email', ''))
        
        if not email:
            return jsonify({
                'success': False,
                'message': '邮箱地址是必填项'
            }), 400
        
        # 生成重置令牌
        success, message, token = AuthService.generate_reset_token(email)
        
        if success:
            # 这里应该发送邮件，暂时返回令牌用于测试
            # TODO: 集成邮件服务
            return jsonify({
                'success': True,
                'message': '重置链接已发送到您的邮箱',
                'reset_token': token  # 生产环境中不应返回令牌
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"忘记密码API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '处理失败，请稍后重试'
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供重置信息'
            }), 400
        
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        
        if not all([token, new_password]):
            return jsonify({
                'success': False,
                'message': '重置令牌和新密码都是必填项'
            }), 400
        
        # 执行密码重置
        success, message = AuthService.reset_password_with_token(token, new_password)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"重置密码API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '重置密码失败，请稍后重试'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'full_name': current_user.full_name,
                'role': current_user.role,
                'is_active': current_user.is_active,
                'created_at': current_user.created_at.isoformat(),
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户信息API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取用户信息失败'
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@login_required
def verify_auth():
    """验证用户认证状态"""
    return jsonify({
        'success': True,
        'authenticated': True,
        'user_id': current_user.id
    }), 200