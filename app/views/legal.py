# -*- coding: utf-8 -*-
"""
法律页面视图
处理服务条款、隐私政策等法律文档的展示
"""

from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__, url_prefix='/legal')


@legal_bp.route('/terms')
def terms():
    """服务条款页面"""
    return render_template('legal/terms.html')


@legal_bp.route('/privacy')
def privacy():
    """隐私政策页面"""
    return render_template('legal/privacy.html')