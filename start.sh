#!/bin/bash

exec uvicorn app.main:api --host=0.0.0.0 &
exec python -m app.worker