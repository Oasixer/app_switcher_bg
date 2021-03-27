#!/bin/bash

set -e

LEFT_MON_WIDTH=1920

generate_post_data () {
    echo "$OUTPUT"
    # 1id         2idk 3left 4top 5width    6height 7classname         8 idk  9 nvim
    # 0x04200003  0     733  384    953     199  termite.Termite       debian nvim
    ids=
    lefts=
    widths=
    heights=
    classnames=
    windowtitles=
    readarray -t ids < <(echo "$OUTPUT" | awk '{print $1}')
    readarray -t lefts < <(echo "$OUTPUT" | awk '{print $3}')
    readarray -t widths < <(echo "$OUTPUT" | awk '{print $5}')
    readarray -t heights < <(echo "$OUTPUT" | awk '{print $6}')
    readarray -t classnames < <(echo "$OUTPUT" | awk '{print $7}')
    readarray -t windowtitles < <(echo "$OUTPUT" | awk '{print $9}')

    LENGTH="${#ids[@]}"

    JSON="{\"active_id\": \"$NEW_ACTIVE\", \"windows\": ["

    for i in "${!ids[@]}"; do 
        MONITOR=0
        LEFT="${lefts[i]}"
        ID="${ids[i]}"
        WIDTH="${widths[i]}"
        HEIGHT="${heights[i]}"
        CLASS_NAME="${classnames[i]}"
        # echo $CLASS_NAME
        WINDOW_TITLE="${windowtitles[i]}"
        if [ "$LEFT" -gt "$LEFT_MON_WIDTH" ]; then
            MONITOR=1
        fi
        WINDOW_JSON="{\"id\": \"$ID\", \"monitor\": $MONITOR, \"width\": $WIDTH, \"height\": $HEIGHT, \"class_name\": \"$CLASS_NAME\", \"window_title\": \"$WINDOW_TITLE\"}"
        # echo $WINDOW_JSON
        if [ "$i" -lt "$(expr $LENGTH - 1)" ]; then
            JSON="${JSON} ${WINDOW_JSON},"
        else
            JSON="${JSON} ${WINDOW_JSON}]}"
        fi
    done
    echo ""
    echo "$JSON"
}

ACTIVE_CMD='xprop -root -f _NET_ACTIVE_WINDOW 0x " \$0\\n" _NET_ACTIVE_WINDOW | awk "{print \$2}"'

update_active_window_id () {
    NEW_ACTIVE=`eval $ACTIVE_CMD`
    NEW_ACTIVE="${NEW_ACTIVE:0:2}0${NEW_ACTIVE:2}"
}

send_curl () {
    curl -i \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X PATCH --data "$JSON" "http://localhost:8888/update"
}


update_active_window_id
CMD="wmctrl -xGl"
OUTPUT=`eval $CMD`

generate_post_data
send_curl

while :; do
    NEW_OUTPUT=`eval $CMD`
    update_active_window_id
    if [ "$NEW_OUTPUT" != "$OUTPUT" ] || [ "$NEW_ACTIVE" != "$ACTIVE" ]; then
        if [[ "$NEW_OUTPUT" == *"app_switcher12345"* ]]; then
            echo "pysimplegui found"
        else
            echo "pysimplegui not found"
            OUTPUT=$NEW_OUTPUT
            ACTIVE=$NEW_ACTIVE
            generate_post_data
            send_curl
        fi
    fi
    sleep 0.1
done
