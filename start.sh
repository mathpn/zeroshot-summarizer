#!/bin/bash

exec python -m app.worker &
exec uvicorn app.main:api --host=0.0.0.0 --workers 2