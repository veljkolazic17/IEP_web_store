#!/usr/bin/env sh
# echo STARTED ENTRY admin
# if [ "$APPLICATION" = "authentication" ]; then
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
python app.py