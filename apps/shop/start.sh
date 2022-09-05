#!/usr/bin/env sh
# if [ "$APPLICATION" = "admin" ]; then
#     echo STARTED ENTRY admin
#     sleep 5
#     while true; do
#         python migrate.py
#         if [ $? -eq 1 ]; then
#             break
#         fi
#         echo sleeping 5
#         sleep 5
#     done
#     echo FINISHED BOOTSTRAP
# else
#     echo sleeping 15
#     sleep 15
# fi
python migrate.py
python admin.py