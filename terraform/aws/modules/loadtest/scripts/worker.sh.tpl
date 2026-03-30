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

# Create systemd service for locust worker
cat > /etc/systemd/system/locust-worker.service << EOF
[Unit]
Description=Locust Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/locust
ExecStart=/usr/local/bin/locust \
  --worker \
  --master-host=${master_private_ip} \
  --master-port=5557 \
  --host=${target_host} \
  -f /opt/locust/locustfile.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable locust-worker
systemctl start locust-worker
