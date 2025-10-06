"""用户界面偏好数据库迁移

添加用户界面偏好设置表，支持个性化UI定制功能。

Revision ID: user_ui_preferences
Revises: performance_metrics
Create Date: 2025-10-05 12:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'user_ui_preferences'
down_revision = 'performance_metrics'
branch_labels = None
depends_on = None


def upgrade():
    """创建用户界面偏好表"""
    # 创建用户界面偏好表
    op.create_table(
        'user_ui_preferences',
        sa.Column('id', sa.Integer(), primary_key=True, comment='偏好ID'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, comment='用户ID'),
        sa.Column('preference_category', sa.String(50), nullable=False, comment='偏好类别'),
        sa.Column('preference_key', sa.String(100), nullable=False, comment='偏好键名'),
        sa.Column('preference_value', sa.Text(), nullable=False, comment='偏好值'),
        sa.Column('value_type', sa.String(20), default='string', comment='值类型'),
        sa.Column('is_default', sa.Boolean(), default=False, comment='是否为默认值'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # 创建索引
    op.create_index('idx_ui_pref_user', 'user_ui_preferences', ['user_id'])
    op.create_index('idx_ui_pref_category', 'user_ui_preferences', ['preference_category'])
    op.create_index('idx_ui_pref_key', 'user_ui_preferences', ['preference_key'])
    op.create_index('idx_ui_pref_user_category', 'user_ui_preferences', ['user_id', 'preference_category'])
    op.create_index('idx_ui_pref_user_key', 'user_ui_preferences', ['user_id', 'preference_key'])
    
    # 创建唯一约束 - 每个用户的每个偏好键只能有一个值
    op.create_unique_constraint(
        'uq_user_preference_key',
        'user_ui_preferences',
        ['user_id', 'preference_key']
    )
    
    # 添加检查约束
    op.create_check_constraint(
        'chk_preference_category',
        'user_ui_preferences',
        text("preference_category IN ('theme', 'layout', 'notification', 'component', 'accessibility')")
    )
    
    op.create_check_constraint(
        'chk_value_type',
        'user_ui_preferences',
        text("value_type IN ('string', 'boolean', 'integer', 'float', 'json')")
    )


def downgrade():
    """删除用户界面偏好表"""
    op.drop_constraint('uq_user_preference_key', 'user_ui_preferences', type_='unique')
    op.drop_index('idx_ui_pref_user_key', 'user_ui_preferences')
    op.drop_index('idx_ui_pref_user_category', 'user_ui_preferences')
    op.drop_index('idx_ui_pref_key', 'user_ui_preferences')
    op.drop_index('idx_ui_pref_category', 'user_ui_preferences')
    op.drop_index('idx_ui_pref_user', 'user_ui_preferences')
    op.drop_table('user_ui_preferences')