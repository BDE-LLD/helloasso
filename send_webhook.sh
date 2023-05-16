#! /bin/bash

URL="your-webhook-url"

WORK_PATH="/your/path"

COUNT=$($WORK_PATH/helloasso.py total)


if (($COUNT > $(wc -l $WORK_PATH/sells.txt | awk '{print $1}')))
then
	$WORK_PATH/helloasso.py list > $WORK_PATH/sells.txt
	curl \
		-H "Content-Type: application/json" \
		--data @<(cat <<EOF
	{
		"content": "tickets vendus: $COUNT\n$(head -n 1 $WORK_PATH/sells.txt)"
	}
EOF
) \
		$URL
else
	echo "no sells"
fi
