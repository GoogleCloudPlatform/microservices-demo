
# Dynatrace's Microservices Demo Fork 🍴 
  
## Changes from upstream

### Note to collaborators: please update as you change stuff

<table>
<tr>
    <th>Change</th>
    <th>location</th>
    <th>Description</th>
</tr>
<tr>
    <td>Kubernetes Manifests</td>
    <td>dynatrace/manifests</td>
    <td>
        <ul>
            <li>Copied from forked /kubernetes-manifests</li>
            <li>Requests values are lower to fit things into small clusters</li>
            <li>MAX_LEAK added to cart service to control fibonacci leak</li>
            <li>Added checkoutservice2.yaml to show versioning features</li>
        </ul>
    </td>
</tr>
<tr>
    <td>Github workflows</td>
    <td>.github/workflows</td>
    <td>
        <ul>
            <li>Moved forked workflows to .github/upstream_flows_forked</li>
            <li>Added image-builder.yaml to build new container images on git push</li>
        </ul>
    </td>
</tr>
<tr>
    <td>Fibonacci CPU leak</td>
    <td>src/checkoutservice/main.go</td>
    <td>
        <ul>
            <li>There is a fibonacci leak in the checkout service</li>
            <li>It is controlled by the MAX_LEAK environment variable</li>
        </ul>
    </td>
</tr>
<tr>
    <td>Go app Dockerfile changes</td>
    <td>src/(different)/Dockerfile</td>
    <td>
    <ul>
            <li>Removed Skaffold env variables (were building via GH actions)</li>
            <li>Added -ldflags for Dynatrace</li>
    </ul>
    </td>
</tr>
</table>
