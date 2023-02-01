#!/bin/bash

exec uvicorn app.main:api --host=0.0.0.0 --workers 2 &
exec python -m app.worker