# when project is built by Cloud Build from a source trigger, the 
# commit SHA will be available as an env var

if [[ "$COMMIT_SHA" && "$SHORT_SHA" ]]; then
    target="<!--GIT_COMMIT_LINK-->"
    replace=" [<a href='https://github.com/GoogleCloudPlatform/microservices-demo/commit/${COMMIT_SHA}'\
             style='font-size:80%'>${SHORT_SHA}</a>]"

    sed -i'' -e "s^$target^$replace^g" src/frontend/templates/footer.html

    # echo 'debug: contents of footer.html:'
    # cat src/frontend/templates/footer.html
fi