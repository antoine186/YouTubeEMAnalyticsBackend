
#!/bin/bash
cd /home/ubuntu/YouTubeEMAnalyticsBackend

python3 -m venv venv
source venv/bin/activate

#sudo pip3 install ../GNews
sudo pip3 install gunicorn

sudo pip3 install -r requirements.txt
