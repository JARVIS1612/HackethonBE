#!/usr/bin/env bash
echo "build started"
pip install -r requirements.txt

# Ensure Prisma generates the correct engine binary
prisma generate
prisma py fetch