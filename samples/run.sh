#!/bin/sh
cycle_count=0
while :
do
	cycle_count=$((cycle_count+1))
	echo "cycle count is "$cycle_count
	now=$(date)
	title="Koineks to Cex "$now
	title=$(echo $title |tr ' ' '_')
	echo $title
	config_path=" config"
	debug_level=" USER_FEEDBACK"
	address="file:///"$PWD/data_to_send/$title".svg"
	echo $address
	param=\"$title\"$config_path$debug_level
	echo $param
	#echo $address
	firefox $address&

	#echo $title
	command="python3.5 cli.py "$param
	echo $command
	eval $command&
	cli_pid=$(ps a|grep "[p]ython3.5 cli.py"|cut -d' ' -f1)
	echo "cli pid is "$cli_pid
	sleep $((2*60*60)) #wait 2 hours 120 point for each table for 60 sec delays
	echo "KIILL ITT"
	kill $cli_pid
	break
done
