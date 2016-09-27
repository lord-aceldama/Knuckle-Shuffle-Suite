git filter-branch -f --env-filter '
    GIT_COMMITTER_EMAIL="aceldama.v1.0@gmail.com"
    GIT_COMMITTER_NAME="Lord AceldmaA"
    GIT_AUTHOR_EMAIL="aceldama.v1.0@gmail.com"
    GIT_AUTHOR_NAME="Lord AceldmaA"

    export GIT_COMMITTER_EMAIL
    export GIT_COMMITTER_NAME
    export GIT_AUTHOR_EMAIL
    export GIT_AUTHOR_NAME
' -- --all

#-- And when we're done, forge an update on the git repo
git push --force -u origin master
