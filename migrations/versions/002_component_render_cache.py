"""组件渲染缓存数据库迁移

添加组件渲染缓存表，提升组件渲染性能和用户体验。

Revision ID: component_render_cache  
Revises: ui_component_config
Create Date: 2025-10-05 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'component_render_cache'
down_revision = 'ui_component_config'
branch_labels = None
depends_on = None


def upgrade():
    """创建组件渲染缓存表"""
    # 创建组件渲染缓存表
    op.create_table(
        'component_render_cache',
        sa.Column('id', sa.Integer(), primary_key=True, comment='缓存ID'),
        sa.Column('cache_key', sa.String(255), nullable=False, unique=True, comment='缓存键'),
        sa.Column('component_type', sa.String(50), nullable=False, comment='组件类型'),
        sa.Column('template_path', sa.String(255), nullable=False, comment='模板路径'),
        sa.Column('rendered_html', sa.Text(), nullable=False, comment='渲染后的HTML'),
        sa.Column('render_data', sa.JSON(), nullable=True, comment='渲染数据JSON'),
        sa.Column('expires_at', sa.DateTime(), nullable=False, comment='过期时间'),
        sa.Column('hit_count', sa.Integer(), default=0, comment='缓存命中次数'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # 创建索引
    op.create_index('idx_cache_key', 'component_render_cache', ['cache_key'])
    op.create_index('idx_cache_component_type', 'component_render_cache', ['component_type'])
    op.create_index('idx_cache_expires', 'component_render_cache', ['expires_at'])
    op.create_index('idx_cache_template', 'component_render_cache', ['template_path'])


def downgrade():
    """删除组件渲染缓存表"""
    op.drop_index('idx_cache_template', 'component_render_cache')
    op.drop_index('idx_cache_expires', 'component_render_cache')
    op.drop_index('idx_cache_component_type', 'component_render_cache')
    op.drop_index('idx_cache_key', 'component_render_cache')
    op.drop_table('component_render_cache')