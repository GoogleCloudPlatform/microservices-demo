#!/bin/bash
set -euo pipefail

yum update -y
yum install -y python3 python3-pip

pip3 install locust faker

# Write locustfile
mkdir -p /opt/locust
cat > /opt/locust/locustfile.py << 'LOCUSTFILE_EOF'
${locustfile_content}
LOCUSTFILE_EOF

# Create systemd service for locust master
cat > /etc/systemd/system/locust-master.service << EOF
[Unit]
Description=Locust Master
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/locust
ExecStart=/usr/local/bin/locust \
  --master \
  --expect-workers=${worker_count} \
  --host=${target_host} \
  --web-port=8089 \
  -f /opt/locust/locustfile.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable locust-master
systemctl start locust-master
