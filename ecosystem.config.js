module.exports = {
  apps: [
    {
      name: 'shopwriter-frontend',
      cwd: '/root/shopwriter/frontend',
      script: 'npm',
      args: 'start',
      env: {
        PORT: 3008,
        NODE_ENV: 'production',
        BACKEND_URL: 'http://localhost:8008',
      },
    },
    {
      name: 'shopwriter-backend',
      cwd: '/root/shopwriter/backend',
      script: '.venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8008',
      env: {
        PYTHONPATH: '/root/shopwriter/backend',
      },
    },
    {
      name: 'shopwriter-bot',
      cwd: '/root/shopwriter/bot',
      script: '.venv/bin/python',
      args: 'bot.py',
    },
  ],
}
