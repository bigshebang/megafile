#!/usr/bin/env bash

pass=password
temp_file=.temp
final_file=commands
command_flags="write readonly denyoom admin pubsub noscript random sort_for_script loading stale skip_monitor asking fast movablekeys"
$(echo 'command' | redis-cli -a $pass > "$temp_file")
grep -vP '\d' "$temp_file" > "${temp_file}.1"
mv "${temp_file}.1" "$temp_file"

for flag in $command_flags; do
	#reverse grep the $flag out of the file
	grep -vP "^$flag$" "$temp_file" > "${temp_file}.1"
	mv "${temp_file}.1" "$temp_file"
done

overlaps="readonly pubsub"
for overlap in $overlaps; do
	echo "$overlap" >> "$temp_file"
done

untouchables="auth shutdown subscribe publish"
for command in $untouchables; do
	grep -vP "^$command$" "$temp_file" > "${temp_file}.1"
	mv "${temp_file}.1" "$temp_file"
done

sort "$temp_file" > "$final_file"

