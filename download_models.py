#!/usr/bin/env python3
"""
Download Kronos models for csweb application
"""

from huggingface_hub import snapshot_download
import os
import sys

# Model configurations
MODELS = {
    'kronos-mini': 'NeoQuasar/Kronos-mini',
    'kronos-small': 'NeoQuasar/Kronos-small', 
    'kronos-base': 'NeoQuasar/Kronos-base'
}

def main():
    """Download all models if they don't exist"""
    downloaded_count = 0
    
    for local_name, repo_id in MODELS.items():
        if not os.path.exists(local_name):
            print(f'Downloading {local_name} from {repo_id}...')
            try:
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=local_name,
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
                print(f'✅ Downloaded {local_name} successfully')
                downloaded_count += 1
            except Exception as e:
                print(f'❌ Failed to download {local_name}: {e}')
        else:
            print(f'✅ {local_name} already exists, skipping')
    
    # Verify at least one model exists
    existing_models = [name for name in MODELS.keys() if os.path.exists(name)]
    if not existing_models:
        print('❌ ERROR: No models were downloaded or found')
        sys.exit(1)
    
    print(f'✅ Setup complete. Available models: {existing_models}')

if __name__ == '__main__':
    main()