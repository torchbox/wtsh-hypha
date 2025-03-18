# Note: This file is loaded on all environments, even production.

alias dj="python -m django"

if [ -n "$DEVCONTAINER" ]
then
    alias djrun="python -m django runserver 0.0.0.0:8000"
    alias djtest="python -m django test --settings=wagtailkit_repo_name.settings.test"
    alias honcho="honcho -f docker/Procfile"
fi
