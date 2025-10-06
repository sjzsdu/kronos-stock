"""性能监控记录数据库迁移

添加性能监控表，记录系统性能指标和用户行为数据。

Revision ID: performance_metrics
Revises: component_render_cache
Create Date: 2025-10-05 12:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'performance_metrics'
down_revision = 'component_render_cache'
branch_labels = None
depends_on = None


def upgrade():
    """创建性能监控记录表"""
    # 创建性能监控记录表
    op.create_table(
        'performance_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, comment='监控ID'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='用户ID'),
        sa.Column('session_id', sa.String(100), nullable=False, comment='会话ID'),
        sa.Column('metric_type', sa.String(50), nullable=False, comment='监控指标类型'),
        sa.Column('metric_name', sa.String(100), nullable=False, comment='指标名称'),
        sa.Column('metric_value', sa.Float(), nullable=False, comment='指标数值'),
        sa.Column('metric_unit', sa.String(20), default='ms', comment='指标单位'),
        sa.Column('page_url', sa.String(500), nullable=True, comment='页面URL'),
        sa.Column('user_agent', sa.String(500), nullable=True, comment='用户代理'),
        sa.Column('additional_data', sa.JSON(), nullable=True, comment='附加数据JSON'),
        sa.Column('recorded_at', sa.DateTime(), default=sa.func.now(), comment='记录时间'),
    )
    
    # 创建索引
    op.create_index('idx_perf_user', 'performance_metrics', ['user_id'])
    op.create_index('idx_perf_session', 'performance_metrics', ['session_id'])
    op.create_index('idx_perf_type', 'performance_metrics', ['metric_type'])
    op.create_index('idx_perf_name', 'performance_metrics', ['metric_name'])
    op.create_index('idx_perf_recorded', 'performance_metrics', ['recorded_at'])
    op.create_index('idx_perf_type_name', 'performance_metrics', ['metric_type', 'metric_name'])
    
    # 添加约束
    op.create_check_constraint(
        'chk_metric_type',
        'performance_metrics',
        text("metric_type IN ('page_load', 'api_response', 'component_render', 'user_interaction', 'resource_load')")
    )
    
    op.create_check_constraint(
        'chk_metric_value_positive',
        'performance_metrics',
        text("metric_value >= 0")
    )


def downgrade():
    """删除性能监控记录表"""
    op.drop_index('idx_perf_type_name', 'performance_metrics')
    op.drop_index('idx_perf_recorded', 'performance_metrics')
    op.drop_index('idx_perf_name', 'performance_metrics')
    op.drop_index('idx_perf_type', 'performance_metrics')
    op.drop_index('idx_perf_session', 'performance_metrics')
    op.drop_index('idx_perf_user', 'performance_metrics')
    op.drop_table('performance_metrics')