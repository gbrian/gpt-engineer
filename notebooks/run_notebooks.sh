JUPYTER_CONFIG_DIR=$(dirname "$0")


cat > ~/.jupyter/lab/user-settings/overrides.json<< EOF
{
  "@jupyterlab/apputils-extension:themes": {
    "theme": "JupyterLab Dark"
  }
}
EOF

jupyter lab --allow-root --no-browser \
  --notebook-dir=/shared \
  --IdentityProvider.token="" \
  --ServerApp.base_url="/notebooks" \
  --ServerApp.allow_remote_access=true