#!/bin/bash

/wait
exec uvicorn app.main:api --host=0.0.0.0 --workers 2 --reload