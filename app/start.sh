#!/bin/bash

sleep 10
exec uvicorn app.main:api --host=0.0.0.0 --workers 2