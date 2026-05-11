{{/*
Renders the container image reference for a service.

Resolution order (most specific wins):
  1. .<service>.image.repository / .<service>.image.tag (per-service override)
  2. .Values.images.repository / .Values.images.tag
  3. .Chart.AppVersion (tag fallback only)

Usage:
  image: {{ include "onlineboutique.image" (list . .Values.checkoutService) }}
*/}}
{{- define "onlineboutique.image" -}}
{{- $root := index . 0 -}}
{{- $svc := index . 1 -}}
{{- $repo := $root.Values.images.repository -}}
{{- $tag := default $root.Chart.AppVersion $root.Values.images.tag -}}
{{- if $svc.image -}}
{{- $repo = default $repo $svc.image.repository -}}
{{- $tag = default $tag $svc.image.tag -}}
{{- end -}}
{{- printf "%s/%s:%s" $repo $svc.name $tag -}}
{{- end -}}
