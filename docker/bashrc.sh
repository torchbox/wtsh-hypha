# Note: This file is loaded on all environments, even production.

alias dj="python -m django"

if [ -n "$DEVCONTAINER" ]
then
    alias djrun="python -m django runserver 0.0.0.0:9001"
    alias honcho="honcho -f docker/Procfile"
fi
