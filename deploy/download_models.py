#!/usr/bin/env python3
"""
Download Kronos models for csweb application
"""

from huggingface_hub import snapshot_download
import os
import sys
import argparse

# Model configurations
MODELS = {
    'kronos-mini': 'NeoQuasar/Kronos-mini',
    'kronos-small': 'NeoQuasar/Kronos-small', 
    'kronos-base': 'NeoQuasar/Kronos-base'
}

def download_models(models_dir="./models", force=False):
    """Download models to specified directory"""
    os.makedirs(models_dir, exist_ok=True)
    downloaded_count = 0
    
    for local_name, repo_id in MODELS.items():
        model_path = os.path.join(models_dir, local_name)
        
        if not force and os.path.exists(model_path):
            print(f'✅ {local_name} already exists at {model_path}, skipping')
            continue
            
        print(f'📥 Downloading {local_name} from {repo_id} to {model_path}...')
        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=model_path,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            print(f'✅ Downloaded {local_name} successfully')
            downloaded_count += 1
        except Exception as e:
            print(f'❌ Failed to download {local_name}: {e}')
    
    # Verify at least one model exists
    existing_models = [name for name in MODELS.keys() 
                      if os.path.exists(os.path.join(models_dir, name))]
    
    if not existing_models:
        print('❌ ERROR: No models were downloaded or found')
        sys.exit(1)
    
    print(f'✅ Setup complete. Available models: {existing_models}')
    return existing_models

def main():
    parser = argparse.ArgumentParser(description='Download Kronos models')
    parser.add_argument('--models-dir', default='./models', 
                       help='Directory to store models (default: ./models)')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if models exist')
    
    args = parser.parse_args()
    
    download_models(args.models_dir, args.force)

if __name__ == '__main__':
    main()