"""组件使用统计数据库迁移

添加组件使用统计表，记录组件使用情况和用户行为分析。

Revision ID: component_usage_stats
Revises: user_ui_preferences  
Create Date: 2025-10-05 12:04:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'component_usage_stats'
down_revision = 'user_ui_preferences'
branch_labels = None
depends_on = None


def upgrade():
    """创建组件使用统计表"""
    # 创建组件使用统计表
    op.create_table(
        'component_usage_stats',
        sa.Column('id', sa.Integer(), primary_key=True, comment='统计ID'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='用户ID'),
        sa.Column('session_id', sa.String(100), nullable=False, comment='会话ID'),
        sa.Column('component_name', sa.String(100), nullable=False, comment='组件名称'),
        sa.Column('component_type', sa.String(50), nullable=False, comment='组件类型'),
        sa.Column('action_type', sa.String(50), nullable=False, comment='操作类型'),
        sa.Column('page_url', sa.String(500), nullable=True, comment='页面URL'),
        sa.Column('interaction_data', sa.JSON(), nullable=True, comment='交互数据JSON'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='交互持续时间(毫秒)'),
        sa.Column('success', sa.Boolean(), default=True, comment='操作是否成功'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('recorded_at', sa.DateTime(), default=sa.func.now(), comment='记录时间'),
    )
    
    # 创建索引
    op.create_index('idx_usage_user', 'component_usage_stats', ['user_id'])
    op.create_index('idx_usage_session', 'component_usage_stats', ['session_id'])
    op.create_index('idx_usage_component', 'component_usage_stats', ['component_name'])
    op.create_index('idx_usage_type', 'component_usage_stats', ['component_type'])
    op.create_index('idx_usage_action', 'component_usage_stats', ['action_type'])
    op.create_index('idx_usage_recorded', 'component_usage_stats', ['recorded_at'])
    op.create_index('idx_usage_success', 'component_usage_stats', ['success'])
    op.create_index('idx_usage_component_action', 'component_usage_stats', ['component_name', 'action_type'])
    
    # 添加约束
    op.create_check_constraint(
        'chk_usage_component_type',
        'component_usage_stats',
        text("component_type IN ('form', 'button', 'card', 'navigation', 'modal', 'notification', 'chart', 'table')")
    )
    
    op.create_check_constraint(
        'chk_usage_action_type',
        'component_usage_stats',
        text("action_type IN ('view', 'click', 'submit', 'hover', 'focus', 'scroll', 'expand', 'collapse', 'close')")
    )
    
    op.create_check_constraint(
        'chk_duration_positive',
        'component_usage_stats',
        text("duration_ms IS NULL OR duration_ms >= 0")
    )


def downgrade():
    """删除组件使用统计表"""
    op.drop_index('idx_usage_component_action', 'component_usage_stats')
    op.drop_index('idx_usage_success', 'component_usage_stats')
    op.drop_index('idx_usage_recorded', 'component_usage_stats')
    op.drop_index('idx_usage_action', 'component_usage_stats')
    op.drop_index('idx_usage_type', 'component_usage_stats')
    op.drop_index('idx_usage_component', 'component_usage_stats')
    op.drop_index('idx_usage_session', 'component_usage_stats')
    op.drop_index('idx_usage_user', 'component_usage_stats')
    op.drop_table('component_usage_stats')