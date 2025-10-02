# -*- coding: utf-8 -*-
"""
过期会话自动清理任务
定时清理过期的用户会话记录，保持数据库清洁
"""

import logging
from datetime import datetime, timezone, timedelta
from flask import current_app
from sqlalchemy import func

from app.models.user import UserSession, PasswordResetToken, EmailVerification, db


class SessionCleanupService:
    """会话清理服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def cleanup_expired_sessions(self, batch_size=1000):
        """
        清理过期的用户会话
        
        Args:
            batch_size: 批量处理大小，避免一次处理太多数据
            
        Returns:
            dict: 清理结果统计
        """
        try:
            current_time = datetime.now(timezone.utc)
            cleanup_stats = {
                'sessions_cleaned': 0,
                'tokens_cleaned': 0,
                'verifications_cleaned': 0,
                'total_cleaned': 0,
                'errors': []
            }
            
            # 1. 清理过期的用户会话
            sessions_cleaned = self._cleanup_expired_user_sessions(current_time, batch_size)
            cleanup_stats['sessions_cleaned'] = sessions_cleaned
            
            # 2. 清理过期的密码重置令牌
            tokens_cleaned = self._cleanup_expired_reset_tokens(current_time, batch_size)
            cleanup_stats['tokens_cleaned'] = tokens_cleaned
            
            # 3. 清理过期的邮箱验证令牌
            verifications_cleaned = self._cleanup_expired_verification_tokens(current_time, batch_size)
            cleanup_stats['verifications_cleaned'] = verifications_cleaned
            
            # 4. 清理过期的非活跃会话（超过30天未使用）
            inactive_sessions_cleaned = self._cleanup_inactive_sessions(current_time, batch_size)
            cleanup_stats['inactive_sessions_cleaned'] = inactive_sessions_cleaned
            
            cleanup_stats['total_cleaned'] = (
                sessions_cleaned + tokens_cleaned + 
                verifications_cleaned + inactive_sessions_cleaned
            )
            
            self.logger.info(f"会话清理完成: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            error_msg = f"会话清理失败: {str(e)}"
            self.logger.error(error_msg)
            cleanup_stats['errors'].append(error_msg)
            return cleanup_stats
    
    def _cleanup_expired_user_sessions(self, current_time, batch_size):
        """清理过期的用户会话"""
        try:
            # 分批删除过期会话，避免长时间锁定
            total_cleaned = 0
            
            while True:
                # 查找过期的会话
                expired_sessions = (
                    UserSession.query
                    .filter(UserSession.expires_at < current_time)
                    .limit(batch_size)
                    .all()
                )
                
                if not expired_sessions:
                    break
                
                # 批量删除
                for session in expired_sessions:
                    try:
                        db.session.delete(session)
                        total_cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"删除会话失败 {session.id}: {str(e)}")
                        continue
                
                # 提交当前批次
                db.session.commit()
                
                # 如果删除的数量少于批量大小，说明已经清理完毕
                if len(expired_sessions) < batch_size:
                    break
            
            self.logger.info(f"清理过期会话: {total_cleaned} 个")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"清理过期会话异常: {str(e)}")
            db.session.rollback()
            return 0
    
    def _cleanup_expired_reset_tokens(self, current_time, batch_size):
        """清理过期的密码重置令牌"""
        try:
            total_cleaned = 0
            
            while True:
                # 查找过期的令牌
                expired_tokens = (
                    PasswordResetToken.query
                    .filter(PasswordResetToken.expires_at < current_time)
                    .limit(batch_size)
                    .all()
                )
                
                if not expired_tokens:
                    break
                
                # 批量删除
                for token in expired_tokens:
                    try:
                        db.session.delete(token)
                        total_cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"删除重置令牌失败 {token.id}: {str(e)}")
                        continue
                
                # 提交当前批次
                db.session.commit()
                
                if len(expired_tokens) < batch_size:
                    break
            
            self.logger.info(f"清理过期重置令牌: {total_cleaned} 个")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"清理过期重置令牌异常: {str(e)}")
            db.session.rollback()
            return 0
    
    def _cleanup_expired_verification_tokens(self, current_time, batch_size):
        """清理过期的邮箱验证令牌"""
        try:
            total_cleaned = 0
            
            while True:
                # 查找过期的验证令牌
                expired_verifications = (
                    EmailVerification.query
                    .filter(EmailVerification.expires_at < current_time)
                    .limit(batch_size)
                    .all()
                )
                
                if not expired_verifications:
                    break
                
                # 批量删除
                for verification in expired_verifications:
                    try:
                        db.session.delete(verification)
                        total_cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"删除验证令牌失败 {verification.id}: {str(e)}")
                        continue
                
                # 提交当前批次
                db.session.commit()
                
                if len(expired_verifications) < batch_size:
                    break
            
            self.logger.info(f"清理过期验证令牌: {total_cleaned} 个")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"清理过期验证令牌异常: {str(e)}")
            db.session.rollback()
            return 0
    
    def _cleanup_inactive_sessions(self, current_time, batch_size, inactive_days=30):
        """清理长时间未活动的会话"""
        try:
            # 计算非活跃时间阈值
            inactive_threshold = current_time - timedelta(days=inactive_days)
            total_cleaned = 0
            
            while True:
                # 查找长时间未活动的会话
                inactive_sessions = (
                    UserSession.query
                    .filter(
                        UserSession.last_activity < inactive_threshold,
                        UserSession.is_active == True
                    )
                    .limit(batch_size)
                    .all()
                )
                
                if not inactive_sessions:
                    break
                
                # 批量设置为非活跃状态（而不是直接删除）
                for session in inactive_sessions:
                    try:
                        session.is_active = False
                        total_cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"停用会话失败 {session.id}: {str(e)}")
                        continue
                
                # 提交当前批次
                db.session.commit()
                
                if len(inactive_sessions) < batch_size:
                    break
            
            self.logger.info(f"停用非活跃会话: {total_cleaned} 个")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"清理非活跃会话异常: {str(e)}")
            db.session.rollback()
            return 0
    
    def get_cleanup_statistics(self):
        """获取清理统计信息"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # 计算各种会话状态的统计
            stats = {
                'active_sessions': UserSession.query.filter(
                    UserSession.is_active == True,
                    UserSession.expires_at > current_time
                ).count(),
                
                'expired_sessions': UserSession.query.filter(
                    UserSession.expires_at <= current_time
                ).count(),
                
                'inactive_sessions': UserSession.query.filter(
                    UserSession.is_active == False
                ).count(),
                
                'pending_reset_tokens': PasswordResetToken.query.filter(
                    PasswordResetToken.expires_at > current_time,
                    PasswordResetToken.is_used == False
                ).count(),
                
                'expired_reset_tokens': PasswordResetToken.query.filter(
                    PasswordResetToken.expires_at <= current_time
                ).count(),
                
                'pending_verifications': EmailVerification.query.filter(
                    EmailVerification.expires_at > current_time,
                    EmailVerification.is_verified == False
                ).count(),
                
                'expired_verifications': EmailVerification.query.filter(
                    EmailVerification.expires_at <= current_time
                ).count()
            }
            
            # 计算总的需要清理的记录数
            stats['total_cleanup_needed'] = (
                stats['expired_sessions'] +
                stats['expired_reset_tokens'] +
                stats['expired_verifications']
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取清理统计异常: {str(e)}")
            return {}
    
    def force_cleanup_user_sessions(self, user_id):
        """强制清理指定用户的所有会话（用于安全用途）"""
        try:
            sessions = UserSession.query.filter(UserSession.user_id == user_id).all()
            cleaned_count = 0
            
            for session in sessions:
                session.is_active = False
                cleaned_count += 1
            
            db.session.commit()
            
            self.logger.info(f"强制清理用户 {user_id} 的 {cleaned_count} 个会话")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"强制清理用户会话异常: {str(e)}")
            db.session.rollback()
            return 0


# 创建全局清理服务实例
session_cleanup_service = SessionCleanupService()


def create_cleanup_cli_commands(app):
    """为Flask应用添加清理相关的CLI命令"""
    
    @app.cli.command('cleanup-sessions')
    def cleanup_sessions_command():
        """清理过期会话的CLI命令"""
        print("开始清理过期会话...")
        
        with app.app_context():
            stats = session_cleanup_service.cleanup_expired_sessions()
            
            print(f"清理完成:")
            print(f"  - 过期会话: {stats['sessions_cleaned']}")
            print(f"  - 过期重置令牌: {stats['tokens_cleaned']}")
            print(f"  - 过期验证令牌: {stats['verifications_cleaned']}")
            print(f"  - 非活跃会话: {stats.get('inactive_sessions_cleaned', 0)}")
            print(f"  - 总计: {stats['total_cleaned']}")
            
            if stats['errors']:
                print(f"清理过程中的错误:")
                for error in stats['errors']:
                    print(f"  - {error}")
    
    @app.cli.command('session-stats')
    def session_stats_command():
        """显示会话统计信息的CLI命令"""
        print("获取会话统计信息...")
        
        with app.app_context():
            stats = session_cleanup_service.get_cleanup_statistics()
            
            print(f"会话统计:")
            print(f"  - 活跃会话: {stats.get('active_sessions', 0)}")
            print(f"  - 过期会话: {stats.get('expired_sessions', 0)}")
            print(f"  - 非活跃会话: {stats.get('inactive_sessions', 0)}")
            print(f"  - 待处理重置令牌: {stats.get('pending_reset_tokens', 0)}")
            print(f"  - 过期重置令牌: {stats.get('expired_reset_tokens', 0)}")
            print(f"  - 待处理验证令牌: {stats.get('pending_verifications', 0)}")
            print(f"  - 过期验证令牌: {stats.get('expired_verifications', 0)}")
            print(f"  - 需清理总数: {stats.get('total_cleanup_needed', 0)}")
    
    @app.cli.command('force-cleanup-user')
    @app.cli.option('--user-id', type=int, required=True, help='用户ID')
    def force_cleanup_user_command(user_id):
        """强制清理指定用户会话的CLI命令"""
        print(f"强制清理用户 {user_id} 的所有会话...")
        
        with app.app_context():
            cleaned_count = session_cleanup_service.force_cleanup_user_sessions(user_id)
            print(f"已清理 {cleaned_count} 个会话")


def schedule_cleanup_task():
    """设置定时清理任务（需要外部调度器如Celery、APScheduler等）"""
    # 这里是示例代码，实际使用时需要配置定时任务
    # 建议每天凌晨执行一次清理
    
    # 使用APScheduler的示例：
    # from apscheduler.schedulers.background import BackgroundScheduler
    # 
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(
    #     func=session_cleanup_service.cleanup_expired_sessions,
    #     trigger="cron",
    #     hour=2,  # 凌晨2点执行
    #     minute=0,
    #     id='session_cleanup'
    # )
    # scheduler.start()
    
    pass


def init_session_cleanup(app):
    """初始化会话清理模块"""
    # 添加CLI命令
    create_cleanup_cli_commands(app)
    
    # 记录初始化日志
    app.logger.info("会话清理模块已初始化")
    app.logger.info("使用 'flask cleanup-sessions' 命令手动清理过期会话")
    app.logger.info("使用 'flask session-stats' 命令查看会话统计")
    
    return session_cleanup_service