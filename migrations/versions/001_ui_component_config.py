"""UI组件配置数据库迁移

添加UI组件配置相关的数据表，支持组件个性化和主题定制功能。

Revision ID: ui_component_config
Revises: 
Create Date: 2025-10-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'ui_component_config'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """创建UI组件配置表"""
    # 创建UI组件配置表
    op.create_table(
        'ui_component_configs',
        sa.Column('id', sa.Integer(), primary_key=True, comment='配置ID'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='用户ID，空表示全局配置'),
        sa.Column('component_name', sa.String(100), nullable=False, comment='组件名称'),
        sa.Column('component_type', sa.String(50), nullable=False, comment='组件类型'),
        sa.Column('config_data', sa.JSON(), nullable=False, comment='配置数据JSON'),
        sa.Column('is_active', sa.Boolean(), default=True, comment='是否启用'),
        sa.Column('version', sa.Integer(), default=1, comment='配置版本'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # 创建索引
    op.create_index('idx_ui_config_user_component', 'ui_component_configs', ['user_id', 'component_name'])
    op.create_index('idx_ui_config_type', 'ui_component_configs', ['component_type'])
    op.create_index('idx_ui_config_active', 'ui_component_configs', ['is_active'])
    
    # 添加约束
    op.create_check_constraint(
        'chk_component_type',
        'ui_component_configs',
        text("component_type IN ('form', 'button', 'card', 'navigation', 'modal', 'notification')")
    )
    
    op.create_check_constraint(
        'chk_component_name_format',
        'ui_component_configs', 
        text("component_name ~ '^[a-zA-Z0-9_-]+$'")
    )


def downgrade():
    """删除UI组件配置表"""
    op.drop_index('idx_ui_config_active', 'ui_component_configs')
    op.drop_index('idx_ui_config_type', 'ui_component_configs')
    op.drop_index('idx_ui_config_user_component', 'ui_component_configs')
    op.drop_table('ui_component_configs')