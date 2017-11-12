#!/usr/bin/env bash

command_file=commands
conf_file=temp_conf

commands=$(cat "$command_file")
for command in $commands; do
	echo "rename-command \"$command\" \"\"" >> "$conf_file"
done

echo "rename-command SHUTDOWN f7c7d0ed0e1d9313a8192805bb6a8221539c95270ad90ed017d5110121c3c0371772724678526f7d9a897c22e8043fb197804232c3f0d00917416c20f9e7cead" >> "$conf_file"

