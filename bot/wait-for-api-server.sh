#!/bin/sh
# wait-for-api-server.sh

set -e

host="$1"
shift
cmd="$@"

until curl http://$host/predict; do
  >&2 echo "api_server is unavailable - sleeping"
  sleep 1
done

>&2 echo "api_server is up - executing command"
exec $cmd
