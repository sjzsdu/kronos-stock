"""
静态资源压缩和优化服务
用于压缩CSS、JS文件，优化图片资源，提升加载性能
"""
import os
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app, request, make_response, send_file
from werkzeug.utils import secure_filename
import mimetypes
import json

from app.config.cache_config import ComponentCacheManager


class StaticResourceCompressor:
    """静态资源压缩器"""
    
    def __init__(self):
        self.compression_cache = {}
        self.file_hashes = {}
        self.compression_stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_ratio': 0.0
        }
        
        # 可压缩的文件类型
        self.compressible_types = {
            '.css', '.js', '.html', '.json', '.xml', '.svg', '.txt'
        }
        
        # 压缩配置
        self.gzip_compression_level = 6
        self.enable_brotli = False  # Brotli压缩（需要额外库支持）
        
    def should_compress(self, filename: str) -> bool:
        """判断文件是否应该压缩"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.compressible_types
    
    def get_file_hash(self, filepath: str) -> str:
        """获取文件哈希值"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ''
    
    def compress_file(self, filepath: str, output_dir: Optional[str] = None) -> Tuple[str, Dict]:
        """压缩单个文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 检查是否需要压缩
        if not self.should_compress(filepath):
            return filepath, {'compressed': False, 'reason': '文件类型不支持压缩'}
        
        # 获取文件信息
        original_size = os.path.getsize(filepath)
        file_hash = self.get_file_hash(filepath)
        
        # 检查缓存
        cache_key = f"{filepath}:{file_hash}"
        if cache_key in self.compression_cache:
            cached_info = self.compression_cache[cache_key]
            if os.path.exists(cached_info['compressed_path']):
                return cached_info['compressed_path'], cached_info['stats']
        
        # 确定输出路径
        if output_dir is None:
            output_dir = os.path.dirname(filepath)
        
        filename = os.path.basename(filepath)
        compressed_filename = f"{filename}.gz"
        compressed_path = os.path.join(output_dir, compressed_filename)
        
        try:
            # 执行Gzip压缩
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=self.gzip_compression_level) as f_out:
                    f_out.write(f_in.read())
            
            compressed_size = os.path.getsize(compressed_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            # 记录统计信息
            stats = {
                'compressed': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compression_type': 'gzip'
            }
            
            # 更新缓存
            self.compression_cache[cache_key] = {
                'compressed_path': compressed_path,
                'stats': stats,
                'timestamp': datetime.utcnow()
            }
            
            # 更新全局统计
            self.compression_stats['total_compressed'] += 1
            self.compression_stats['total_original_size'] += original_size
            self.compression_stats['total_compressed_size'] += compressed_size
            
            if self.compression_stats['total_original_size'] > 0:
                self.compression_stats['compression_ratio'] = (
                    1 - self.compression_stats['total_compressed_size'] / 
                    self.compression_stats['total_original_size']
                ) * 100
            
            current_app.logger.info(
                f"文件压缩完成: {filepath} -> {compressed_path} "
                f"(压缩率: {compression_ratio:.1f}%)"
            )
            
            return compressed_path, stats
            
        except Exception as e:
            current_app.logger.error(f"文件压缩失败: {filepath} - {e}")
            return filepath, {'compressed': False, 'error': str(e)}
    
    def compress_directory(self, directory: str, recursive: bool = True) -> Dict:
        """压缩目录下的所有文件"""
        results = {
            'total_files': 0,
            'compressed_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'files': []
        }
        
        try:
            for root, dirs, files in os.walk(directory):
                # 如果不递归，只处理根目录
                if not recursive and root != directory:
                    continue
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    results['total_files'] += 1
                    
                    try:
                        compressed_path, stats = self.compress_file(filepath)
                        
                        if stats.get('compressed', False):
                            results['compressed_files'] += 1
                            results['total_original_size'] += stats['original_size']
                            results['total_compressed_size'] += stats['compressed_size']
                        else:
                            results['skipped_files'] += 1
                        
                        results['files'].append({
                            'original_path': filepath,
                            'compressed_path': compressed_path,
                            'stats': stats
                        })
                        
                    except Exception as e:
                        results['error_files'] += 1
                        results['files'].append({
                            'original_path': filepath,
                            'error': str(e)
                        })
            
            # 计算总体压缩率
            if results['total_original_size'] > 0:
                results['overall_compression_ratio'] = (
                    1 - results['total_compressed_size'] / results['total_original_size']
                ) * 100
            else:
                results['overall_compression_ratio'] = 0.0
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"目录压缩失败: {directory} - {e}")
            results['error'] = str(e)
            return results
    
    def get_compression_stats(self) -> Dict:
        """获取压缩统计信息"""
        return self.compression_stats.copy()
    
    def clear_compression_cache(self):
        """清空压缩缓存"""
        # 删除压缩文件
        for cache_info in self.compression_cache.values():
            try:
                compressed_path = cache_info['compressed_path']
                if os.path.exists(compressed_path):
                    os.remove(compressed_path)
            except Exception as e:
                current_app.logger.error(f"删除压缩文件失败: {e}")
        
        # 清空缓存
        self.compression_cache.clear()
        self.file_hashes.clear()
        
        # 重置统计
        self.compression_stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_ratio': 0.0
        }


class AssetOptimizer:
    """资源优化器"""
    
    def __init__(self, cache_manager: ComponentCacheManager):
        self.cache_manager = cache_manager
        self.compressor = StaticResourceCompressor()
        
        # 资源版本管理
        self.asset_versions = {}
        self.version_file = 'static/asset_versions.json'
        
        # 加载现有版本信息
        self.load_asset_versions()
    
    def load_asset_versions(self):
        """加载资源版本信息"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    self.asset_versions = json.load(f)
        except Exception as e:
            current_app.logger.warning(f"加载资源版本信息失败: {e}")
            self.asset_versions = {}
    
    def save_asset_versions(self):
        """保存资源版本信息"""
        try:
            os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self.asset_versions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            current_app.logger.error(f"保存资源版本信息失败: {e}")
    
    def get_asset_version(self, asset_path: str) -> str:
        """获取资源版本号"""
        if not os.path.exists(asset_path):
            return '1.0.0'
        
        # 使用文件修改时间生成版本号
        mtime = os.path.getmtime(asset_path)
        version = str(int(mtime))
        
        # 更新版本信息
        self.asset_versions[asset_path] = {
            'version': version,
            'timestamp': datetime.fromtimestamp(mtime).isoformat()
        }
        
        return version
    
    def get_versioned_url(self, asset_path: str) -> str:
        """获取带版本号的资源URL"""
        version = self.get_asset_version(asset_path)
        
        # 添加版本参数
        separator = '&' if '?' in asset_path else '?'
        return f"{asset_path}{separator}v={version}"
    
    def optimize_static_resources(self, static_dir: str = 'app/static') -> Dict:
        """优化静态资源"""
        optimization_results = {
            'compression': {},
            'versioning': {},
            'cache_headers': {},
            'total_optimization_time': 0
        }
        
        start_time = datetime.utcnow()
        
        try:
            # 1. 压缩静态文件
            current_app.logger.info("开始压缩静态资源...")
            compression_results = self.compressor.compress_directory(static_dir)
            optimization_results['compression'] = compression_results
            
            # 2. 更新资源版本
            current_app.logger.info("更新资源版本信息...")
            for file_info in compression_results.get('files', []):
                original_path = file_info.get('original_path')
                if original_path and os.path.exists(original_path):
                    self.get_asset_version(original_path)
            
            self.save_asset_versions()
            optimization_results['versioning'] = {
                'total_assets': len(self.asset_versions),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # 3. 设置缓存策略（通过中间件实现）
            optimization_results['cache_headers'] = {
                'static_cache_ttl': 86400,  # 24小时
                'versioned_cache_ttl': 31536000,  # 1年
                'compression_enabled': True
            }
            
            # 计算总优化时间
            optimization_results['total_optimization_time'] = (
                datetime.utcnow() - start_time
            ).total_seconds()
            
            current_app.logger.info(
                f"静态资源优化完成，耗时: {optimization_results['total_optimization_time']:.2f}秒"
            )
            
            return optimization_results
            
        except Exception as e:
            current_app.logger.error(f"静态资源优化失败: {e}")
            optimization_results['error'] = str(e)
            return optimization_results
    
    def serve_optimized_static(self, filename: str):
        """提供优化后的静态资源"""
        try:
            # 获取文件路径
            static_dir = current_app.static_folder
            filepath = os.path.join(static_dir, filename)
            
            if not os.path.exists(filepath):
                return None, 404
            
            # 检查是否有压缩版本
            compressed_path = f"{filepath}.gz"
            
            # 判断客户端是否支持gzip
            accept_encoding = request.headers.get('Accept-Encoding', '')
            supports_gzip = 'gzip' in accept_encoding.lower()
            
            # 选择合适的文件
            if supports_gzip and os.path.exists(compressed_path):
                response_file = compressed_path
                content_encoding = 'gzip'
            else:
                response_file = filepath
                content_encoding = None
            
            # 创建响应
            response = make_response(send_file(response_file))
            
            # 设置内容编码
            if content_encoding:
                response.headers['Content-Encoding'] = content_encoding
            
            # 设置缓存头
            if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
                # 静态资源缓存1天
                response.headers['Cache-Control'] = 'public, max-age=86400'
                
                # 如果URL包含版本参数，设置长期缓存
                if 'v=' in request.args.get('v', ''):
                    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            
            # 设置MIME类型
            mimetype = mimetypes.guess_type(filename)[0]
            if mimetype:
                response.headers['Content-Type'] = mimetype
            
            return response, 200
            
        except Exception as e:
            current_app.logger.error(f"提供优化静态资源失败: {filename} - {e}")
            return None, 500


# 全局资源优化器
asset_optimizer = None


def init_asset_optimization(app, cache_manager: ComponentCacheManager):
    """初始化资源优化功能"""
    global asset_optimizer
    
    asset_optimizer = AssetOptimizer(cache_manager)
    
    # 注册静态资源优化路由
    @app.route('/api/performance/optimize-assets', methods=['POST'])
    def optimize_assets():
        """执行资源优化"""
        try:
            results = asset_optimizer.optimize_static_resources()
            return results
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/performance/compression-stats')
    def compression_stats():
        """获取压缩统计信息"""
        try:
            return asset_optimizer.compressor.get_compression_stats()
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/performance/clear-compression-cache', methods=['POST'])
    def clear_compression_cache():
        """清空压缩缓存"""
        try:
            asset_optimizer.compressor.clear_compression_cache()
            return {'message': '压缩缓存已清空'}
        except Exception as e:
            return {'error': str(e)}, 500
    
    # 替换默认静态文件处理
    @app.route('/static/<path:filename>')
    def optimized_static(filename):
        """优化的静态文件服务"""
        response, status = asset_optimizer.serve_optimized_static(filename)
        if response:
            return response
        else:
            return app.send_static_file(filename)
    
    current_app.logger.info("资源优化功能已初始化")


def get_asset_optimizer():
    """获取资源优化器实例"""
    return asset_optimizer