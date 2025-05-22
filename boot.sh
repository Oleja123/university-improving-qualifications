#!/bin/bash
flask db upgrade
exec gunicorn -b :5000 university:app