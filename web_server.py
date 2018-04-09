#!/usr/bin/env python
import os
import sys
import seeburg_manager

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seeburg_django.settings")

    from django.core.management import execute_from_command_line

    args = seeburg_manager.parse_args()
    seeburg_manager.startup(args)

    execute_from_command_line([sys.executable, "runserver", "0.0.0.0:80", "--noreload"])
