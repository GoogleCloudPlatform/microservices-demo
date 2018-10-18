# adsservice
FROM grafana/grafana
RUN grafana-cli plugins install mtanda-histogram-panel

COPY provisioning /etc/grafana/provisioning

WORKDIR /
EXPOSE 3000
ENTRYPOINT ["/run.sh"]
