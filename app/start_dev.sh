#!/bin/bash

/wait
exec uvicorn app.main:app --host=0.0.0.0 --reload