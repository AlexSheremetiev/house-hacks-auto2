name: Daily Build

on:
  # ежедневно в 06:00 по Мск  (UTC-3)
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    # 1. берём код
    - name: Checkout
      uses: actions/checkout@v4

    # 2. ставим Python 3.11
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    # 3. зависимости
    - name: Install dependencies
      run: |
        pip install backoff "openai==0.28.*" feedgen boto3 markdown

    # 4. случайная тема из seeds.txt (или дефолт)
    - name: Generate article
      run: |
        TOPIC=$(shuf -n1 seeds.txt 2>/dev/null || echo "Полезные лайфхаки для дома")
        echo "🔹 Тема статьи: $TOPIC"
        python scripts/generate.py "$TOPIC"
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

    # 5. собираем сайт + RSS
    - name: Build site
      run: python scripts/build_site.py

    # 6. загружаем в Object Storage
    - name: Deploy to Yandex Object Storage
      run: python scripts/deploy.py
      env:
        AWS_ACCESS_KEY_ID:     ${{ secrets.YC_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.YC_SECRET_ACCESS_KEY }}
        BUCKET:                ${{ secrets.BUCKET_NAME }}
        REGION:                ${{ secrets.BUCKET_REGION }}
